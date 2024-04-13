import datetime
import random
import time

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from commodity_category.models import ShopCategory
from order.models import ItemStatus
from reserve_download.models import ReserveDownload
from reserve_download.scripts.inquire_order_info import ReserveDownloadOrderInquirer
from reserve_download.serializers import ReserveDownloadRecordSerializer, OrderScanCodeStatusChoiceListSerializer, FenDianChoiceListSerializer, \
    ZhuboChoiceListSerializer, ShopShipperChoiceListSerializer, UserFirstNameChoiceListSerializer
from shipper.models import ShopShipper
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
        # rep_data['result'] = True
        # rep_data['data'] = OrderScanCodeStatusChoiceListSerializer(status_qs, many=True).data

        # 分组，按照 statustype 分组 0 1 2 3 4
        # 0，未退款
        wei_tui_kuan_qs = status_qs.filter(statustype='0')
        wei_tui_kuan_data = {
            'value': 0,
            'label': '未退款',
            'children': OrderScanCodeStatusChoiceListSerializer(wei_tui_kuan_qs, many=True).data,
        }
        rep_data['data'].append(wei_tui_kuan_data)
        # 1, 跑单退款
        pao_dan_tui_kuan_qs = status_qs.filter(statustype='1')
        pao_dan_tui_kuan_data = {
            'value': 1,
            'label': '跑单退款',
            'children': OrderScanCodeStatusChoiceListSerializer(pao_dan_tui_kuan_qs, many=True).data,
        }
        rep_data['data'].append(pao_dan_tui_kuan_data)
        # 2, 售后退款
        shou_hou_tui_kuan_qs = status_qs.filter(statustype='2')
        shou_hou_tui_kuan_data = {
            'value': 2,
            'label': '售后退款',
            'children': OrderScanCodeStatusChoiceListSerializer(shou_hou_tui_kuan_qs, many=True).data,
        }
        rep_data['data'].append(shou_hou_tui_kuan_data)
        # 3, 待减账退款
        dai_jian_zhang_tui_kuan_qs = status_qs.filter(statustype='3')
        dai_jian_zhang_tui_kuan_data = {
            'value': 3,
            'label': '待减账退款',
            'children': OrderScanCodeStatusChoiceListSerializer(dai_jian_zhang_tui_kuan_qs, many=True).data,
        }
        # 4, 可结算状态
        ke_jie_suan_qs = status_qs.filter(statustype='4')
        ke_jie_suan_data = {
            'value': 4,
            'label': '可结算状态',
            'children': OrderScanCodeStatusChoiceListSerializer(ke_jie_suan_qs, many=True).data,
        }
        rep_data['data'].append(ke_jie_suan_data)

        rep_data['result'] = True

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

    @action(methods=['get'], detail=False)
    def commodity_category_choice_list(self, request):
        """
        商品分类选择列表，树状结构
        """
        rep_data = {
            'msg': '',
            'result': True,
            'data': ShopCategory.get_category_tree_data(shop=2),
        }
        return Response(rep_data)

    @action(methods=['POST'], detail=False)
    def get_four_choice_list(self, request):
        """
        获取四个选择列表: 主播 type=3、货主、市场专员 type=17、扫码人员 type=1,2,14,5
        通过店铺id获取
        """
        rep_data = {
            'msg': '',
            'result': False,
            'zhubo_choice_list': [],
            'shipper_choice_list': [],
            'shichangzhuanyuan_choice_list': [],
            'scanner_choice_list': [],
        }

        fendian_id_list = request.data.get('fendian_id_list')
        department_id = request.data.get('department_id', None)

        if not fendian_id_list:
            rep_data['msg'] = '店铺id列表不能为空！'
            return Response(rep_data)
        if not department_id:
            rep_data['msg'] = '部门id不能为空！'
            return Response(rep_data)

        # 所有人员
        all_people_qs = AccountMyuser.objects.filter(
            type__in=['1', '2', '3', '5', '14', '17'],
            prefix__id__in=fendian_id_list,
            is_active=True,
        )
        # 主播
        zhubo_qs = all_people_qs.filter(type='3')
        # 市场专员
        shichangzhuanyuan_qs = all_people_qs.filter(type='17')
        # 扫码人员
        scanner_qs = all_people_qs.filter(type__in=['1', '2', '14', '5'])

        # 货主
        shipper_qs = ShopShipper.objects.filter(is_active=True, department__id=department_id)

        rep_data['zhubo_choice_list'] = ZhuboChoiceListSerializer(zhubo_qs, many=True).data
        rep_data['shipper_choice_list'] = ShopShipperChoiceListSerializer(shipper_qs, many=True).data
        rep_data['shichangzhuanyuan_choice_list'] = UserFirstNameChoiceListSerializer(shichangzhuanyuan_qs, many=True).data
        rep_data['scanner_choice_list'] = UserFirstNameChoiceListSerializer(scanner_qs, many=True).data
        rep_data['result'] = True
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
