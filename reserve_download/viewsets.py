import datetime
import random
import time

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from order.models import ItemStatus
from reserve_download.models import ReserveDownload
from reserve_download.scripts.inquire_order_info import ReserveDownloadOrderInquirer
from reserve_download.serializers import ReserveDownloadRecordSerializer, OrderStatusChoiceListSerializer, FenDianChoiceListSerializer
from shop.models import ShopSerialprefix
from user.models import AccountMyuser
from utils.pagination import CustomV3Pagination
from utils.renderer import CustomV3Renderer
from celery_task.reserve_download.task import scheduled_download


class ReserveDownloadViewSet(viewsets.ModelViewSet):
    renderer_classes = [CustomV3Renderer]
    pagination_class = CustomV3Pagination
    queryset = ReserveDownload.objects.all().order_by('-created_time').select_related('creator')
    serializer_class = ReserveDownloadRecordSerializer

    def filter_queryset(self, queryset):
        # 筛选，创建人，tag，is_success, created_data_start, created_data_end
        creator_id = self.request.query_params.get('creator_id', None)
        if not creator_id:
            return ReserveDownload.objects.none()
        if creator_id in ['6623', 6623, 4841, 2136, '4841', '2136']:
            # 静宇，秋娣，敏仪  可以查看所有任务
            queryset = queryset
        else:
            queryset = queryset.filter(creator_id=creator_id)
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tag__contains=tag)
        is_success = self.request.query_params.get('is_success', None)
        # 将字符串转换为布尔值
        if is_success in ['True', 'False', 'true', 'false']:
            is_success = True if is_success in ['True', 'true'] else False
            queryset = queryset.filter(is_success=is_success)
        created_data_start = self.request.query_params.get('created_data_start', None)
        created_data_end = self.request.query_params.get('created_data_end', None)
        if created_data_start and created_data_end:
            queryset = queryset.filter(created_time__date__gte=created_data_start, created_time__date__lte=created_data_end)
        return queryset

    @action(methods=['get'], detail=False)
    def scan_code_status_choice_list(self, request):
        """
        扫码状态
        @param request:
        @return:
        """
        rep_data = {
            'msg': '',
            'result': False,
            'data': [],
        }
        status_qs = ItemStatus.objects.filter(is_active=True)
        rep_data['result'] = True
        rep_data['data'] = OrderStatusChoiceListSerializer(status_qs, many=True).data
        return Response(rep_data)

    @action(methods=['get'], detail=False)
    def fendian_choice_list(self, request):
        """
        店铺选择列表
        @param request:
        @return:
        """
        rep_data = {
            'msg': '',
            'result': False,
            'data': [],
        }
        fendian_qs = ShopSerialprefix.objects.filter(is_active=True)
        rep_data['result'] = True
        rep_data['data'] = FenDianChoiceListSerializer(fendian_qs, many=True).data
        return Response(rep_data)

    def check_create_params(self, request_data):
        """
        校验创建任务参数
        @param request_data: request.data
        @return: is_pass, msg, exec_type
        """
        ret_data = {
            'is_pass': False,
            'msg': '',
            'fendian_info': None,
            'filter_condition': None,
            'creator_obj': None,
            'is_future': False,
            'future_exec_time': None,
        }
        fendian_id_list = request_data.get('fendian_id_list')
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        date_type = request_data.get('date_type')
        creator_id = request_data.get('creator_id')
        scan_code_status = request_data.get('scan_code_status')
        task_tag = request_data.get('task_tag')

        # 校验 task_tag
        if not task_tag:
            ret_data['msg'] = '任务标签不能为空！'
            return ret_data

        # 校验店铺id列表
        if not fendian_id_list:
            ret_data['msg'] = '店铺id列表不能为空！'
            return ret_data
        # 校验创建者
        if not creator_id:
            ret_data['msg'] = '创建者不能为空！'
            return ret_data
        if not AccountMyuser.objects.filter(id=creator_id).exists():
            ret_data['msg'] = '创建者不存在！'
            return ret_data
        ret_data['creator_obj'] = AccountMyuser.objects.get(id=creator_id)
        # 校验日期类型
        if not date_type:
            ret_data['msg'] = '日期类型不能为空！'
            return ret_data
        if date_type not in ['order_date', 'scan_date']:
            ret_data['msg'] = '日期类型错误！'
            return ret_data
        # 若日期类型为 scan_date，必须有扫码状态
        if date_type == 'scan_date' and not scan_code_status:
            ret_data['msg'] = '扫码日期，必须有扫码状态！'
            return ret_data
        """
        校验时间参数
        """
        # 必须有开始和结束时间
        if not start_date or not end_date:
            ret_data['msg'] = '时间范围不完整！'
            return ret_data
        # 开始时间不能大于结束时间
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        if start_date_obj > end_date_obj:
            ret_data['msg'] = '开始时间不能大于结束时间！'
            return ret_data
        # 时间范围不能超过 65 天
        if (end_date_obj - start_date_obj).days > 65:
            ret_data['msg'] = '时间范围不能超过两个月！'
            return ret_data

        """   构建 fendian_info """
        fendian_info = []
        for fendian_id in fendian_id_list:
            try:
                shop_serialprefix_obj = ShopSerialprefix.objects.get(id=fendian_id)
            except ShopSerialprefix.DoesNotExist:
                ret_data['msg'] = f'{fendian_id}店铺id不存在！'
                return ret_data
            fendian_info.append({
                'id': fendian_id,
                'name': shop_serialprefix_obj.name,
            })
        ret_data['fendian_info'] = fendian_info

        """   构建 filter_condition  """
        ret_data['filter_condition'] = {
            'start_date': start_date,
            'end_date': end_date,
            'date_type': date_type,
            'scan_code_status': scan_code_status,
            'date_type_text': '下单日期' if date_type == 'order_date' else '扫码日期',
        }

        """  是否预约定时  """
        now_date_obj = datetime.datetime.now().date()
        if end_date_obj <= now_date_obj:
            # 无需预约定时, 需要校验数据量
            ret_data['is_future'] = False
            inquire = ReserveDownloadOrderInquirer(
                start_date=start_date,
                end_date=end_date,
                date_type=date_type,
                fendian_id_list=fendian_id_list,
                scan_code_status_id_list=scan_code_status,
            )
            count_check_re, msg = inquire.only_check_count()
            if not count_check_re:
                ret_data['is_pass'] = False
                ret_data['msg'] = msg
                return ret_data
        else:
            # 预约定时
            ret_data['is_future'] = True
            ret_data['future_exec_time'] = (end_date_obj + datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:01:00')
        ret_data['is_pass'] = True
        return ret_data

    @action(methods=['post'], detail=False)
    def create_task(self, request):
        rep_data = {
            'msg': '',
            'result': False,
            'data': None,
        }
        post_data = request.data
        check_re = self.check_create_params(post_data)
        if not check_re['is_pass']:
            rep_data['msg'] = check_re['msg']
            return Response(rep_data)
        fendian_id_list = request.data.get('fendian_id_list')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        date_type = request.data.get('date_type')
        scan_code_status = request.data.get('scan_code_status')
        task_tag = request.data.get('task_tag')
        creator_id = request.data.get('creator_id')

        # 创建记录 obj
        file_name = f'{creator_id}_{start_date}_{end_date}_{int(time.time())}_{random.randint(100, 999)}.xlsx'
        record_obj_id = ReserveDownload.objects.create(
            creator=check_re.get('creator_obj'),
            filter_condition=check_re.get('filter_condition'),
            fendian_info=check_re.get('fendian_info'),
            task_status=0,
            file_name=file_name,
            task_celery_id=None,
            tag=task_tag,
            data_count=None,
        ).id

        if check_re['is_future']:
            # 预约定时
            try:
                task_exec_time = check_re.get('future_exec_time')
                task = scheduled_download.apply_async(
                    eta=task_exec_time,
                    args=(start_date, end_date, date_type, fendian_id_list, scan_code_status, record_obj_id, file_name),
                )
                ReserveDownload.objects.filter(id=record_obj_id).update(task_celery_id=task.id, task_status=3)
                rep_data['result'] = True
                rep_data['msg'] = f'任务创建成功, 预约定时 {check_re["future_exec_time"]}'
                rep_data['data'] = self.serializer_class(ReserveDownload.objects.get(id=record_obj_id)).data
            except Exception as e:
                rep_data['msg'] = f'任务创建失败！{e}'
                ReserveDownload.objects.filter(id=record_obj_id).update(task_status=2, task_result=str(e))
        else:
            # 无需预约定时
            try:
                task = scheduled_download.apply_async(
                    args=(start_date, end_date, date_type, fendian_id_list, scan_code_status, record_obj_id, file_name),
                )
                ReserveDownload.objects.filter(id=record_obj_id).update(task_celery_id=task.id, task_status=3)
                rep_data['result'] = True
                rep_data['msg'] = '任务创建成功, 无需预约定时, 立即执行 !'
                rep_data['data'] = self.serializer_class(ReserveDownload.objects.get(id=record_obj_id)).data
            except Exception as e:
                rep_data['msg'] = f'任务创建失败！{e}'
                ReserveDownload.objects.filter(id=record_obj_id).update(task_status=2, task_result=str(e))
        return Response(rep_data)
