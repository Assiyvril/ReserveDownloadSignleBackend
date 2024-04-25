import datetime
import time

from scripts_public import _setup_django
from reserve_download.models import ReserveDownload
from reserve_download.scripts.gen_excel import LargeDataExport
from reserve_download.serializers import ReserveDownloadOrderSerializer, ReserveDownloadOrderFlowSerializer
from order.models import OrderOrder, OrderFlow, OrderTaobaoorder, OrderTaobaoorderOrders


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


class ReserveDownloadOrderInquirer:
    """
    新查询器 2024-04-14
    """
    DATA_COUNT_LIMIT = 50000  # 数据量限制, 超过此数量，不予导出

    def __init__(self, query_param_dict, reserve_download_record_id=None, file_name=None):
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

    @staticmethod
    def get_order_queryset(date_type, start_date, end_date, fendian_id_list, scan_code_status_id_list, commodity_category_id_list,
                           scanner_id_list, live_shift_list, platform_status_list, is_Guding_link, has_certificate, shichangzhuanyuan_id_list,
                           pinjianzhuangtai_list, is_ship, order_situation_list, zhubo_id_list, shipper_id_list):

        """查询 OrderOrder 查询集 , 不再排除 status=0 的订单，"""
        if date_type == 'order_date':
            order_queryset = OrderOrder.objects.filter(
                day__gte=start_date,
                day__lte=end_date,
                prefix__id__in=fendian_id_list,
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
            print('下单日期yyy', order_queryset.count())
            # 先判断 需要从 OrderFlow 逆向查询到 OrderOrder 的条件： scanner_id_list 扫码人， scan_code_status_id_list 扫码状态，
            need_reverse_query = False  # 是否需要逆向查询
            order_flow_qs = OrderFlow.objects.filter(
                order__in=order_queryset
            )
            if scan_code_status_id_list:
                print('有扫码状态', scan_code_status_id_list)
                # 有扫码状态的情况
                need_reverse_query = True
                order_flow_qs = order_flow_qs.filter(
                    status__id__in=scan_code_status_id_list,
                    order__in=order_queryset
                ).prefetch_related(
                    'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                    'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                    'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                    'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                    'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4', 'order__play__classs',
                    'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                    'order__scan_code_flows', 'owner', 'status',
                )
            if scanner_id_list:
                # 有扫码人的情况
                print('有扫码人', scanner_id_list)
                need_reverse_query = True
                order_flow_qs = order_flow_qs.filter(
                    owner__id__in=scanner_id_list,
                    order__in=order_queryset
                ).prefetch_related(
                    'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                    'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                    'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                    'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                    'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4', 'order__play__classs',
                    'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                    'order__scan_code_flows', 'owner', 'status',
                )
            if need_reverse_query:
                print('需要逆向')
                order_queryset = order_queryset.filter(
                    id__in=order_flow_qs.values_list('order_id', flat=True)
                )

        elif date_type == 'scan_date':
            """若是扫码时间，则用 OrderFlow 查出 OrderOrder """
            order_flow_qs = OrderFlow.objects.filter(
                created_time__date__gte=start_date,
                created_time__date__lte=end_date,
                order__prefix_id__in=fendian_id_list,
            ).prefetch_related(
                    'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                    'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                    'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                    'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                    'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4', 'order__play__classs',
                    'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                    'order__scan_code_flows', 'owner', 'status',
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
        else:
            order_queryset = OrderOrder.objects.none()

        # 进一步对 order_queryset 进行筛选
        # 商品分类
        if commodity_category_id_list:
            print('商品分类', commodity_category_id_list)
            order_queryset = order_queryset.filter(
                category__id__in=commodity_category_id_list
            )
        # 直播班次
        if live_shift_list:
            print('直播班次', live_shift_list)
            order_queryset = order_queryset.filter(
                play__classs__classtag__in=live_shift_list
            )
        # 是否固定链接
        if is_Guding_link is not None:
            print('是否固定链接', is_Guding_link, type(is_Guding_link))
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
            print('是否有证书', has_certificate, type(has_certificate))
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
            print('是否发货', is_ship, type(is_ship))
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
            print('平台状态', platform_status_list)
            order_queryset = ReserveDownloadOrderInquirer.filter_order_qs_by_platform_status(order_queryset, platform_status_list)
        # 市场专员
        if shichangzhuanyuan_id_list:
            print('市场专员', shichangzhuanyuan_id_list)
            order_queryset = order_queryset.filter(
                play__shichangzhuanyuan__id__in=shichangzhuanyuan_id_list
            )
        # 品检状态
        if pinjianzhuangtai_list:
            print('品检状态', pinjianzhuangtai_list)
            order_queryset = ReserveDownloadOrderInquirer.filter_order_qs_by_pinjianzhuangtai(order_queryset, pinjianzhuangtai_list)
        # 主播
        if zhubo_id_list:
            print('主播', zhubo_id_list)
            order_queryset = order_queryset.filter(
                zhubo__id__in=zhubo_id_list
            )

        # 订单情况
        if order_situation_list:
            print('订单情况', order_situation_list)
            order_queryset = ReserveDownloadOrderInquirer.filter_order_qs_by_order_situation(order_queryset, order_situation_list)

        # 货主
        if shipper_id_list:
            print('货主', shipper_id_list)
            order_queryset = order_queryset.filter(
                shipper__id__in=shipper_id_list
            )

        print('最终数量', order_queryset.count())
        return order_queryset.distinct('id')

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
        return combine_qs

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
        return combine_qs

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

        not_deleted_order_qs = order_queryset.exclude(
            status='0'
        )

        # 正常订单
        if 'normal_order' in order_situation_list:
            normal_order_qs = not_deleted_order_qs
        # 被删订单
        if 'deleted_order' in order_situation_list:
            deleted_order_qs = order_queryset.filter(
                status='0'
            )
        # 预售订单
        if 'presale_order' in order_situation_list:
            presale_order_qs = not_deleted_order_qs.filter(
                is_presale=True
            )
        # 超福订单
        if 'super_welfare_order' in order_situation_list:
            super_welfare_order_qs = not_deleted_order_qs.filter(
                tradetype=1
            )
        # 线下发货
        if 'offline_ship' in order_situation_list:
            offline_ship_qs = not_deleted_order_qs.filter(
                tradetype=0,
                amount__lte=30
            ) | not_deleted_order_qs.filter(
                tradetype__isnull=True,
                amount__lte=30
            )
        # 成本结算
        if 'cost_settlement' in order_situation_list:
            cost_settlement_qs = not_deleted_order_qs.filter(
                balancetype=2
            )
        # 扣点结算
        if 'kick_settlement' in order_situation_list:
            kick_settlement_qs = not_deleted_order_qs.exclude(
                balancetype=2
            ) | not_deleted_order_qs.filter(
                balancetype__isnull=True
            )
        # 特殊订单
        if 'special_order' in order_situation_list:
            special_order_qs = not_deleted_order_qs.filter(
                tradetype=2
            )
        # 需绑货品
        if 'need_bind_goods' in order_situation_list:
            need_bind_goods_qs = not_deleted_order_qs.filter(
                is_bindgoods=True
            )
        # 重录订单
        if 're_record_order' in order_situation_list:
            re_record_order_qs = not_deleted_order_qs.filter(
                is_reorder=1
            )

        combine_qs = (normal_order_qs | deleted_order_qs | presale_order_qs | super_welfare_order_qs | offline_ship_qs | cost_settlement_qs |
                      kick_settlement_qs | special_order_qs | need_bind_goods_qs | re_record_order_qs)
        return combine_qs

    @staticmethod
    def get_order_flow_queryset(date_type, start_date, end_date, fendian_id_list, scan_code_status_id_list, commodity_category_id_list,
                                scanner_id_list, live_shift_list, platform_status_list, is_Guding_link, has_certificate, shichangzhuanyuan_id_list,
                                pinjianzhuangtai_list, is_ship, order_situation_list, zhubo_id_list, shipper_id_list):
        if date_type == 'order_date':
            flow_queryset = OrderFlow.objects.filter(
                order__day__gte=start_date,
                order__day__lte=end_date,
                order__prefix_id__in=fendian_id_list,
            ).prefetch_related(
                'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4', 'order__play__classs',
                'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                'order__scan_code_flows', 'owner', 'status',
            )
        elif date_type == 'scan_date':
            flow_queryset = OrderFlow.objects.filter(
                created_time__date__gte=start_date,
                created_time__date__lte=end_date,
                order__prefix_id__in=fendian_id_list,
            ).prefetch_related(
                'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4',
                'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                'order__scan_code_flows'
            )
        else:
            flow_queryset = OrderFlow.objects.none()

        # 进一步对 flow_queryset 进行筛选
        # scan_code_status_id_list 扫码状态
        if scan_code_status_id_list:
            flow_queryset = flow_queryset.filter(
                status_id__in=scan_code_status_id_list
            )
        # 商品分类 commodity_category_id_list
        if commodity_category_id_list:
            flow_queryset = flow_queryset.filter(
                order__category__id__in=commodity_category_id_list
            )
        # 扫码人 scanner_id_list
        if scanner_id_list:
            flow_queryset = flow_queryset.filter(
                owner__id__in=scanner_id_list
            )
        # 直播班次 live_shift_list
        if live_shift_list:
            flow_queryset = flow_queryset.filter(
                order__play__classs__classtag__in=live_shift_list
            )
        # 是否固定链接 is_Guding_link
        if is_Guding_link is not None:
            if is_Guding_link:
                flow_queryset = flow_queryset.filter(
                    order__is_guding_url=1
                )
            else:
                flow_queryset = flow_queryset.filter(
                    order__is_guding_url=0
                )
        # 是否有证书 has_certificate
        if has_certificate is not None:
            if has_certificate:
                flow_queryset = flow_queryset.filter(
                    order__is_zhengshu=1
                )
            else:
                flow_queryset = flow_queryset.filter(
                    order__is_zhengshu=0
                )
        # 是否发货 is_ship
        if is_ship is not None:
            if is_ship:
                flow_queryset = flow_queryset.filter(
                    order__item_status__sendgoodstype=1
                )
            else:
                flow_queryset = flow_queryset.exclude(
                    order__item_status__sendgoodstype=0
                )
        # 市场专员 shichangzhuanyuan_id_list
        if shichangzhuanyuan_id_list:
            flow_queryset = flow_queryset.filter(
                order__play__shichangzhuanyuan__id__in=shichangzhuanyuan_id_list
            )
        # 主播
        if zhubo_id_list:
            flow_queryset = flow_queryset.filter(
                order__zhubo__id__in=zhubo_id_list
            )
        # 货主
        if shipper_id_list:
            flow_queryset = flow_queryset.filter(
                order__shipper__id__in=shipper_id_list
            )
        # 平台状态 platform_status_list
        if platform_status_list:
            flow_queryset = ReserveDownloadOrderInquirer.filter_flow_qs_by_platform_status(flow_queryset, platform_status_list)
        # 品检状态 pinjianzhuangtai_list
        if pinjianzhuangtai_list:
            flow_queryset = ReserveDownloadOrderInquirer.filter_flow_qs_by_pinjianzhuangtai(flow_queryset, pinjianzhuangtai_list)
        # 订单情况 order_situation_list
        if order_situation_list:
            flow_queryset = ReserveDownloadOrderInquirer.filter_flow_qs_by_order_situation(flow_queryset, order_situation_list)

        return flow_queryset.distinct('id')

    @staticmethod
    def filter_flow_qs_by_platform_status(flow_queryset, platform_status_list):
        all_return_qs = OrderFlow.objects.none()
        not_return_qs = OrderFlow.objects.none()
        part_return_qs = OrderFlow.objects.none()

        # 全部退货
        if 'all_return' in platform_status_list:
            all_return_qs = flow_queryset.filter(
                order__autostatus='2'
            )
        # 部分退货
        if 'part_return' in platform_status_list:
            part_return_qs = flow_queryset.filter(
                order__autostatus='11'
            )
        # 未退货
        if 'not_return' in platform_status_list:
            exclude_ids = flow_queryset.filter(
                order__autostatus='2'
            ).values_list('id', flat=True)
            not_return_qs = flow_queryset.exclude(
                id__in=exclude_ids
            )

        combine_qs = all_return_qs | part_return_qs | not_return_qs
        return combine_qs

    @staticmethod
    def filter_flow_qs_by_pinjianzhuangtai(flow_queryset, pinjianzhuangtai_list):
        eligibility_qs = OrderFlow.objects.none()
        unqualified_qs = OrderFlow.objects.none()
        unqualified_enter_warehouse_qs = OrderFlow.objects.none()
        no_check_qs = OrderFlow.objects.none()

        # 品检合格
        if 'eligibility' in pinjianzhuangtai_list:
            eligibility_qs = flow_queryset.filter(
                order__is_checkgoods=1
            )
        # 品检不合格
        if 'unqualified' in pinjianzhuangtai_list:
            unqualified_qs = flow_queryset.filter(
                order__is_checkgoods=2
            )
        # 不合格入库
        if 'unqualified_enter_warehouse' in pinjianzhuangtai_list:
            unqualified_enter_warehouse_qs = flow_queryset.filter(
                order__is_checkgoods=3
            )
        # 未品检
        if 'no_check' in pinjianzhuangtai_list:
            no_check_qs = flow_queryset.filter(
                order__is_checkgoods=0
            )

        combine_qs = eligibility_qs | unqualified_qs | unqualified_enter_warehouse_qs | no_check_qs
        return combine_qs

    @staticmethod
    def filter_flow_qs_by_order_situation(flow_queryset, order_situation_list):
        normal_order_qs = OrderFlow.objects.none()
        deleted_order_qs = OrderFlow.objects.none()
        presale_order_qs = OrderFlow.objects.none()
        super_welfare_order_qs = OrderFlow.objects.none()
        offline_ship_qs = OrderFlow.objects.none()
        cost_settlement_qs = OrderFlow.objects.none()
        kick_settlement_qs = OrderFlow.objects.none()
        special_order_qs = OrderFlow.objects.none()
        need_bind_goods_qs = OrderFlow.objects.none()
        re_record_order_qs = OrderFlow.objects.none()

        not_deleted_order_qs = flow_queryset.exclude(
            order__status='0'
        )

        # 正常订单
        if 'normal_order' in order_situation_list:
            normal_order_qs = not_deleted_order_qs
        # 被删订单
        if 'deleted_order' in order_situation_list:
            deleted_order_qs = flow_queryset.filter(
                order__status='0'
            )
        # 预售订单
        if 'presale_order' in order_situation_list:
            presale_order_qs = not_deleted_order_qs.filter(
                order__is_presale=True
            )
        # 超福订单
        if 'super_welfare_order' in order_situation_list:
            super_welfare_order_qs = not_deleted_order_qs.filter(
                order__tradetype=1
            )
        # 线下发货
        if 'offline_ship' in order_situation_list:
            offline_ship_qs = not_deleted_order_qs.filter(
                order__tradetype=0,
                order__amount__lte=30
            ) | not_deleted_order_qs.filter(
                order__tradetype__isnull=True,
                order__amount__lte=30
            )
        # 成本结算
        if 'cost_settlement' in order_situation_list:
            cost_settlement_qs = not_deleted_order_qs.filter(
                order__balancetype=2
            )
        # 扣点结算
        if 'kick_settlement' in order_situation_list:
            kick_settlement_qs = not_deleted_order_qs.exclude(
                order__balancetype=2
            ) | not_deleted_order_qs.filter(
                order__balancetype__isnull=True
            )
        # 特殊订单
        if 'special_order' in order_situation_list:
            special_order_qs = not_deleted_order_qs.filter(
                order__tradetype=2
            )
        # 需绑货品
        if 'need_bind_goods' in order_situation_list:
            need_bind_goods_qs = not_deleted_order_qs.filter(
                order__is_bindgoods=True
            )
        # 重录订单
        if 're_record_order' in order_situation_list:
            re_record_order_qs = not_deleted_order_qs.filter(
                order__is_reorder=1
            )

        combine_qs = (normal_order_qs | deleted_order_qs | presale_order_qs | super_welfare_order_qs | offline_ship_qs | cost_settlement_qs |
                      kick_settlement_qs | special_order_qs | need_bind_goods_qs | re_record_order_qs)
        return combine_qs

    def update_task_status(self, task_status_num=None, data_count=None, task_result_str=None, is_success=None, can_download=False):
        """
        更新任务状态
        :param task_status_num:     状态阶段
        :param data_count:          数据量
        :param task_result_str:     任务结果
        :param is_success:          是否成功
        :param can_download:        是否可以下载
        :return:
        有哪个参数就更新哪个参数
        """
        if not self.reserve_download_record_id:
            return
        update_dict = {}
        if task_status_num:
            update_dict['task_status'] = task_status_num
        if data_count:
            update_dict['data_count'] = data_count
        if task_result_str:
            update_dict['task_result'] = task_result_str
        if is_success:
            update_dict['is_success'] = is_success
        if can_download:
            update_dict['can_download'] = True
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
        exec_inquire_start_time = datetime.datetime.now()
        print('开始执行查询，时间：', exec_inquire_start_time.strftime('%Y-%m-%d %H:%M:%S'))
        is_history = self.query_param_dict.get('is_history', False)
        date_type = self.query_param_dict.get('date_type', None)
        start_date = self.query_param_dict.get('start_date', None)
        end_date = self.query_param_dict.get('end_date', None)
        fendian_id_list = self.query_param_dict.get('fendian_id_list', None)
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
            self.queryset = self.get_order_flow_queryset(
                date_type=date_type, start_date=start_date, end_date=end_date, fendian_id_list=fendian_id_list,
                scan_code_status_id_list=scan_code_status_id_list, commodity_category_id_list=commodity_category_id_list,
                scanner_id_list=scanner_id_list, live_shift_list=live_shift_list, platform_status_list=platform_status_list,
                is_Guding_link=is_Guding_link, has_certificate=has_certificate, shichangzhuanyuan_id_list=shichangzhuanyuan_id_list,
                pinjianzhuangtai_list=pinjianzhuangtai_list, is_ship=is_ship, order_situation_list=order_situation_list,
                zhubo_id_list=zhubo_id_list, shipper_id_list=shipper_id_list
            )
        else:
            # 不导出历史状态，以 order order 为核心
            self.serializer_class = ReserveDownloadOrderSerializer
            self.queryset = self.get_order_queryset(
                date_type=date_type, start_date=start_date, end_date=end_date, fendian_id_list=fendian_id_list,
                scan_code_status_id_list=scan_code_status_id_list, commodity_category_id_list=commodity_category_id_list,
                scanner_id_list=scanner_id_list, live_shift_list=live_shift_list, platform_status_list=platform_status_list,
                is_Guding_link=is_Guding_link, has_certificate=has_certificate, shichangzhuanyuan_id_list=shichangzhuanyuan_id_list,
                pinjianzhuangtai_list=pinjianzhuangtai_list, is_ship=is_ship, order_situation_list=order_situation_list,
                zhubo_id_list=zhubo_id_list, shipper_id_list=shipper_id_list
            )
        self.data_count = self.queryset.count()
        exec_inquire_end_time = datetime.datetime.now()
        print('查询结束，时间：', exec_inquire_end_time.strftime('%Y-%m-%d %H:%M:%S'))
        print('查询耗时：', exec_inquire_end_time - exec_inquire_start_time)

    def only_check_count(self):
        """
        只校验数量
        :return:
        """
        self.inquire_queryset()
        if self.data_count > self.DATA_COUNT_LIMIT:
            return False, f'数据量为{self.data_count}, 超过{self.DATA_COUNT_LIMIT}条，禁止导出，请修改筛选条件'
        if self.data_count == 0:
            return False, '数据量为0，请修改筛选条件'
        return True, f'数据量为{self.data_count}'

    def exec_serializer(self):
        """
        执行序列化
        :return:
        """
        self.update_task_status(task_status_num=4)
        try:
            self.write_data_list = self.serializer_class(self.queryset, many=True).data
            self.serializer_ok = True
        except Exception as e:
            self.update_task_status(task_status_num=6, task_result_str=f'序列化异常：{e}', is_success=False)
            self.serializer_ok = False
            self.write_data_list = []

    def gen_excel(self):
        if not self.serializer_ok:
            return False
        self.update_task_status(task_status_num=5)
        # 生成 excel
        try:
            LargeDataExport(data_list=self.write_data_list, file_name=self.file_name).save()
            self.update_task_status(task_status_num=7, is_success=True, can_download=True)
            return
        except Exception as e:
            self.update_task_status(task_status_num=8, task_result_str=f'生成 excel 异常：{e}', is_success=False)
            return

    def exec(self):
        # 1, 查询数据
        self.update_task_status(task_status_num=4)
        self.inquire_queryset()
        # 2， 更新数据量
        self.update_task_status(data_count=self.data_count)
        """ 这里再校验一次数据量， 有两个原因
            1， 此任务可能是预约将来执行的，不能在创建任务之前调用 only_check_count 来校验数据量，只能在执行时校验
            2， 此任务创建时，数据量校验通过； 然后进入队列排队执行；等到执行时，数据量可能已经发生变化
        """
        if self.data_count > self.DATA_COUNT_LIMIT:
            self.update_task_status(task_status_num=6,
                                    task_result_str=f'数据量为{self.data_count}, 超过{self.DATA_COUNT_LIMIT}条，禁止导出，请修改筛选条件',
                                    is_success=False)
            return False
        if self.data_count == 0:
            self.update_task_status(task_status_num=6, task_result_str='数据量为0，请修改筛选条件', is_success=False)
            return False
        # 3， 执行序列化
        self.exec_serializer()
        if not self.serializer_ok:
            return False
        # 4， 生成 excel
        self.gen_excel()


class OrderInquireByCode:
    """
    通过订单码查询订单（从excel中解析到的）
    分为 大G码 和 平台码
    """

    DATA_COUNT_LIMIT = 50000    # 数据量限制

    def __init__(self, parse_order_code_list, available_fendian_id_list, order_code_mode, is_history, reserve_download_record_id=None, file_name=None):
        """
        :param parse_order_code_list:       解析后的订单码列表
        :param available_fendian_id_list:   可用分店列表
        :param order_code_mode:             订单码模式， 大G码 或 平台码
        :param is_history:                  是否查询历史数据
        """
        self.parse_order_code_list = parse_order_code_list
        self.available_fendian_id_list = available_fendian_id_list
        self.order_code_mode = order_code_mode
        self.is_history = is_history
        self.reserve_download_record_id = reserve_download_record_id
        self.file_name = file_name

        self.order_code_list = []           # parse_order_code_list 提取出的订单码列表
        self.no_permission_code_list = []   # 不在权限范围内的订单码列表
        self.queryset = None                # 查询集
        self.data_count = 0                 # 数据量
        self.write_data_list = []           # 写入 excel 的数据列表
        self.serializer_ok = False          # 序列化是否成功
        self.serializer_class = None        # 序列化类

    @staticmethod
    def direct_filter_big_g_qs(code_list, fendian_id_list):
        """
        直接使用大G编号查询 orderorder， 适用于 order_code_mode = big_g
        然后对比出不在权限范围内的 大G编号列表
        :param code_list:
        :param fendian_id_list:
        :return: big_G qs, no_permission_code_list
        """
        big_g_queryset = OrderOrder.objects.filter(
            sn__in=code_list,
            prefix__id__in=fendian_id_list
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
        no_permission_code_list = list(set(code_list) - set(big_g_queryset.values_list('sn', flat=True)))
        return big_g_queryset, no_permission_code_list

    @staticmethod
    def filter_big_g_qs_by_platform_code(code_list, fendian_id_list):
        """
        使用平台码查询 orderorder， 适用于 order_code_mode = platform_code
        :param code_list:
        :param fendian_id_list:
        :return: big_G qs, no_permission_code_list
        """
        platform_order_queryset = OrderTaobaoorder.objects.filter(
            tbno__in=code_list,
            prefix__id__in=fendian_id_list
        )
        # 中介关系表
        rel_qs_id_list = OrderTaobaoorderOrders.objects.filter(
            taobaoorder__in=platform_order_queryset
        ).values_list('order__id', flat=True)
        big_g_queryset = OrderOrder.objects.filter(
            id__in=rel_qs_id_list
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
        no_permission_code_list = list(set(code_list) - set(platform_order_queryset.values_list('tbno', flat=True)))
        return big_g_queryset, no_permission_code_list

    def get_order_code_list(self):
        """
        从 parse_order_code_list 中获取订单码列表
        :return:
        """
        for item in self.parse_order_code_list:
            if item.get('check_success'):
                self.order_code_list.append(item.get('order_code'))

    def inquire_queryset(self):
        """
        根据情况 查询订单
        :return:
        """
        if self.order_code_mode == 'big_G':
            # 使用 order_code_list 直接查出 orderorder
            big_g_qs, no_permission_code_list = self.direct_filter_big_g_qs(
                code_list=self.order_code_list,
                fendian_id_list=self.available_fendian_id_list
            )
            self.no_permission_code_list = no_permission_code_list
        else:
            # 使用 order_code_list 查出平台订单，再反查 order order
            big_g_qs, no_permission_code_list = self.filter_big_g_qs_by_platform_code(
                code_list=self.order_code_list,
                fendian_id_list=self.available_fendian_id_list
            )
            self.no_permission_code_list = no_permission_code_list

        if self.is_history:
            # 使用 big_g_qs 查出 order flow
            self.queryset = OrderFlow.objects.filter(
                order__in=big_g_qs
            ).prefetch_related(
                'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
                'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
                'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
                'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
                'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4', 'order__play__classs',
                'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
                'order__scan_code_flows', 'owner', 'status',
            )
            self.serializer_class = ReserveDownloadOrderFlowSerializer
            self.data_count = self.queryset.count()
        else:
            # 直接使用 big_g
            self.queryset = big_g_qs
            self.data_count = self.queryset.count()
            self.serializer_class = ReserveDownloadOrderSerializer

    def only_check_count(self):
        """
        只校验数量
        :return:
        """
        self.get_order_code_list()
        self.inquire_queryset()
        if self.data_count > self.DATA_COUNT_LIMIT:
            return False, f'数据量为{self.data_count}, 超过{self.DATA_COUNT_LIMIT}条，禁止导出，请修改筛选条件'
        if self.data_count == 0:
            return False, '数据量为0，请修改筛选条件'
        return True, f'数据量为{self.data_count}'

    def exec_serializer(self):
        """
        执行序列化
        :return:
        """
        try:
            self.write_data_list = self.serializer_class(self.queryset, many=True).data
            self.serializer_ok = True
        except Exception as e:
            self.serializer_ok = False
            self.write_data_list = []
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=6, task_result=str(e), is_success=False)

    def append_no_permission_code_data(self):
        """
        向序列化后的 write_data_list 中，追加不在权限范围内的订单码数据，内容为 “无权限查看”
        :return:
        """
        if len(self.no_permission_code_list) == 0:
            return
        if not self.serializer_ok:
            return

        if self.order_code_mode == 'big_G':
            for code in self.no_permission_code_list:
                data = {'sn': code, 'order_day': '无权查看', 'fen_dian_name': '无权查看'}
                self.write_data_list.append(data)
        else:
            for code in self.no_permission_code_list:
                data = {
                    'taobao_tbno': code,
                    'order_day': '无权查看',
                    'fen_dian_name': '无权查看'
                }
                self.write_data_list.append(data)

    def gen_excel(self):
        if not self.serializer_ok:
            return False
        # 生成 excel
        try:
            LargeDataExport(data_list=self.write_data_list, file_name=self.file_name).save()
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=7, is_success=True, can_download=True)
            return
        except Exception as e:
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=8, task_result=str(e), is_success=False)
            return

    def exec(self):
        # 1, 查询数据
        ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=4)
        self.get_order_code_list()
        self.inquire_queryset()
        # 2， 更新数据量,并校验
        ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(data_count=self.data_count)
        if self.data_count > self.DATA_COUNT_LIMIT:
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=6, task_result=f'数据量为{self.data_count}, 超过{self.DATA_COUNT_LIMIT}条，禁止导出，请修改筛选条件', is_success=False)
            return False
        if self.data_count == 0:
            ReserveDownload.objects.filter(id=self.reserve_download_record_id).update(task_status=6, task_result='数据量为0，请修改筛选条件', is_success=False)
            return False
        # 3， 执行序列化
        self.exec_serializer()
        if not self.serializer_ok:
            return False
        # 4， 追加无权限查看的数据
        self.append_no_permission_code_data()
        # 5， 生成 excel
        self.gen_excel()


