#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.db import models
from django.utils import timezone
from datetime import datetime, time
from decimal import Decimal

from commodity_category.models import ShopCategory
from live_play.models import OrderPlay
from order.order_status_enum import OrderFlowStatus, OrderCheckedStatus
from shipper.models import ShopShipper
from shop.models import ShopSerialprefix
from user.models import AccountMyuser

timezone.activate('Asia/Shanghai')


class ItemStatus(models.Model):

    STATUS_TYPE_CHOICE = (
        ('0', u'未退款'),
        ('1', u'跑单退款'),
        ('2', u'售后退款'),
        ('3', u'待减账退款'),
        ('-1', u'----------'),
        ('4', u'可结算状态'),
    )

    shop_id = models.IntegerField(blank=True, null=True, default=2)
    name = models.CharField(u'名称', max_length=31)
    notes = models.CharField(u'说明', max_length=63, null=True, blank=True)
    statustype = models.CharField(u'状态类型', choices=STATUS_TYPE_CHOICE, default='0', max_length=2)
    sort = models.PositiveIntegerField(u'排序', default=200, help_text=u'从小到大显示')
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    is_refund = models.BooleanField(u'是否退款', default=False, help_text=u'是否退款')
    is_active = models.BooleanField(u'是否启用', default=True, help_text=u'是否启用')

    class Meta:
        verbose_name = u'订单流程'
        verbose_name_plural = u'订单流程'
        ordering = ('sort',)
        unique_together = ('shop_id', 'name',)
        managed = False
        db_table = 'shop_itemstatus'


