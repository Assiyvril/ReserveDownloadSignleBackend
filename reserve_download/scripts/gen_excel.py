import os

# from v3.utils.export import ExportBase
from openpyxl import Workbook
from django.conf import settings

EXPORT_DIR = os.path.join(settings.MEDIA_ROOT, 'Export_Excel', 'Reserve_Download')

# class ReserveDownloadExport(ExportBase):
#
#     excel_headers = (
#         ['下单日期', '店铺', '单号', '班次', '客户昵称', '货品', '数量', '金额', '成本金额', '成本导入时间', '固定货款', '代购费', '证书费', '绳子费', '盒子费',
#          '运费', '其它', '多付金额', '附加扣款', '附加补款', '货主证书', '扣点', '利润', '应付商家', '扣点调否', '扣调ID', '差异扣点', '售后金额', '货主', '货主ID',
#          '主播', '助理', '备注', '录单员', '系统状态', '流程状态', '退款金额', '退款状态', '自动状态', '流程最近更新者', '订单更新时间', '订单创建时间', '订单付款时间',
#          '电商订单', '支付方式', '交易截图', '标题', '标题货品码', '销售件数', '是否打印', '是否加帐', '证书', '发货记录', '优惠券', '链接类型', '货主备注', '货品单号',
#          '场次ID', '班次时间', '厂长', '班次长', '市场人员', '助理2', '助理3', '助理4', '场控1', '场控2', '场控3', '场控4', '客服1', '客服2', '客服3', '客服4',
#          '拉新专员', '图片地址', '直播方式', '扫码时间', '扫码状态', '扫码人', '扫码历史流程', '品检状态', '品检类型', '品检备注', '品检人', '品检时间', '预售订单',
#          '待结ID', '结扣ID', '结算ID'],
#     )
#
#     col_keys = [
#         'order_day', 'fen_dian_name', 'sn', 'ban_ci', '客户昵称', 'category_name', 'quantity', 'amount', '成本金额', '成本导入时间', 'finance_amount',
#         '代购费', '证书费', '绳子费', '盒子费', 'yunfei', '其它', '多付金额', '附加扣款', '附加补款', '货主证书', 'kickback', '利润', 'should_pay_merchant',
#         '扣点调否', '调扣ID', '差异扣点', '售后金额', 'shipper_name', 'shipper_id', 'zhubo_name', 'zhuli_name', '备注', '录单员', '系统状态',
#         'item_status_name', '退款金额', '退款状态', '自动状态', '流程最近更新者', '订单更新时间', '订单创建时间', 'taobao_order_pay_time', 'taobao_tbno',
#         '支付方式', '交易截图', 'title', '标题货品码', 'quantity', '是否打印', '是否加帐', '证书', '发货记录', 'yhq', 'link_type', '货主备注',
#         'itemcode', '场次ID', '班次时间', 'chang_zhang_name', 'ban_ci_zhang', 'shi_chang_ren_yuan', 'zhu_li_2', 'zhu_li_3', 'zhu_li_4', 'chang_kong_1',
#         'chang_kong_2', 'chang_kong_3', 'chang_kong_4',
#         'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', '拉新专员', '图片地址', 'zhibo_type_text', 'scan_code_time', '扫码状态', '扫码人', '扫码历史', '品检状态',
#         '品检类型', '品检备注', '品检人', '品检时间', '预售订单', '待结ID', '结扣ID', '结算ID',
#         ]