class TestInquire:

    def __init__(self, num):
        self.num = num
        self.queryset = None
        self.data_count = 0
        print('TestInquire 实例化', self.num)

    def exec(self):
        print('exec 方法执行', self.num)

if __name__ == '__main__':
    query = {
        "date_type": "order_date",
        "start_date": "2024-04-02",
        "end_date": "2024-04-05",
        "fendian_id_list": [
            161,
            263,
            256,
            261,
            218
        ],
        "scan_code_status_id_list": [
            294,
            11,
            34,
            37,
            65,
            66,
            69,
            70,
            71,
            72,
            73,
            74,
            78,
            67,
            68,
            83,
            82,
            33,
            80,
            32,
            84,
            85,
            88,
            287,
            286,
            285,
            284,
            253,
            115,
            47,
            42,
            40,
            26,
            23,
            22,
            9,
            295,
            90,
            91,
            92,
            93,
            94,
            245,
            229,
            169,
            168,
            159,
            158,
            149,
            111,
            109,
            296,
            194,
            189,
            240,
            239,
            195,
            191,
            190,
            187,
            192,
            291,
            241,
            231,
            222,
            208,
            203,
            180,
            177,
            176,
            175,
            172,
            171,
            166,
            162,
            238,
            314,
            213,
            218,
            188,
            261,
            260,
            258,
            257,
            256,
            255,
            254,
            252,
            251,
            235,
            232,
            64,
            299,
            306,
            13,
            48,
            273,
            276,
            277,
            275,
            271,
            270,
            266,
            263,
            262,
            242,
            220,
            164,
            17,
            14,
            186,
            206,
            174,
            116,
            8,
            10,
            307,
            50,
            185,
            300,
            298,
            302,
            303,
            305,
            246,
            311,
            312,
            319,
            318,
            315,
            316,
            320,
            325,
            7,
            173,
            324,
            323,
            329,
            309,
            290
        ],
        "task_tag": "234",
        "is_history": False,
        "commodity_category_id_list": [],
        "scanner_id_list": [],
        "live_shift_list": [1, 2, 3],
        "platform_status_list": [],
        "is_Guding_link": None,
        "has_certificate": None,
        "shichangzhuanyuan_id_list": [],
        "pinjianzhuangtai_list": [],
        "is_ship": None,
        "order_situation_list": [],
        "zhubo_id_list": [],
        "shipper_id_list": [],
        "creator_id": 6623
    }
    # t = ReserveDownloadOrderInquirer(query_param_dict=query)
    # t.only_check_count()
    # print('数量：', t.data_count)