# 系统订单数据模型
class OrderOrder(models.Model):
    # ### 基础信息 ###
    title = models.CharField('宝贝标题', max_length=255, blank=True, null=True, db_column='guding_title')
    quantity = models.SmallIntegerField('数量')
    amount = models.DecimalField('货价', max_digits=15, decimal_places=2)
    yhq = models.DecimalField('优惠券', default=0, max_digits=10, decimal_places=2)
    yunfei = models.FloatField('运费', default=0, db_column='shipping')
    other = models.FloatField('其它费用(海外订单税费)', default=0)
    payment_currency = models.SmallIntegerField('订单计价币种', blank=True, null=True)  # 字典值 1或空-人民币
    order_amount = models.DecimalField('应收订单金额', max_digits=15, decimal_places=2, blank=True, null=True,
                                       default=0)
    exchange_rate = models.DecimalField('第三方结账汇率', max_digits=10, decimal_places=6, blank=True, null=True)
    sn = models.CharField('单号', max_length=63)  # 重要 自定义或自动生成
    desc = models.TextField('备注', blank=True, null=True)
    image = models.CharField('打印图片', max_length=100, blank=True, null=True)  # 打印生成同步
    image_1 = models.CharField('产品图片1', max_length=100, blank=True, null=True)
    image_2 = models.CharField('产品图片2', max_length=100, blank=True, null=True)
    image_3 = models.CharField('产品图片3', max_length=100, blank=True, null=True)
    image_4 = models.CharField('产品图片4', max_length=100, blank=True, null=True)
    image_5 = models.CharField('产品图片5', max_length=100, blank=True, null=True)
    day = models.DateField('下单日期', blank=True, null=True)  # 与class日期同步
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modified = models.DateTimeField('最近更新时间', null=True, blank=True, auto_now=True)
    # ####### 状态字段 #######
    # order_status = models.CharField('订单核对状态', max_length=2, default=OrderCheckedStatus.UNCERTIFIED.value,
    #                                 db_column='status')  # 订单核对或删除等状态
    flow_status = models.CharField('订单流程状态', max_length=2, default=OrderFlowStatus.NEW_ORDER.value,
                                   db_column='autostatus')  # 控制订单流程状态 自动状态
    # #######无关但必需写入的字段##### #
    fee = models.DecimalField('代购费', max_digits=15, decimal_places=2, default=0)
    has_wen = models.BooleanField('有纹', default=False)
    has_lie = models.BooleanField('有裂', default=False)
    certificate = models.FloatField('证书费', default=0)
    is_zhengshu = models.IntegerField('是否有证书', default=0)
    kouzi = models.FloatField('扣子费', default=0)
    lianzi = models.FloatField('链子费', default=0)
    shengzi = models.FloatField('绳子费', default=0)
    erxian = models.FloatField('耳线费', default=0)
    box = models.FloatField('盒子费', default=0)
    overage = models.FloatField('多付金额', default=0)
    refund_fee = models.FloatField('退货费用', default=0)

    flat = models.IntegerField('同步标记', blank=True, null=True, default=0)
    is_check = models.IntegerField('联络审核状态', blank=True, null=True, default=0)  # 默认0
    printstatus = models.BooleanField('是否打印', default=False)
    # #######关联字段########## #
    # fendian与prefix_id相同，过渡使用，以fendian为主
    fendian = models.ForeignKey(ShopSerialprefix, models.DO_NOTHING, blank=True, null=True, db_column='fendian',
                                verbose_name='店铺', related_name='n_orders')
    prefix = models.ForeignKey(ShopSerialprefix, models.DO_NOTHING, blank=True, null=True, verbose_name='店铺(旧)',
                               related_name='o_orders', db_column='prefix_id')
    zhubo = models.ForeignKey(AccountMyuser, models.DO_NOTHING, related_name='oo_zhubo', verbose_name='主播')
    creator = models.ForeignKey(AccountMyuser, models.DO_NOTHING, related_name='oo_creator', verbose_name='创建人')
    shipper = models.ForeignKey(ShopShipper, models.DO_NOTHING, verbose_name='货主', db_column='shipper_id')
    category = models.ForeignKey(ShopCategory, models.DO_NOTHING, blank=True, null=True, verbose_name='商品类目')
    # item_status = models.OneToOneField(ShopItemstatus, models.DO_NOTHING, blank=True, null=True,
    #                                    verbose_name='流程状态')
    zhuli = models.ForeignKey(AccountMyuser, models.DO_NOTHING, verbose_name='助理')  # 暂不关联
    shop_id = models.IntegerField('所属商户', blank=True, null=True, default=2)  # 暂不关联
    play = models.ForeignKey(OrderPlay, models.DO_NOTHING, blank=True, null=True)
    # 支付凭证many2many关联
    # pay_vouchers = models.ManyToManyField(OrderTaobaoorder, through='OrderTaobaoorderOrders',
    #                                       through_fields=('order', 'taobaoorder'), verbose_name='平台订单关联',
    #                                       related_name='orders')

    itemcode = models.CharField('商品编号', max_length=1550, blank=True, null=True)
    finance_amount = models.FloatField('固定货价/财务金额', blank=True, null=True)

    # autostatus = models.CharField('自动状态', max_length=2, blank=True, null=True)
    item_status = models.ForeignKey(ItemStatus, related_name='orders_item_status', verbose_name=u'流程状态', null=True, blank=True,
                                    help_text=u'通过订单流程来设置',
                                    on_delete=models.SET_NULL)
    status = models.CharField('是否删除 0 为没删', max_length=2, blank=True, null=True)
    taobao_order_count = models.IntegerField('平台订单数量，有多少个平台订单属于此大G订单 理应最少为 1', blank=True, null=True)

    shipper_memo = models.CharField('货主备注', max_length=2550, blank=True, null=True)
    is_guding_url = models.IntegerField('是否固定链接', blank=True, null=True, default=1)

    class Meta:
        managed = False
        db_table = 'order_order'

    """
    #########order_order实例方法#########
    """

    # 订单状态更新
    def update_status(self):
        """
        核对订单金额与支付凭证金额
        忽略删除状态订单和收款凭证
        """
        if self.order_status == OrderCheckedStatus.DELETED.value:
            return
        # 订单金额, 没有记录币种的使用订单计价， 有币种记录的使用订单应收
        order_amount = Decimal(str(self.amount)) - Decimal(str(self.yhq)) + Decimal(str(self.yunfei)) + Decimal(
            str(self.other))  # 原订单计价
        # 收款总金额
        payment_sum = 0
        # 收款凭证金额统计
        payments = self.pay_vouchers.all()
        for payment in payments:
            # + 直接计价
            payment_sum += payment.p_amount
        # 比对应收应付
        if order_amount == payment_sum:
            # 核对成功
            # 订单更新核对状态
            self.order_status = OrderCheckedStatus.CERTIFIED.value
        elif order_amount < payment_sum:
            # 核对异常
            self.order_status = OrderCheckedStatus.VERIFY_ERROR.value
        elif order_amount > payment_sum:
            # 核对异常
            self.order_status = OrderCheckedStatus.UNCERTIFIED.value
        self.save(update_fields=['order_status'])

    def delete(self, *args, **kwargs):
        # 重载删除方法，设置删除标记
        self.order_status = OrderCheckedStatus.DELETED.value
        self.save(update_fields=['order_status'])

    """
    #########order_order类方法#########
    """

    # sn查重方法
    @classmethod
    def is_sn_exist(cls, sn):
        return cls.objects.filter(sn=sn).only('id').exists()

    # 获取指定店铺，当日或指定日期的总单量
    @classmethod
    def get_current_day_order_count(cls, prefix):
        # now = timezone.datetime.strptime(day, '%Y-%m-%d').date() if day != '' else timezone.now()
        # start_date = timezone.make_aware(timezone.datetime(now.year, now.month, now.day))
        # end_date = start_date + timezone.timedelta(days=1)
        start_datetime = datetime.combine(datetime.today(), time.min)
        end_datetime = datetime.combine(datetime.today(), time.max)
        order_count = cls.objects.filter(fendian__id=prefix, created_time__range=[start_datetime, end_datetime]).count()
        return order_count

    """
    #########order_order实例属性#########
    """

    # 成交状态
    @property
    def is_turnover(self):
        # 发货状态(不是退款状态列入成交)
        # today = timezone.now().date()
        # diff_day = (today - self.day).days
        return self.item_status is None or not self.item_status.is_refund

    # 订单实付金额
    @property
    def rcv_amount(self):
        return float(self.amount) - float(self.yhq) + float(self.yunfei) + float(self.other)

    # 已送检状态(扫码状态有存在过BIC送检的订单)
    @property
    def has_bic(self):
        """
        涉及到查询扫码流程数据，需预取flows数据
        """
        # for flow in self.flows.all():
        #     print(flow.status.name)
        return False


