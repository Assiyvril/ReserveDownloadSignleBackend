import datetime

from scripts_public import _setup_django
from reserve_download.models import ReserveDownload
from reserve_download.scripts.gen_excel import LargeDataExport
from reserve_download.serializers import ReserveDownloadOrderSerializer, ReserveDownloadOrderFlowSerializer
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
        self.queryset = None
        # self.flow_queryset = None
        self.data_count = 0
        self.write_data_list = []
        self.data_type = ''     # 数据类型, order: 订单数据, flow: 流程数据, 根据筛选条件判断数据类型, unknown: 未知
        self.serializer_ok = False
        self.serializer_class = None

    def judge_data_type(self):
        """
        判断数据类型
        :return:
        """
        if self.data_start_date and self.data_end_date and not self.scan_code_start_date and not self.scan_code_end_date:
            self.data_type = 'order'
            self.serializer_class = ReserveDownloadOrderSerializer
        if self.scan_code_start_date and self.scan_code_end_date and self.scan_code_status_id_list and not self.data_start_date and not self.data_end_date:
            self.data_type = 'flow'
            self.serializer_class = ReserveDownloadOrderFlowSerializer
        else:
            self.data_type = 'unknown'

    def get_query_set(self):
        """
        根据条件，获取 OrderOrder 订单查询集
        @return:
        """
        """
        1，只有下单时间
        2，只有扫码时间 和 扫码状态
        """
        # 1，只有数据时间范围，没有扫码时间范围，也没有扫码状态
        if self.data_type == 'order':
            order_queryset = OrderOrder.objects.filter(
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
            self.queryset = order_queryset

        # 2 只有扫码时间范围，和 扫码状态
        if self.data_type == 'flow':
            order_flow_qs = OrderFlow.objects.filter(
                created_time__date__gte=self.scan_code_start_date,
                created_time__date__lte=self.scan_code_end_date,
                status__in=self.scan_code_status_id_list,
                order__prefix_id__in=self.fendian_id_list,
            ).prefetch_related(
                'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4',
                'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                'order__scan_code_flows'
            )
            self.queryset = order_flow_qs
            # order_id_list = order_flow_qs.values_list('order_id', flat=True)
            # queryset = OrderOrder.objects.filter(
            #     id__in=order_id_list,
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

    def get_data_count(self):
        """
        获取数据数量
        @return:
        """

        self.data_count = self.queryset.count()

    def exec_serializer(self):
        """
        执行序列化
        @return:
        """
        ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=4)
        try:

            data = self.serializer_class(self.queryset, many=True).data
            self.write_data_list = data
            self.serializer_ok = True
        except Exception as e:
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=6, task_result=str(e), is_success=False)
            self.write_data_list = []
            self.serializer_ok = False

    def gen_excel(self):
        """
        生成 excel
        @return:
        """
        if not self.serializer_ok:
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
        # 判断数据类型
        self.judge_data_type()
        if self.data_type == 'unknown':
            ReserveDownload.objects.filter(
                id=self.reserve_download_record_id
            ).update(task_status=6, task_result='根据筛选条件判断数据类型错误', is_success=False)
            return False
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

        self.exec_serializer()
        if not self.serializer_ok:
            return False
        # 生成 excel
        self.gen_excel()