# 
# test_header_list = ['下单日期', '店铺', '单号', '班次', '客户昵称', '货品', '数量', '金额', '成本金额', '实付金额', '成本导入时间', '固定货款', '代购费',
#                     '证书费', '绳子费', '盒子费',
#                     '运费', '其它', '多付金额', '附加扣款', '附加补款', '货主证书', '扣点', '利润', '应付商家', '扣点调否', '扣调ID', '差异扣点',
#                     '售后金额', '货主', '货主ID',
#                     '主播', '助理', '备注', '录单员', '系统状态', '流程状态', '退款金额', '退款状态', '自动状态', '流程最近更新者', '订单更新时间',
#                     '订单创建时间', '订单付款时间',
#                     '电商订单', '支付方式', '交易截图', '标题', '标题货品码', '销售件数', '是否打印', '是否加帐', '证书', '发货记录', '优惠券',
#                     '链接类型', '货主备注', '货品单号',
#                     '场次ID', '班次时间', '厂长', '厂长2', '班次长', '市场人员', '助理2', '助理3', '助理4', '场控1', '场控2', '场控3', '场控4',
#                     '客服1', '客服2', '客服3', '客服4',
#                     '拉新专员', '图片地址', '直播方式', '扫码时间', '扫码状态', '扫码人', '扫码历史流程', '品检状态', '品检类型', '品检备注',
#                     '品检人', '品检时间', '预售订单',
#                     '待结ID', '结扣ID', '结算ID']
# COL_KEYS = [
#     'order_day', 'fen_dian_name', 'sn', 'ban_ci', '客户昵称', 'category_name', 'quantity', 'amount', '成本金额', 'total_paid', '成本导入时间', 'finance_amount',
#     '代购费', '证书费', '绳子费', '盒子费', 'yunfei', '其它', '多付金额', '附加扣款', '附加补款', '货主证书', 'kickback', '利润',
#     'should_pay_merchant',
#     '扣点调否', '调扣ID', '差异扣点', '售后金额', 'shipper_name', 'shipper_id', 'zhubo_name', 'zhuli_name', '备注', '录单员', '系统状态',
#     'item_status_name', '退款金额', '退款状态', '自动状态', '流程最近更新者', '订单更新时间', '订单创建时间', 'taobao_order_pay_time', 'taobao_tbno',
#     '支付方式', '交易截图', 'title', '标题货品码', 'quantity', '是否打印', '是否加帐', '证书', '发货记录', 'yhq', 'link_type', '货主备注',
#     'itemcode', '场次ID', '班次时间', 'chang_zhang_name', 'chang_zhang2_name', 'ban_ci_zhang', 'shi_chang_ren_yuan', 'zhu_li_2', 'zhu_li_3', 'zhu_li_4',
#     'chang_kong_1',
#     'chang_kong_2', 'chang_kong_3', 'chang_kong_4',
#     'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', '拉新专员', '图片地址', 'zhibo_type_text', 'scan_code_time', '扫码状态', 'code_scaner', '扫码历史',
#     '品检状态',
#     '品检类型', '品检备注', '品检人', '品检时间', '预售订单', '待结ID', '结扣ID', '结算ID',
# ]

# 严格按照序列化器的字段顺序的 header
# excel_header1 = [
#     '下单日期', '店铺', '单号', '货品', '数量', '金额', '固定货款', '运费',
#     '扣点', '应付商家', '货主', '货主ID', '主播', '助理',
#     '流程状态', '电商订单', '优惠券', '货品单号', '厂长', '直播方式',
#     '标题', '订单付款时间', '链接类型', '扫码时间', '班次', '班次长',
#     '市场人员', '助理2', '助理3', '助理4', '场控1', '场控2', '场控3',
#     '场控4', '客服1', '客服2', '客服3', '客服4', '厂长2', '扫码人', '实付金额',
#     '扫码历史', '扫码状态', '品检状态', '代购费', '证书费', '绳子费', '盒子费',
#     '其它费用', '多付金额', '图片地址', '备注', '自动状态', '订单创建时间', '证书',
#     '发货记录', '货主备注', '场次ID', '班次时间', '是否打印', '流程最近更新者',
#     '预售订单', '系统状态', '退款状态', '品检类型', '品检备注',
#     '品检人', '品检时间', '交易截图', '成本金额', '附加扣款',
#     '附加补款', '调扣ID', '退款金额', '订单更新时间', '是否加帐',
#     '分类一级', '分类二级', '分类三级', '分类四级', '最晚发货时间',
# ]

# excel_header1 = []