# 企得宝订单数据，2023-12-02 添加，用于获取订单图片，别的用不上
class QiDeBaoOrderInfo(models.Model):
    shop_id = models.IntegerField(blank=True, null=True, default=2)
    prefix = models.ForeignKey(ShopSerialprefix, models.DO_NOTHING, blank=True, null=True, verbose_name='店铺')
    order = models.ForeignKey(OrderOrder, models.DO_NOTHING, blank=True, null=True, verbose_name='系统订单')
    tradeno = models.CharField(max_length=255, blank=True, null=True, verbose_name='交易单号')
    seller_message = models.CharField(db_column='sellerMessage', max_length=5000, blank=True, null=True, verbose_name='备注？')
    platform_goods_name = models.CharField(max_length=255, blank=True, null=True, db_column='platformgoodsname', verbose_name='平台商品名称')
    platformrefundstatus = models.CharField(db_column='platformRefundStatus', max_length=255, blank=True, null=True)
    orderagioamount = models.FloatField(db_column='orderAgioAmount', blank=True, null=True)
    agioamount = models.FloatField(db_column='agioAmount', blank=True, null=True)
    buyernick = models.CharField(db_column='buyerNick', max_length=255, blank=True, null=True)
    paydate = models.DateTimeField(db_column='payDate', blank=True, null=True)
    payamount = models.FloatField(db_column='payAmount', blank=True, null=True)
    createdate = models.DateTimeField(blank=True, null=True)
    platformgoodsspecs = models.CharField(db_column='platformGoodsSpecs', max_length=255, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    bicordercode = models.CharField(db_column='bicOrderCode', max_length=255, blank=True, null=True)
    receivermobile = models.CharField(db_column='receiverMobile', max_length=3100, blank=True, null=True)
    postamount = models.FloatField(db_column='postAmount', blank=True, null=True)
    receivername = models.CharField(db_column='receiverName', max_length=3200, blank=True, null=True)
    receiveraddress = models.CharField(db_column='receiverAddress', max_length=3300, blank=True, null=True)
    sourcecreatedate = models.DateTimeField(blank=True, null=True)
    shopid = models.CharField(db_column='shopId', max_length=255)
    picurl = models.CharField(max_length=255, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    refundamount = models.FloatField(db_column='refundAmount', blank=True, null=True)
    refundreason = models.CharField(db_column='refundReason', max_length=255, blank=True, null=True)
    up_count = models.IntegerField(blank=True, null=True)
    afteragioamount = models.FloatField(db_column='afterAgioAmount', blank=True, null=True)
    returnkind = models.CharField(max_length=255, blank=True, null=True)
    qdb_code = models.TextField(blank=True, null=True)
    refund_qdb_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_qdborderlist'


class OrderFlow(models.Model):
    """
    订单 扫码相关状态
    """
    desc = models.TextField(null=True, blank=True, verbose_name='描述说明')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    old_status = models.ForeignKey(ItemStatus, models.DO_NOTHING, verbose_name='旧状态', related_name='order_old_flows')
    order = models.ForeignKey(OrderOrder, models.DO_NOTHING, verbose_name='大G订单', related_name='scan_code_flows')
    owner = models.ForeignKey(AccountMyuser, models.DO_NOTHING, verbose_name='操作人')
    shop_id = models.IntegerField('所属商户', blank=True, null=True, default=2)  # 暂不关联
    status = models.ForeignKey(ItemStatus, models.DO_NOTHING, verbose_name='新状态', related_name='order_new_flows')
    # batch_id 指向 BatchOrders, 这里用不上，暂定为 IntegerField
    batch_id = models.IntegerField('扫码动作的归集ID', blank=True, null=True, default=0)

    class Meta:
        managed = False
        db_table = 'order_orderflow'


class OrderTaobaoorder(models.Model):
    # ### 订单基础信息 ###
    tbno = models.CharField('交易单号', max_length=127)
    p_amount = models.DecimalField('收款金额', max_digits=15, decimal_places=2, db_column='amount')  # 收款金额(人民币)
    pirce = models.DecimalField('收款金额_1', max_digits=15, decimal_places=2)  # 与amount一致
    real_amount = models.DecimalField('收款金额_2', max_digits=15, decimal_places=2)  # 与amount一致
    remittance = models.DecimalField('外币金额', max_digits=15, decimal_places=2)  # 外币收款金额
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    src = models.CharField('交易渠道平台', max_length=2)  # 字典
    img_list = models.CharField('交易凭证', max_length=5000, blank=True, null=True, db_column='imglist')  # 图片列表
    currency_type = models.SmallIntegerField('收款货币种类', blank=True, null=True)  # 字典
    trans_type = models.CharField('交易渠道', max_length=2, db_column='orderstatus')  # 交易渠道
    sn = models.CharField('大G码', max_length=255, blank=True, null=True)  # 系统订单sn 大G码
    buyer = models.CharField('买家ID', max_length=127, blank=True, null=True)
    # ### 订单客户信息 ###
    buyer_note = models.CharField('买家备注', max_length=600, blank=True, null=True)
    contact = models.CharField('收货人', max_length=2550, blank=True, null=True)
    address = models.CharField('收货地址', max_length=511, blank=True, null=True)
    phone = models.CharField('联系号码1', max_length=127, blank=True, null=True)
    mobile = models.CharField('联系号码2', max_length=127, blank=True, null=True)
    # ### 关联信息 ###
    shop_id = models.IntegerField(default=2)
    fendian = models.ForeignKey(ShopSerialprefix, models.DO_NOTHING, related_name='f_tborders', db_column='fendian')
    prefix = models.ForeignKey(ShopSerialprefix, models.DO_NOTHING, related_name='f_tborders2',
                               db_column='prefix_id')
    # sys_orders = models.ManyToManyField('OrderOrder', through='OrderTaobaoorderOrders',
    #                                     through_fields=('taobaoorder', 'order'), verbose_name='系统订单关联')

    # ###未使用字段###
    point = models.IntegerField('未知0', default=0)
    point_return = models.IntegerField('未知1', default=0)
    point_real = models.IntegerField('未知2', default=0)
    ship_fee = models.DecimalField('运费', max_digits=15, decimal_places=2, default=0)  # 海外订单不在此处记录
    product_count = models.IntegerField('产品数量', default=1)  # 非自动抓取，不作记录
    tbcreated_time = models.DateTimeField('下单时间', blank=True, null=True, auto_now_add=True)
    tbpayed_time = models.DateTimeField('支付时间', blank=True, null=True, auto_now_add=True)
    status = models.CharField('核对状态', max_length=2, default=OrderCheckedStatus.CERTIFIED.value)  # 历史字段，无实际用途

    # refund_time = models.DateTimeField('退款时间', blank=True, null=True)
    # refund_desc = models.CharField('退款描述', max_length=255, blank=True, null=True)
    # refund_fee = models.FloatField('退款金额', blank=True, null=True)
    seller_memo = models.CharField('卖家备注', max_length=2550, blank=True, null=True)

    is_bindprint = models.IntegerField(verbose_name='是否已经QIC，绑定了 BIC, 3 表示已经绑定', blank=True, null=True)
    is_pass_qic_check = models.IntegerField(verbose_name='是否通过 QIC 检查，0 表示订单初生 还没示有下载bic码，1 表下载了BIC码 还未进行绑码操作，2 表示成功  3表示绑码失败', blank=True, null=True)
    dy_order_code = models.CharField(verbose_name='BIC，预绑定的', blank=True, null=True, max_length=255)
    qualityagency = models.CharField(verbose_name='质检机构 NGTC/GTC', null=True, blank=True, max_length=20)
    goods_specs = models.CharField(verbose_name='商品规格', null=True, blank=True, max_length=255, db_column='goodsSpecs')

    class Meta:
        managed = False
        db_table = 'order_taobaoorder'

    @classmethod
    def is_tbno_exist(cls, tbno):
        return cls.objects.filter(tbno=tbno).exists()


class OrderTaobaoorderOrders(models.Model):
    taobaoorder = models.ForeignKey(OrderTaobaoorder, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderOrder, on_delete=models.CASCADE, related_name='rel_to_taobao_order')

    class Meta:
        managed = False
        db_table = 'order_taobaoorder_orders'
        unique_together = (('taobaoorder', 'order'),)
