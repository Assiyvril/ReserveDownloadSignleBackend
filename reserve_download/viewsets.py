import datetime
import random
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from order.models import OrderOrder, ItemStatus
from reserve_download.models import ReserveDownload
from reserve_download.scripts.gen_excel import LargeDataExport
from reserve_download.scripts.inquire_order_info import ReserveDownloadOrderInquirer
from reserve_download.serializers import ReserveDownloadRecordSerializer, FenDianChoiceListSerializer, OrderStatusChoiceListSerializer, \
    ReserveDownloadOrderSerializer
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
        if creator_id in ['6623', 6623]:
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

    @action(methods=['post'], detail=False)
    def create_task(self, request):
        """
        创建任务
        @param request:
        @return:
        """
        rep_data = {
            'msg': '',
            'result': False,
            'data': None,
        }
        fendian_id_list = request.data.get('fendian_id_list')
        data_start_date = request.data.get('data_start_date')
        data_end_date = request.data.get('data_end_date')
        creator_id = request.data.get('creator_id')
        scan_code_status = request.data.get('scan_code_status')
        scan_code_start_date = request.data.get('scan_code_start_date')
        scan_code_end_date = request.data.get('scan_code_end_date')
        task_tag = request.data.get('task_tag')

        """
        校验 POST 参数  
        """
        if not fendian_id_list:
            rep_data['msg'] = '店铺id列表不能为空！'
            return Response(rep_data)
        # 若有开始时间，必须有结束时间，若有结束时间，必须有开始时间
        if data_start_date and not data_end_date or data_end_date and not data_start_date:
            rep_data['msg'] = '数据时间范围不完整！'
            return Response(rep_data)
        if scan_code_start_date and not scan_code_end_date or scan_code_end_date and not scan_code_start_date:
            rep_data['msg'] = '扫码时间范围不完整！'
            return Response(rep_data)
        # 数据时间范围 和 扫码时间范围，至少有一个
        if not data_start_date and not data_end_date and not scan_code_start_date and not scan_code_end_date:
            rep_data['msg'] = '数据时间范围 和 扫码时间范围，至少有一个！'
            return Response(rep_data)
        # 开始时间不能大于结束时间
        if data_start_date:

            data_start_date_obj = datetime.datetime.strptime(data_start_date, '%Y-%m-%d')
            data_end_date_obj = datetime.datetime.strptime(data_end_date, '%Y-%m-%d')
            if data_start_date_obj > data_end_date_obj:
                rep_data['msg'] = '数据开始时间不能大于结束时间！'
                return Response(rep_data)

            # 时间范围不能超过 65 天
            if (data_end_date_obj - data_start_date_obj).days > 65:
                rep_data['msg'] = '数据时间范围不能超过两个月！'
                return Response(rep_data)
        if scan_code_start_date:
            scan_code_start_date_obj = datetime.datetime.strptime(scan_code_start_date, '%Y-%m-%d')
            scan_code_end_data_obj = datetime.datetime.strptime(scan_code_end_date, '%Y-%m-%d')
            if scan_code_start_date_obj > scan_code_end_data_obj:
                rep_data['msg'] = '扫码开始时间不能大于结束时间！'
                return Response(rep_data)
            # 时间范围不能超过 65 天
            if (scan_code_end_data_obj - scan_code_start_date_obj).days > 65:
                rep_data['msg'] = '扫码时间范围不能超过两个月！'
                return Response(rep_data)

        # 数据时间和扫码时间不能同时存在
        if data_start_date and scan_code_start_date:
            rep_data['msg'] = '数据时间和扫码时间不能同时存在！'
            return Response(rep_data)

        # 扫码时间和扫码状态必须同时存在
        if scan_code_start_date and not scan_code_status:
            rep_data['msg'] = '扫码时间和扫码状态必须同时存在！'
            return Response(rep_data)
        if scan_code_status and not scan_code_start_date:
            rep_data['msg'] = '扫码时间和扫码状态必须同时存在！'
            return Response(rep_data)

        # 校验店铺id列表，生成 fendian_info 字段
        fendian_info = []
        for fendian_id in fendian_id_list:
            try:
                shop_serialprefix_obj = ShopSerialprefix.objects.get(id=fendian_id)
            except ShopSerialprefix.DoesNotExist:
                rep_data['msg'] = f'{fendian_id}店铺id不存在！'
                return Response(rep_data)
            fendian_info.append({
                'id': fendian_id,
                'name': shop_serialprefix_obj.name,
            })

        # 校验创建者
        if not creator_id:
            rep_data['msg'] = '创建者不能为空！'
            return Response(rep_data)
        if not AccountMyuser.objects.filter(id=creator_id).exists():
            rep_data['msg'] = '创建者不存在！'
            return Response(rep_data)
        creator_obj = AccountMyuser.objects.get(id=creator_id)

        # 生成文件名，创建人id + 时间戳 + 时间范围 + 6位随机数 + .xlsx
        file_name_start_date = data_start_date if data_start_date else scan_code_start_date
        file_name_end_date = data_end_date if data_end_date else scan_code_end_date
        file_name = f'{creator_id}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}_{file_name_start_date}_{file_name_end_date}_{random.randint(100000, 999999)}.xlsx'

        """
                计算任务执行时间，取数据日期 和 扫码日期 的最晚日期，作为 “最晚日期”。
                若最晚日期 早于当前日期，则无需预约定时，立即执行，
                若最晚日期 等于或晚于 当前日期，则预约定时， 最晚日期 + 1天 的 00:01:00
        """

        latest_date = None
        if data_end_date:
            latest_date = data_end_date
        if scan_code_end_date:
            if not latest_date:
                latest_date = scan_code_end_date
            else:
                if scan_code_end_date > latest_date:
                    latest_date = scan_code_end_date

        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        if latest_date < now_date:
            """
            无需预约定时，立即执行
            """
            record_obj_id = ReserveDownload.objects.create(
                creator=creator_obj,
                filter_condition={
                    'data_start_date': data_start_date,
                    'data_end_date': data_end_date,
                    'scan_code_status': scan_code_status,
                    'scan_code_start_date': scan_code_start_date,
                    'scan_code_end_date': scan_code_end_date,
                },
                fendian_info=fendian_info,
                task_status=0,
                file_name=file_name,
                task_celery_id=None,
                tag=task_tag,
                data_count=None,
            ).id
            try:
                task = scheduled_download.apply_async(
                    args=(data_start_date, data_end_date, fendian_id_list, scan_code_status, scan_code_start_date,
                          scan_code_end_date, record_obj_id, file_name)
                )
                ReserveDownload.objects.filter(id=record_obj_id).update(task_celery_id=task.id, task_status=3)
                rep_data['result'] = True
                rep_data['msg'] = '任务创建成功, 无需预约定时, 立即执行 !'
                rep_data['data'] = self.serializer_class(ReserveDownload.objects.get(id=record_obj_id)).data
            except Exception as e:
                rep_data['msg'] = f'任务创建失败！{e}'
                ReserveDownload.objects.filter(id=record_obj_id).update(task_status=2, task_result=str(e))

        else:
            """
            预约定时， 最晚日期 + 1天 的 00:01:00
            """
            task_exec_time = (datetime.datetime.strptime(latest_date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d 00:01:00')
            record_obj_id = ReserveDownload.objects.create(
                creator=creator_obj,
                filter_condition={
                    'data_start_date': data_start_date,
                    'data_end_date': data_end_date,
                    'scan_code_status': scan_code_status,
                    'scan_code_start_date': scan_code_start_date,
                    'scan_code_end_date': scan_code_end_date,
                },
                fendian_info=fendian_info,
                task_status=0,
                file_name=file_name,
                task_celery_id=None,
                tag=task_tag,
                data_count=None,
                task_exec_start_time=task_exec_time,
            ).id
            try:
                task = scheduled_download.apply_async(
                        eta=task_exec_time,
                        args=(data_start_date, data_end_date, fendian_id_list, scan_code_status, scan_code_start_date,
                              scan_code_end_date, record_obj_id, file_name)
                    )
                ReserveDownload.objects.filter(id=record_obj_id).update(task_celery_id=task.id, task_status=3)
                rep_data['result'] = True
                rep_data['msg'] = f'任务创建成功, 预约定时 {task_exec_time}'
                rep_data['data'] = self.serializer_class(ReserveDownload.objects.get(id=record_obj_id)).data
            except Exception as e:
                rep_data['msg'] = f'任务创建失败！{e}'
                ReserveDownload.objects.filter(id=record_obj_id).update(task_status=2, task_result=str(e))
        return Response(rep_data)

    @action(methods=['get'], detail=False)
    def status_choice_list(self, request):
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