# 正式的表头，调整了顺序
OFFICIAL_HEADER = [
    '店铺', '单号', '标题', '下单日期', '电商订单', '货品', '数量', '备注', '货品码', '货主货品单号',
    '金额', '固定货款', '优惠券', '运费', '客户昵称',
    '代购费', '证书费', '绳子费', '盒子费', '其它费用', '杂项支出',
    '实付金额', '多付金额', '成本金额', '利润', '上传成本价',
    '扣点', '应付商家',  '货主', '货主ID', '货主备注',
    '订单付款时间', '链接类型', '扫码状态', '扫码时间', '扫码人', '扫码历史',
    '主播', '助理', '厂长', '直播方式', '班次', '班次时间', '班次长', '场次ID', '市场人员', '助理2', '助理3', '助理4',
    '场控1', '场控2', '场控3', '场控4', '客服1', '客服2', '客服3', '客服4', '厂长2',
    '品检状态', '品检类型', '品检备注', '品检人', '品检时间',
    '分类一级', '分类二级', '分类三级', '分类四级',
    '流程状态', '流程最近更新者', '自动状态', '系统状态', '退款状态', '退款数量',
    '订单创建时间', '图片地址', '交易截图', '订单更新时间', '最晚发货时间',
    '证书', '发货记录', '是否打印', '是否加帐', '预售订单', '附加扣款', '附加补款', '调扣ID', '退款金额',
    '收货组跟进', '关联店铺', '标题货品码',
    '拉新专员', '销售专员', '转粉专员', '支付方式', '货主证书', '扣点调否', '差异扣点', '售后金额',
    '待结ID', '结扣ID', '结算ID', '成本导入时间', '录单员',
]

OFFICIAL_COL_KEYS = [
    'fen_dian_name', 'sn', 'title', 'order_day', 'taobao_tbno', 'category_name', 'quantity', 'seller_memo', 'itemcode', 'shipper_goods_sn',
    'amount', 'finance_amount', 'yhq', 'yunfei', 'buyer_nick_name',
    'dai_gou_fee', 'zheng_shu_fee', 'sheng_zi_fee', 'he_zi_fee', 'other_fee', 'za_xiang',
    'total_paid', 'duo_fu_jin_e', 'cost_amount', 'profit', 'old_costamount',
    'kickback', 'should_pay_merchant', 'shipper_name', 'shipper_id', 'shipper_memo',
    'taobao_order_pay_time', 'link_type', 'scan_code_status', 'scan_code_time', 'code_scaner', 'scan_code_history',
    'zhubo_name', 'zhuli_name', 'chang_zhang_name', 'zhibo_type_text', 'ban_ci', 'ban_ci_time', 'ban_ci_zhang', 'chang_ci_id', 'shi_chang_ren_yuan',
    'zhu_li_2', 'zhu_li_3', 'zhu_li_4',
    'chang_kong_1', 'chang_kong_2', 'chang_kong_3', 'chang_kong_4', 'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', 'chang_zhang2_name',
    'check_good_status', 'check_good_category', 'checkgoods_desc', 'checkgoods_checker', 'checkgoods_time',
    'category_level_1', 'category_level_2', 'category_level_3', 'category_level_4',
    'item_status_name', 'flow_newest_updater', 'auto_status_text', 'system_status', 'refund_status', 'refund_quantity',
    'order_create_time', 'goods_image_url', 'trade_screenshot', 'order_update_time', 'delivery_time_dead_line',
    'zheng_shu', 'fa_huo_ji_lu', 'is_print', 'is_add_account', 'is_presale_order', 'additional_deduction', 'additional_payment', 'deduction_id', 'refund_amount',
    'desc_shz_gj', 'guanlian_fendian', 'title',
    '拉新专员', 'zhubo_name', 'zhuli_name', '支付方式', 'zheng_shu_fee', '扣点调否', '差异扣点', '售后金额',
    '待结ID', '结扣ID', '结算ID', '成本导入时间', '录单员',
]


class LargeDataExport(object):

    def __init__(self, data_list, file_name):
        # if headers_list is None:
        #     headers_list = test_header_list
        # if col_keys is None:
        #     col_keys = test_col_keys
        self.data_list = data_list
        self.headers_list = OFFICIAL_HEADER
        self.file_name = file_name
        self.col_keys = OFFICIAL_COL_KEYS
        self.wb = Workbook(write_only=True)
        self.ws = self.wb.create_sheet()

    def write_header(self):
        self.ws.append(self.headers_list)
        # print('写入表头完毕', self.headers_list)

    def write_data(self):
        for data in self.data_list:
            row = []
            for key in self.col_keys:
                row.append(data.get(key, ''))
            self.ws.append(row)

    def check_path(self):
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)

    def save(self):
        self.write_header()
        print('开始写入内容数据')
        self.write_data()
        print('写入内容数据完毕')
        self.check_path()
        self.wb.save(os.path.join(EXPORT_DIR, self.file_name))
