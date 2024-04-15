import datetime

from scripts_public import _setup_django
from reserve_download.models import ReserveDownload
from reserve_download.scripts.gen_excel import LargeDataExport
from reserve_download.serializers import ReserveDownloadOrderSerializer, ReserveDownloadOrderFlowSerializer
from order.models import OrderOrder, OrderFlow


class ReserveDownloadOrderInquirerOld:
    """
    查询器
    """

    def __init__(self, start_date, end_date, date_type, fendian_id_list, scan_code_status_id_list,
                 reserve_download_record_id=None, file_name=None, is_test_mode=False):
        """
        @param start_date: 数据开始时间
        @param end_date: 数据结束时间
        @param fendian_id_list: 店铺id列表
        @param scan_code_status_id_list: 扫码状态 id 列表
        @param reserve_download_record_id: 预约下载记录id
        @param is_test_mode: 是否测试模式
        """
        self.start_date = start_date
        self.end_date = end_date
        self.date_type = date_type
        self.fendian_id_list = fendian_id_list
        self.scan_code_status_id_list = scan_code_status_id_list
        self.reserve_download_record_id = reserve_download_record_id
        self.file_name = file_name
        self.is_test_mode = is_test_mode
        self.queryset = None
        # self.flow_queryset = None
        self.data_count = 0
        self.write_data_list = []
        self.serializer_ok = False
        self.serializer_class = None

    def judge_data_type(self):
        """
        判断数据类型
        :return:
        """
        if self.date_type == 'order_date':
            self.serializer_class = ReserveDownloadOrderSerializer
        elif self.date_type == 'scan_date':
            self.serializer_class = ReserveDownloadOrderFlowSerializer
        else:
            print('数据类型未知')
            self.date_type = 'unknown'

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
        if self.date_type == 'order_date':
            order_queryset = OrderOrder.objects.filter(
                day__gte=self.start_date,
                day__lte=self.end_date,
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
        if self.date_type == 'scan_date':
            order_flow_qs = OrderFlow.objects.filter(
                created_time__date__gte=self.start_date,
                created_time__date__lte=self.end_date,
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
        if self.date_type == 'unknown':
            ReserveDownload.objects.filter(
                id=self.reserve_download_record_id
            ).update(task_status=6, task_result='数据类型错误', is_success=False)
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

    def only_check_count(self):
        self.judge_data_type()
        if self.date_type == 'unknown':
            return False, '根据筛选条件判断数据类型错误，无法校验数量'
        self.get_query_set()
        self.get_data_count()
        if self.data_count > 50000:
            return False, f'数据量为{self.data_count}, 超过50000条，禁止导出，请修改筛选条件'
        if self.data_count == 0:
            return False, '数据量为0，请修改筛选条件'
        return True, f'数据量为{self.data_count}'


query_param_example = {
    "date_type": "order_date",
    "start_date": "2024-04-02",
    "end_date": "2024-04-03",
    "fen_dian_id_list": [
        256,
        161
    ],
    "scan_code_status_id_list": [
        [
            0,
            11
        ],
        [
            0,
            34
        ],
        [
            0,
            37
        ],
        [
            0,
            65
        ],
        [
            0,
            66
        ]
    ],
    "task_tag": "343ewfdsgfred",
    "is_history": False,
    "commodity_category_id_list": [
        194,
        197,
        196,
        198,
        195,
        272,
        566,
        565,
        204,
        207,
        206,
        208,
        205
    ],
    "scanner_id_list": [
        1045,
        7163,
        7609,
        7798
    ],
    "live_shift_list": [
        2,
        3,
        4
    ],
    "platform_status_list": [
        "all_return",
        "part_return"
    ],
    "is_Guding_link": False,
    "has_certificate": False,
    "shichangzhuanyuan_id_list": [
        4274,
        139,
        7976
    ],
    "pinjianzhuangtai_list": [
        "eligibility"
    ],
    "is_ship": True,
    "order_situation_list": [
        "deleted_order",
        "presale_order",
        "super_welfare_order",
        "offline_ship"
    ],
    "zhubo_id_list": [
        7565,
        7799,
        7963,
        6705
    ],
    "shipper_id_list": [
        6430,
        2509,
        6402,
        6655
    ]
}


class ReserveDownloadOrderInquirer(object):
    """
    新查询器 2024-04-14
    """

    def __init__(self, reserve_download_record_id, file_name, query_param_dict):
        """
        :param reserve_download_record_id:  预约下载记录id
        :param file_name:            文件名
        :param query_param_dict:    查询参数字典
        """
        self.reserve_download_record_id = reserve_download_record_id
        self.file_name = file_name
        self.query_param_dict = query_param_dict
        self.queryset = None
        self.data_count = 0
        self.write_data_list = []
        self.serializer_ok = False
        self.serializer_class = None

    def update_task_status(self, task_status_num=None, data_count=None, task_result_str=None, is_success=None):
        """
        更新任务状态
        :param task_status_num:     状态阶段
        :param data_count:          数据量
        :param task_result_str:     任务结果
        :param is_success:          是否成功
        :return:
        有哪个参数就更新哪个参数
        """
        update_dict = {}
        if task_status_num:
            update_dict['task_status'] = task_status_num
        if data_count:
            update_dict['data_count'] = data_count
        if task_result_str:
            update_dict['task_result'] = task_result_str
        if is_success:
            update_dict['is_success'] = is_success
        ReserveDownload.objects.filter(
            id=self.reserve_download_record_id
        ).update(
            **update_dict
        )

    def inquire_queryset(self):
        """
        筛选 OrderOrder 查询集
        :return:
        """
        is_history = self.query_param_dict.get('is_history', False)
        date_type = self.query_param_dict.get('date_type', None)
        start_date = self.query_param_dict.get('start_date', None)
        end_date = self.query_param_dict.get('end_date', None)
        fen_dian_id_list = self.query_param_dict.get('fen_dian_id_list', None)
        scan_code_status_id_list = self.query_param_dict.get('scan_code_status_id_list', None)
        commodity_category_id_list = self.query_param_dict.get('commodity_category_id_list', None)
        scanner_id_list = self.query_param_dict.get('scanner_id_list', None)
        live_shift_list = self.query_param_dict.get('live_shift_list', None)
        platform_status_list = self.query_param_dict.get('platform_status_list', None)
        is_Guding_link = self.query_param_dict.get('is_Guding_link', None)
        has_certificate = self.query_param_dict.get('has_certificate', None)
        shichangzhuanyuan_id_list = self.query_param_dict.get('shichangzhuanyuan_id_list', None)
        pinjianzhuangtai_list = self.query_param_dict.get('pinjianzhuangtai_list', None)
        is_ship = self.query_param_dict.get('is_ship')
        order_situation_list = self.query_param_dict.get('order_situation_list', None)
        zhubo_id_list = self.query_param_dict.get('zhubo_id_list', None)
        shipper_id_list = self.query_param_dict.get('shipper_id_list', None)

        if is_history:
            # 导出历史状态，以 order flow 为核心
            self.serializer_class = ReserveDownloadOrderFlowSerializer
            self.queryset = self.get_order_flow_queryset()
        else:
            # 不导出历史状态，以 order order 为核心
            self.serializer_class = ReserveDownloadOrderSerializer
            self.queryset = self.get_order_queryset()

    @staticmethod
    def get_order_queryset(date_type, start_date, end_date, fen_dian_id_list, scan_code_status_id_list, commodity_category_id_list,
                           scanner_id_list, live_shift_list, platform_status_list, is_Guding_link, has_certificate, shichangzhuanyuan_id_list,
                           pinjianzhuangtai_list, is_ship, order_situation_list, zhubo_id_list, shipper_id_list):

        """查询 OrderOrder 查询集 , 不再排除 status=0 的订单，"""
        if date_type == 'order_date':
            order_queryset = OrderOrder.objects.filter(
                day__gte=start_date,
                day__lte=end_date,
                prefix_id__in=fen_dian_id_list,
            )
            # 先判断 需要从 OrderFlow 逆向查询到 OrderOrder 的条件： scanner_id_list 扫码人， scan_code_status_id_list 扫码状态，
            need_reverse_query = False  # 是否需要逆向查询
            order_flow_qs = OrderFlow.objects.filter(
                order__in=order_queryset
            )
            if scan_code_status_id_list:
                # 有扫码状态的情况
                need_reverse_query = True
                order_flow_qs = order_flow_qs.objects.filter(
                    status_id__in=scan_code_status_id_list,
                    order__in=order_queryset
                )
            if scanner_id_list:
                # 有扫码人的情况
                need_reverse_query = True
                order_flow_qs = order_flow_qs.objects.filter(
                    owner__id__in=scanner_id_list,
                    order__in=order_queryset
                )
            if need_reverse_query:
                order_queryset = order_queryset.filter(
                    id__in=order_flow_qs.values_list('order_id', flat=True)
                )

        elif date_type == 'scan_date':
            """若是扫码时间，则用 OrderFlow 查出 OrderOrder """
            order_flow_qs = OrderFlow.objects.filter(
                created_time__date__gte=start_date,
                created_time__date__lte=end_date,
                order__prefix_id__in=fen_dian_id_list,
            )
            if scan_code_status_id_list:
                # 有扫码状态的情况
                order_flow_qs = order_flow_qs.filter(
                    status_id__in=scan_code_status_id_list,
                )
            if scanner_id_list:
                # 有扫码人的情况
                order_flow_qs = order_flow_qs.filter(
                    owner__id__in=scanner_id_list,
                )
            order_queryset = OrderOrder.objects.filter(
                id__in=order_flow_qs.values_list('order_id', flat=True)
            ).distinct('id')
        else:
            order_queryset = OrderOrder.objects.none()

        # 进一步对 order_queryset 进行筛选
        # 商品分类
        if commodity_category_id_list:
            order_queryset = order_queryset.filter(
                category__id__in=commodity_category_id_list
            )
        # 直播班次
        if live_shift_list:
            order_queryset = order_queryset.filter(
                play__classs__classtag__in=live_shift_list
            )
        # 是否固定链接
        if is_Guding_link is not None:
            if is_Guding_link:
                # 是固定链接
                order_queryset = order_queryset.filter(
                    is_guding_url=1
                )
            else:
                # 是闪购链接
                order_queryset = order_queryset.filter(
                    is_guding_url=0
                )
        # 是否有证书
        if has_certificate is not None:
            if has_certificate:
                # 有证书
                order_queryset = order_queryset.filter(
                    is_zhengshu=1
                )
            else:
                # 无证书
                order_queryset = order_queryset.filter(
                    is_zhengshu=0
                )
        # 是否发货
        if is_ship is not None:
            if is_ship:
                # 已发货
                order_queryset = order_queryset.filter(
                    item_status__sendgoodstype=1
                )
            else:
                # 未发货
                order_queryset = order_queryset.exclude(
                    item_status__sendgoodstype=0
                )
        # 平台状态
        if platform_status_list:
            order_queryset = ReserveDownloadOrderInquirer.filter_order_qs_by_platform_status(order_queryset, platform_status_list)
        # 市场专员
        if shichangzhuanyuan_id_list:
            order_queryset = order_queryset.filter(
                play__shichangzhuanyuan__id__in=shichangzhuanyuan_id_list
            )
        # 品检状态
        if pinjianzhuangtai_list:
            order_queryset = ReserveDownloadOrderInquirer.filter_order_qs_by_pinjianzhuangtai(order_queryset, pinjianzhuangtai_list)
        # 主播
        if zhubo_id_list:
            order_queryset = order_queryset.filter(
                zhubo__id__in=zhubo_id_list
            )



    @staticmethod
    def filter_order_qs_by_platform_status(order_queryset, platform_status_list):
        # 平台状态 筛选
        all_return_qs = OrderOrder.objects.none()
        not_return_qs = OrderOrder.objects.none()
        part_return_qs = OrderOrder.objects.none()

        # 全部退货
        if 'all_return' in platform_status_list:
            all_return_qs = order_queryset.filter(
                autostatus='2'
            )
        # 部分退货
        if 'part_return' in platform_status_list:
            part_return_qs = order_queryset.filter(
                autostatus='11'
            )
        # 未退货
        if 'not_return' in platform_status_list:
            exclude_ids = order_queryset.filter(
                autostatus='2'
            ).values_list('id', flat=True)
            not_return_qs = order_queryset.exclude(
                id__in=exclude_ids
            )

        combine_qs = all_return_qs | part_return_qs | not_return_qs
        return combine_qs.distinct('id')

    @staticmethod
    def filter_order_qs_by_pinjianzhuangtai(order_queryset, pinjianzhuangtai_list):
        # eligibility 品检合格 is_checkgoods = 1 ; unqualified 品检不合格 is_checkgoods = 2; unqualified_enter_warehouse 不合格入库 is_checkgoods = 3;
        # no_check 未品检 is_checkgoods = 0
        eligibility_qs = OrderOrder.objects.none()
        unqualified_qs = OrderOrder.objects.none()
        unqualified_enter_warehouse_qs = OrderOrder.objects.none()
        no_check_qs = OrderOrder.objects.none()

        # 品检合格
        if 'eligibility' in pinjianzhuangtai_list:
            eligibility_qs = order_queryset.filter(
                is_checkgoods=1
            )
        # 品检不合格
        if 'unqualified' in pinjianzhuangtai_list:
            unqualified_qs = order_queryset.filter(
                is_checkgoods=2
            )
        # 不合格入库
        if 'unqualified_enter_warehouse' in pinjianzhuangtai_list:
            unqualified_enter_warehouse_qs = order_queryset.filter(
                is_checkgoods=3
            )
        # 未品检
        if 'no_check' in pinjianzhuangtai_list:
            no_check_qs = order_queryset.filter(
                is_checkgoods=0
            )

        combine_qs = eligibility_qs | unqualified_qs | unqualified_enter_warehouse_qs | no_check_qs
        return combine_qs.distinct('id')

    @staticmethod
    def filter_order_qs_by_order_situation(order_queryset, order_situation_list):
        """
        订单情况 筛选 十种情况
        正常订单 normal_order    order_order.status  ！= '0'
        被删订单 deleted_order    order_order.status='0'
        预售订单 presale_order    order_order.status<>'0' and order_order.is_presale=true
        超福订单 super_welfare_order    order_order.status<>'0' and order_order.tradetype=1
        线下发货 offline_ship    order_order.status<>'0' and (order_order.tradetype=0 or  order_order.tradetype isnull) and order_order.amount<=30
        成本结算 cost_settlement    order_order.status<>'0' and order_order.balancetype=2
        扣点结算 kick_settlement    order_order.status<>'0' and (order_order.balancetype<>2 or order_order.balancetype isnull
        特殊订单 special_order    order_order.status<>'0' and order_order.tradetype=2
        需绑货品 need_bind_goods    order_order.status<>'0' and order_order.is_bindgoods=true
        重录订单 re_record_order    order_order.status<>'0' and order_order.is_reorder=1
        """
        normal_order_qs = OrderOrder.objects.none()
        deleted_order_qs = OrderOrder.objects.none()
        presale_order_qs = OrderOrder.objects.none()
        super_welfare_order_qs = OrderOrder.objects.none()
        offline_ship_qs = OrderOrder.objects.none()
        cost_settlement_qs = OrderOrder.objects.none()
        kick_settlement_qs = OrderOrder.objects.none()
        special_order_qs = OrderOrder.objects.none()
        need_bind_goods_qs = OrderOrder.objects.none()
        re_record_order_qs = OrderOrder.objects.none()

        # 正常订单
        if 'normal_order' in order_situation_list:
            normal_order_qs = order_queryset.exclude(
                status='0'
            )
        # 被删订单
        if 'deleted_order' in order_situation_list:
            deleted_order_qs = order_queryset.filter(
                status='0'
            )
        # 预售订单
        if 'presale_order' in order_situation_list:
            presale_order_qs = order_queryset.filter(
                is_presale=True
            ).exclude(
                status='0'
            )
        # 超福订单
        if 'super_welfare_order' in order_situation_list:
            super_welfare_order_qs = order_queryset.filter(
                tradetype=1
            ).exclude(
                status='0'
            )
        # 线下发货
        if 'offline_ship' in order_situation_list:
            offline_ship_qs = order_queryset.filter(
                tradetype=0,
                amount__lte=30
            ).exclude(
                status='0'
            )


    def get_order_flow_queryset(self):
        pass
