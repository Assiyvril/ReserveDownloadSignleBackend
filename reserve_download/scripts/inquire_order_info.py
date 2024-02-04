
from scripts_public import _setup_django
from reserve_download.models import ReserveDownload
from reserve_download.scripts.gen_excel import LargeDataExport
from reserve_download.serializers import ReserveDownloadOrderSerializer
from django.db.models import Max
from order.models import OrderOrder, OrderFlow


class ReserveDownloadOrderInquirer:
    """
    查询器
    """

    def __init__(self, data_start_date, data_end_date, fendian_id_list, scan_code_status_id_list, scan_code_start_date,
                 scan_code_end_date, reserve_download_record_id, file_name, is_test_mode=False):
        """
        @param data_start_date: 数据开始时间
        @param data_end_date: 数据结束时间
        @param fendian_id_list: 店铺id列表
        @param scan_code_status_id_list: 扫码状态 id 列表
        @param scan_code_start_date: 扫码开始时间
        @param scan_code_end_date: 扫码结束时间
        @param reserve_download_record_id: 预约下载记录id
        @param is_test_mode: 是否测试模式
        """
        self.data_start_date = data_start_date
        self.data_end_date = data_end_date
        self.fendian_id_list = fendian_id_list
        self.scan_code_status_id_list = scan_code_status_id_list
        self.scan_code_start_date = scan_code_start_date
        self.scan_code_end_date = scan_code_end_date
        self.reserve_download_record_id = reserve_download_record_id
        self.file_name = file_name
        self.is_test_mode = is_test_mode
        self.order_queryset = None
        self.data_count = 0
        self.write_data_list = []

    def get_query_set(self):
        """
        根据条件，获取 OrderOrder 订单查询集
        @return:
        """
        if self.is_test_mode:
            return OrderOrder.objects.all().prefetch_related(
                'prefix',
                'category', 'shipper',
                'zhubo', 'zhuli',
                'item_status',
                'play', 'play__changzhang', 'play__banzhang', 'play__shichangzhuanyuan', 'play__zhuli2',
                'play__zhuli3', 'play__zhuli4', 'play__changkong', 'play__changkong1',
                'play__changkong2', 'play__changkong3', 'play__kefu1', 'play__kefu2',
                'play__kefu3', 'play__kefu4',
                'rel_to_taobao_order', 'rel_to_taobao_order__taobaoorder',
                'scan_code_flows'
            )
        queryset = OrderOrder.objects.none()
        # 只有数据时间范围，没有扫码时间范围
        if self.data_start_date and not self.scan_code_start_date:
            queryset = OrderOrder.objects.filter(
                day__gte=self.data_start_date,
                day__lte=self.data_end_date,
                prefix_id__in=self.fendian_id_list,
            ).exclude(
                status='0',
            ).prefetch_related(
                'prefix',
                'category', 'shipper',
                'zhubo', 'zhuli',
                'item_status',
                'play', 'play__changzhang', 'play__banzhang', 'play__shichangzhuanyuan', 'play__zhuli2',
                'play__zhuli3', 'play__zhuli4', 'play__changkong', 'play__changkong1',
                'play__changkong2', 'play__changkong3', 'play__kefu1', 'play__kefu2',
                'play__kefu3', 'play__kefu4',
                'rel_to_taobao_order', 'rel_to_taobao_order__taobaoorder',
                'scan_code_flows'
            )
        # 只有扫码时间范围，没有数据时间范围
        if self.scan_code_start_date and not self.data_start_date:
            order_flow_qs = OrderFlow.objects.filter(
                created_time__date__gte=self.scan_code_start_date,
                created_time__date__lte=self.scan_code_end_date,
                order__prefix_id__in=self.fendian_id_list,
            )
            order_id_list = order_flow_qs.values_list('order_id', flat=True)
            queryset = OrderOrder.objects.filter(
                id__in=order_id_list,
            ).exclude(
                status='0',
            ).prefetch_related(
                'prefix',
                'category', 'shipper',
                'zhubo', 'zhuli',
                'item_status',
                'play', 'play__changzhang', 'play__banzhang', 'play__shichangzhuanyuan', 'play__zhuli2',
                'play__zhuli3', 'play__zhuli4', 'play__changkong', 'play__changkong1',
                'play__changkong2', 'play__changkong3', 'play__kefu1', 'play__kefu2',
                'play__kefu3', 'play__kefu4',
                'rel_to_taobao_order', 'rel_to_taobao_order__taobaoorder',
                'scan_code_flows'
            ).annotate(newest_scan_time=Max('scan_code_flows__created_time'))
            queryset = queryset.filter(
                newest_scan_time__date__gte=self.scan_code_start_date,
                newest_scan_time__date__lte=self.scan_code_end_date,
            )

            # 方案2
            # print('只有扫码时间范围')
            # queryset = OrderOrder.objects.annotate(newest_scan_time=Max('scan_code_flows__created_time')).filter(
            #     newest_scan_time__date__gte=self.scan_code_start_date,
            #     newest_scan_time__date__lte=self.scan_code_end_date,
            #     prefix_id__in=self.fendian_id_list,
            # ).exclude(
            #     status='0',
            # ).prefetch_related(
            #     'prefix',
            #     'category', 'shipper',
            #     'zhubo', 'zhuli',
            #     'item_status',
            #     'play', 'play__changzhang', 'play__banzhang', 'play__shichangzhuanyuan', 'play__zhuli2',
            #     'play__zhuli3', 'play__zhuli4', 'play__changkong', 'play__changkong1',
            #     'play__changkong2', 'play__changkong3', 'play__kefu1', 'play__kefu2',
            #     'play__kefu3', 'play__kefu4',
            #     'rel_to_taobao_order', 'rel_to_taobao_order__taobaoorder',
            #     'scan_code_flows'
            # )

        # 有数据时间范围，也有扫码时间范围
        if self.data_start_date and self.scan_code_start_date:
            # order_flow_qs = OrderFlow.objects.filter(
            #     created_time__date__gte=self.scan_code_start_date,
            #     created_time__date__lte=self.scan_code_end_date,
            #     order__prefix_id__in=self.fendian_id_list,
            # )
            # order_id_list = order_flow_qs.values_list('order_id', flat=True)
            # print('order_id_list', order_id_list)
            queryset = OrderOrder.objects.filter(
                day__gte=self.data_start_date,
                day__lte=self.data_end_date,
                # id__in=order_id_list,
                prefix_id__in=self.fendian_id_list
            ).exclude(
                status='0',
            ).prefetch_related(
                'prefix',
                'category', 'shipper',
                'zhubo', 'zhuli',
                'item_status',
                'play', 'play__changzhang', 'play__banzhang', 'play__shichangzhuanyuan', 'play__zhuli2',
                'play__zhuli3', 'play__zhuli4', 'play__changkong', 'play__changkong1',
                'play__changkong2', 'play__changkong3', 'play__kefu1', 'play__kefu2',
                'play__kefu3', 'play__kefu4',
                'rel_to_taobao_order', 'rel_to_taobao_order__taobaoorder',
                'scan_code_flows'
            ).annotate(newest_scan_time=Max('scan_code_flows__created_time'))
            queryset = queryset.filter(
                newest_scan_time__date__gte=self.scan_code_start_date,
                newest_scan_time__date__lte=self.scan_code_end_date,
            )
        # 有扫码状态
        if self.scan_code_status_id_list:
            # queryset = queryset.filter(
            #     item_status_id__in=self.scan_code_status_id_list,
            # )
            order_id_list_2 = queryset.values_list('id', flat=True)
            order_flow_qs_2 = OrderFlow.objects.filter(
                order_id__in=order_id_list_2,
                status_id__in=self.scan_code_status_id_list,
            )
            order_id_list_3 = order_flow_qs_2.values_list('order_id', flat=True)
            queryset = queryset.filter(
                id__in=order_id_list_3,
            )
        self.order_queryset = queryset

    def get_data_count(self):
        """
        获取数据数量
        @return:
        """
        self.data_count = self.order_queryset.count()

    def exec_serializer(self):
        """
        执行序列化
        @return:
        """
        ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=4)
        try:

            data = ReserveDownloadOrderSerializer(self.order_queryset, many=True).data
            self.write_data_list = data
            return True
        except Exception as e:
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=6, task_result=str(e), is_success=False)
            self.write_data_list = []
            return False

    def gen_excel(self):
        """
        生成 excel
        @return:
        """
        is_ok = self.exec_serializer()
        if not is_ok:
            return False
        ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=5)
        try:

            LargeDataExport(data_list=self.write_data_list, file_name=self.file_name).save()

            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=7, is_success=True)
            return
        except Exception as e:
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=8, task_result=str(e), is_success=False)

            return

    def exec(self):
        # 获取查询集
        self.get_query_set()
        # 获取数据数量
        self.get_data_count()
        ReserveDownload.objects.filter(
            id=self.reserve_download_record_id
        ).update(
            data_count=self.data_count
        )
        # 检查数据数量
        if self.data_count > 50000:
            ReserveDownload.objects.filter(
                id=self.reserve_download_record_id
            ).update(task_status=6, task_result='数据量超过50000条，禁止导出，请修改筛选条件', is_success=False)
            return False
        if self.data_count == 0:
            ReserveDownload.objects.filter(
                id=self.reserve_download_record_id
            ).update(task_status=6, task_result='数据量为0，请修改筛选条件', is_success=False)
            return False
        # 序列化
        serializer_ok = self.exec_serializer()
        if not serializer_ok:
            return False
        # 生成 excel
        self.gen_excel()
