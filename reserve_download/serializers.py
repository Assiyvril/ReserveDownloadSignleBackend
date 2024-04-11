from rest_framework import serializers

from order.models import ItemStatus, OrderTaobaoorder, OrderOrder, OrderFlow
from reserve_download.models import ReserveDownload
from shop.models import ShopSerialprefix
from user.models import AccountMyuser


class ReserveDownloadRecordSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.first_name', read_only=True, help_text='创建人名称', label='创建人名称')
    creator_id = serializers.PrimaryKeyRelatedField(
        source='creator', queryset=AccountMyuser.objects.filter(is_active=True), help_text='创建人id',
    )

    task_status_text = serializers.CharField(source='get_task_status_display', read_only=True, help_text='任务状态', label='任务状态')
    file_url = serializers.SerializerMethodField(read_only=True, help_text='文件下载地址', label='文件下载地址')
    fen_dian_name_text = serializers.SerializerMethodField(read_only=True, help_text='店铺名称 text', label='店铺名称 text')

    def get_file_url(self, obj):
        """
        文件下载地址
        """
        if obj.is_success:
            return 'media/Export_Excel/Reserve_Download/' + obj.file_name
        return ''

    def get_fen_dian_name_text(self, obj):
        """
        店铺名称 text， 便于前端展示
        @param obj:
        @return:
        """
        fendian_info_list = obj.fendian_info
        if not fendian_info_list:
            return ''
        fendian_name_text = ''
        for fen_dian in fendian_info_list:
            fendian_name_text += fen_dian['name'] + ', '
        # 去掉最后的 ', '
        return fendian_name_text[:-2]


    def to_representation(self, instance):
        """
        将日期时间格式化为 %Y-%m-%d %H:%M:%S
        @param instance:
        @return:
        """
        ret = super(ReserveDownloadRecordSerializer, self).to_representation(instance)
        if ret['created_time']:
            ret['created_time'] = instance.created_time.strftime('%Y-%m-%d %H:%M:%S')
        if ret['task_exec_start_time']:
            ret['task_exec_start_time'] = instance.task_exec_start_time.strftime('%Y-%m-%d %H:%M:%S')
        if ret['task_exec_end_time']:
            ret['task_exec_end_time'] = instance.task_exec_end_time.strftime('%Y-%m-%d %H:%M:%S')
        # 扫码状态 text
        if ret['filter_condition'].get('scan_code_status'):
            scan_code_status_text = ''
            for scan_code_status_id in ret['filter_condition']['scan_code_status']:
                status_obj = ItemStatus.objects.filter(id=scan_code_status_id).first()
                if not status_obj:
                    continue
                if not status_obj.name:
                    continue
                scan_code_status_text += status_obj.name + ', '
            # 去掉最后的 ', '
            ret['filter_condition']['scan_code_status_text'] = scan_code_status_text[:-2]
        else:
            ret['filter_condition']['scan_code_status_text'] = ''
        return ret

    class Meta:
        model = ReserveDownload
        fields = ['id', 'creator_name', 'creator_id', 'created_time', 'filter_condition', 'fendian_info', 'task_status', 'task_exec_start_time',
                  'task_exec_end_time', 'data_count', 'file_url', 'fen_dian_name_text',
                  'task_status_text', 'task_celery_id', 'task_result', 'file_name', 'is_success', 'tag']


class ReserveDownloadOrderSerializer(serializers.ModelSerializer):
    """
    导出订单
    """
    order_day = serializers.CharField(source='day', read_only=True, help_text='下单日期', label='下单日期')
    fen_dian_name = serializers.CharField(source='prefix.name', read_only=True, help_text='店铺名称', label='店铺名称', default='')
    category_name = serializers.CharField(source='category.name', read_only=True, help_text='货品', label='货品', default='')
    kickback = serializers.SerializerMethodField(help_text='扣点', label='扣点')
    should_pay_merchant = serializers.SerializerMethodField(help_text='应付商家', label='应付商家')
    shipper_name = serializers.CharField(source='shipper.name', read_only=True, help_text='货主', label='货主', default='')
    shipper_id = serializers.CharField(source='shipper.id', read_only=True, help_text='货主ID', label='货主ID', default='')
    zhubo_name = serializers.CharField(source='zhubo.first_name', read_only=True, help_text='主播', label='主播', default='')
    zhuli_name = serializers.CharField(source='play.zhuli1.first_name', read_only=True, help_text='助理', label='助理', default='')
    item_status_name = serializers.CharField(source='item_status.name', read_only=True, help_text='流程状态', label='流程状态', default='')
    taobao_tbno = serializers.SerializerMethodField(help_text='电商平台单号', label='电商平台单号')
    chang_zhang_name = serializers.CharField(source='play.changzhang.first_name', read_only=True, help_text='厂长', label='厂长', default='')
    zhibo_type_text = serializers.CharField(source='play.get_zhibo_type_display', read_only=True, help_text='直播方式', label='直播方式', default='')
    # 订单付款时间, 标题, 链接类型, 扫码时间
    taobao_order_pay_time = serializers.SerializerMethodField(read_only=True, help_text='订单付款时间', label='订单付款时间')
    link_type = serializers.SerializerMethodField(read_only=True, help_text='链接类型', label='链接类型')
    scan_code_time = serializers.SerializerMethodField(read_only=True, help_text='扫码时间', label='扫码时间')
    ban_ci = serializers.SerializerMethodField(read_only=True, help_text='班次', label='班次')
    # 从班次长 到 客服4
    ban_ci_zhang = serializers.CharField(source='play.banzhang.first_name', read_only=True, help_text='班次长', label='班次长', default='')
    shi_chang_ren_yuan = serializers.CharField(source='play.shichangzhuanyuan.first_name', read_only=True, help_text='市场人员', label='市场人员', default='')
    # zhu_li_1 = serializers.CharField(source='play.zhuli1.first_name', read_only=True, help_text='助理1', label='助理1')
    zhu_li_2 = serializers.CharField(source='play.zhuli2.first_name', read_only=True, help_text='助理2', label='助理2', default='')
    zhu_li_3 = serializers.CharField(source='play.zhuli3.first_name', read_only=True, help_text='助理3', label='助理3', default='')
    zhu_li_4 = serializers.CharField(source='play.zhuli4.first_name', read_only=True, help_text='助理4', label='助理4', default='')
    chang_kong_1 = serializers.CharField(source='play.changkong.first_name', read_only=True, help_text='场控1', label='场控1', default='')
    chang_kong_2 = serializers.CharField(source='play.changkong1.first_name', read_only=True, help_text='场控2', label='场控2', default='')
    chang_kong_3 = serializers.CharField(source='play.changkong2.first_name', read_only=True, help_text='场控3', label='场控3', default='')
    chang_kong_4 = serializers.CharField(source='play.changkong3.first_name', read_only=True, help_text='场控4', label='场控4', default='')
    ke_fu_1 = serializers.CharField(source='play.kefu1.first_name', read_only=True, help_text='客服1', label='客服1', default='')
    ke_fu_2 = serializers.CharField(source='play.kefu2.first_name', read_only=True, help_text='客服2', label='客服2', default='')
    ke_fu_3 = serializers.CharField(source='play.kefu3.first_name', read_only=True, help_text='客服3', label='客服3', default='')
    ke_fu_4 = serializers.CharField(source='play.kefu4.first_name', read_only=True, help_text='客服4', label='客服4', default='')

    chang_zhang2_name = serializers.CharField(source='play.changzhang1.first_name', read_only=True, help_text='厂长2', label='厂长2', default='')
    code_scaner = serializers.SerializerMethodField(read_only=True, help_text='扫码人', label='扫码人')

    def get_kickback(self, obj):
        """
        扣点, 根据店铺类型，判断货主的扣点
        """
        fen_dian_src = obj.prefix.src
        shop_shipper_obj = obj.shipper

        if not fen_dian_src:
            return '店铺类型为空'
        if not shop_shipper_obj:
            return '货主数据为空'
        # 淘宝
        if fen_dian_src == '1':
            return shop_shipper_obj.kickback

        # 抖音
        elif fen_dian_src == '2':
            return shop_shipper_obj.kickback_dy

        # 拼多多
        elif fen_dian_src == '3':
            return shop_shipper_obj.kickback_dd

        # 快手
        elif fen_dian_src == '5':
            return shop_shipper_obj.kickback_ks

        # tikto
        elif fen_dian_src == '8':
            return shop_shipper_obj.kickback_tikto

        # 视频号
        elif fen_dian_src == '9':
            return shop_shipper_obj.kickback_shipin

        # 小红书
        elif fen_dian_src == '10':
            return shop_shipper_obj.kickback_xhs

        else:
            return '店铺类型错误' + fen_dian_src

    def get_should_pay_merchant(self, obj):
        # 计算应付商家， 根据扣点计算
        kickback = self.get_kickback(obj)
        # 能否转为float
        try:
            kickback = float(kickback)
        except Exception as e:
            return '无'
        # 计算应付商家， 金额 * （1 - 扣点）   amount * (1 - kickback)
        if not obj.amount:
            return '无'
        return float(obj.amount) * (1 - kickback)

    def get_taobao_tbno(self, obj):
        """
        平台单号
        """
        # rel_qs = OrderTaobaoorderOrders.objects.filter(order=obj)
        # if not rel_qs:
        #     return '无'
        # tbno = ''
        # for rel_obj in rel_qs:
        #     try:
        #         tbno += rel_obj.taobaoorder.tbno + ' |'
        #     except Exception as e:
        #         continue
        # # 去掉最后的 ' |'
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'
        tbno = ''
        for taobao_obj in taobao_qs:
            tbno += taobao_obj.tbno + ', '
        # 去掉最后的 ', '
        return tbno[:-2]

    def get_link_type(self, obj):
        if obj.is_guding_url == 1:
            return '固定链接'
        elif obj.is_guding_url == 2:
            return '闪购链接'
        else:
            return '未识别'

    @staticmethod
    def get_taobao_order_qs(obj):
        """
        获取大G订单关联的淘宝订单 qs
        """
        rel_qs = obj.rel_to_taobao_order.all()
        if not rel_qs:
            return OrderTaobaoorder.objects.none()
        taobao_id_list = []
        for rel_obj in rel_qs:
            try:
                tao_bao_order_obj = rel_obj.taobaoorder
            except Exception as e:
                continue
            taobao_id_list.append(tao_bao_order_obj.id)
        return OrderTaobaoorder.objects.filter(id__in=taobao_id_list)

    def get_taobao_order_pay_time(self, obj):
        """
        获取订单付款时间
        """
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'

        pay_time = taobao_qs.first().tbpayed_time.strftime('%Y-%m-%d %H:%M:%S')

        return pay_time

    def to_representation(self, instance):
        """
        将日期时间格式化为 %Y-%m-%d %H:%M:%S
        @param instance:
        @return:
        """
        blank_fields = [
            '客户昵称', '成本金额', '成本导入时间', '代购费', '证书费', '绳子费', '盒子费', '其它', '多付金额', '附加扣款', '附加补款',
            '货主证书', '利润', '扣点调否', '调扣ID', '差异扣点', '售后金额', '备注', '录单员', '系统状态', '退款金额', '退款状态', '自动状态',
            '流程最近更新者', '订单更新时间', '订单创建时间', '支付方式', '交易截图', '标题货品码', '是否打印', '是否加帐',
            '证书', '发货记录', '货主备注', '场次ID', '班次时间', '拉新专员', '图片地址',
            '扫码状态', '扫码历史', '品检状态', '品检类型', '品检备注', '品检人', '品检时间', '预售订单',
            '待结ID', '结扣ID', '结算ID'
        ]
        ret = super(ReserveDownloadOrderSerializer, self).to_representation(instance)
        for field in blank_fields:
            ret[field] = ''
        return ret

    def get_scan_code_time(self, obj):
        """
        扫码时间
        """
        # order_flow_obj = OrderFlow.objects.filter(order=obj).order_by('-created_time').first()
        order_flow_obj = obj.scan_code_flows.all().order_by('-created_time').first()
        if not order_flow_obj:
            return '无'
        return order_flow_obj.created_time.strftime('%Y-%m-%d %H:%M:%S')

    def get_code_scaner(self, obj):
        order_flow_obj = obj.scan_code_flows.all().order_by('-created_time').first()
        if not order_flow_obj:
            return '无'
        return order_flow_obj.owner.first_name

    def get_ban_ci(self, obj):
        return '无'

    class Meta:
        model = OrderOrder
        fields = [
            'order_day', 'fen_dian_name', 'sn', 'category_name', 'quantity', 'amount', 'finance_amount', 'yunfei',
            'kickback', 'should_pay_merchant', 'shipper_name', 'shipper_id', 'zhubo_name', 'zhuli_name',
            'item_status_name', 'taobao_tbno', 'yhq', 'itemcode', 'chang_zhang_name', 'zhibo_type_text',
            'title', 'taobao_order_pay_time', 'link_type', 'scan_code_time', 'ban_ci', 'ban_ci_zhang',
            'shi_chang_ren_yuan', 'zhu_li_2', 'zhu_li_3', 'zhu_li_4', 'chang_kong_1', 'chang_kong_2', 'chang_kong_3',
            'chang_kong_4', 'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', 'chang_zhang2_name', 'code_scaner'
        ]


class FenDianChoiceListSerializer(serializers.ModelSerializer):
    """
    店铺选择列表， id 和 name
    """

    # 重写name ，name + 平台店铺名
    name = serializers.SerializerMethodField(help_text='店铺名称', label='店铺名称', read_only=True)

    def get_name(self, obj):
        """
        店铺名称
        """
        name = obj.name
        if not name:
            name = '未知大G店铺名'
        platform_store_name = obj.platform_store_name
        if not platform_store_name:
            platform_store_name = '---'
        return f'{name}({platform_store_name})'

    class Meta:
        model = ShopSerialprefix
        fields = ['id', 'name']


class OrderScanCodeStatusChoiceListSerializer(serializers.ModelSerializer):
    """
    订单状态选择列表
    """
    value = serializers.IntegerField(source='id', read_only=True, help_text='状态id', label='状态id')
    label = serializers.CharField(source='name', read_only=True, help_text='状态名称', label='状态名称')

    class Meta:
        model = ItemStatus
        fields = ['value', 'label']


class ReserveDownloadOrderFlowSerializer(serializers.ModelSerializer):
    order_day = serializers.CharField(source='order.day', read_only=True, help_text='下单日期', label='下单日期')
    fen_dian_name = serializers.CharField(source='order.prefix.name', read_only=True, help_text='店铺名称', label='店铺名称', default='')
    category_name = serializers.CharField(source='order.category.name', read_only=True, help_text='货品', label='货品', default='')
    kickback = serializers.SerializerMethodField(help_text='扣点', label='扣点')
    should_pay_merchant = serializers.SerializerMethodField(help_text='应付商家', label='应付商家')
    shipper_name = serializers.CharField(source='order.shipper.name', read_only=True, help_text='货主', label='货主', default='')
    shipper_id = serializers.CharField(source='order.shipper.id', read_only=True, help_text='货主ID', label='货主ID', default='')
    zhubo_name = serializers.CharField(source='order.zhubo.first_name', read_only=True, help_text='主播', label='主播', default='')
    zhuli_name = serializers.CharField(source='order.play.zhuli1.first_name', read_only=True, help_text='助理', label='助理', default='')
    item_status_name = serializers.CharField(source='order.item_status.name', read_only=True, help_text='流程状态', label='流程状态', default='')
    taobao_tbno = serializers.SerializerMethodField(help_text='电商平台单号', label='电商平台单号')
    chang_zhang_name = serializers.CharField(source='order.play.changzhang.first_name', read_only=True, help_text='厂长', label='厂长', default='')
    zhibo_type_text = serializers.CharField(source='order.play.get_zhibo_type_display', read_only=True, help_text='直播方式', label='直播方式', default='')
    # 订单付款时间, 标题, 链接类型, 扫码时间
    taobao_order_pay_time = serializers.SerializerMethodField(read_only=True, help_text='订单付款时间', label='订单付款时间')
    link_type = serializers.SerializerMethodField(read_only=True, help_text='链接类型', label='链接类型')
    scan_code_time = serializers.CharField(read_only=True, help_text='扫码时间', label='扫码时间', source='created_time')
    ban_ci = serializers.SerializerMethodField(read_only=True, help_text='班次', label='班次')
    # 从班次长 到 客服4
    ban_ci_zhang = serializers.CharField(source='order.play.banzhang.first_name', read_only=True, help_text='班次长', label='班次长', default='')
    shi_chang_ren_yuan = serializers.CharField(source='order.play.shichangzhuanyuan.first_name', read_only=True, help_text='市场人员', label='市场人员', default='')
    # zhu_li_1 = serializers.CharField(source='play.zhuli1.first_name', read_only=True, help_text='助理1', label='助理1')
    zhu_li_2 = serializers.CharField(source='order.play.zhuli2.first_name', read_only=True, help_text='助理2', label='助理2', default='')
    zhu_li_3 = serializers.CharField(source='order.play.zhuli3.first_name', read_only=True, help_text='助理3', label='助理3', default='')
    zhu_li_4 = serializers.CharField(source='order.play.zhuli4.first_name', read_only=True, help_text='助理4', label='助理4', default='')
    chang_kong_1 = serializers.CharField(source='order.play.changkong.first_name', read_only=True, help_text='场控1', label='场控1', default='')
    chang_kong_2 = serializers.CharField(source='order.play.changkong1.first_name', read_only=True, help_text='场控2', label='场控2', default='')
    chang_kong_3 = serializers.CharField(source='order.play.changkong2.first_name', read_only=True, help_text='场控3', label='场控3', default='')
    chang_kong_4 = serializers.CharField(source='order.play.changkong3.first_name', read_only=True, help_text='场控4', label='场控4', default='')
    ke_fu_1 = serializers.CharField(source='order.play.kefu1.first_name', read_only=True, help_text='客服1', label='客服1', default='')
    ke_fu_2 = serializers.CharField(source='order.play.kefu2.first_name', read_only=True, help_text='客服2', label='客服2', default='')
    ke_fu_3 = serializers.CharField(source='order.play.kefu3.first_name', read_only=True, help_text='客服3', label='客服3', default='')
    ke_fu_4 = serializers.CharField(source='order.play.kefu4.first_name', read_only=True, help_text='客服4', label='客服4', default='')

    # order 的静态字段
    sn = serializers.CharField(source='order.sn', read_only=True, help_text='订单号', label='订单号')
    quantity = serializers.IntegerField(source='order.quantity', read_only=True, help_text='数量', label='数量')
    amount = serializers.FloatField(source='order.amount', read_only=True, help_text='金额', label='金额')
    finance_amount = serializers.FloatField(source='order.finance_amount', read_only=True, help_text='财务金额', label='财务金额')
    yunfei = serializers.FloatField(source='order.yunfei', read_only=True, help_text='运费', label='运费')
    yhq = serializers.FloatField(source='order.yhq', read_only=True, help_text='优惠券', label='优惠券')
    itemcode = serializers.CharField(source='order.itemcode', read_only=True, help_text='货品码', label='货品码')
    title = serializers.CharField(source='order.title', read_only=True, help_text='标题', label='标题')

    code_scaner = serializers.CharField(source='owner.first_name', read_only=True, help_text='扫码人', label='扫码人', default='')
    chang_zhang2_name = serializers.CharField(source='order.play.changzhang1.first_name', read_only=True, help_text='厂长2', label='厂长2', default='')

    def get_kickback(self, obj):
        """
        扣点, 根据店铺类型，判断货主的扣点
        """
        fen_dian_src = obj.order.prefix.src
        shop_shipper_obj = obj.order.shipper

        if not fen_dian_src:
            return '店铺类型为空'
        if not shop_shipper_obj:
            return '货主数据为空'
        # 淘宝
        if fen_dian_src == '1':
            return shop_shipper_obj.kickback

        # 抖音
        elif fen_dian_src == '2':
            return shop_shipper_obj.kickback_dy

        # 拼多多
        elif fen_dian_src == '3':
            return shop_shipper_obj.kickback_dd

        # 快手
        elif fen_dian_src == '5':
            return shop_shipper_obj.kickback_ks

        # tikto
        elif fen_dian_src == '8':
            return shop_shipper_obj.kickback_tikto

        # 视频号
        elif fen_dian_src == '9':
            return shop_shipper_obj.kickback_shipin

        # 小红书
        elif fen_dian_src == '10':
            return shop_shipper_obj.kickback_xhs

        else:
            return '店铺类型错误' + fen_dian_src

    def get_should_pay_merchant(self, obj):
        # 计算应付商家， 根据扣点计算
        kickback = self.get_kickback(obj)
        # 能否转为float
        try:
            kickback = float(kickback)
        except Exception as e:
            return '无'
        # 计算应付商家， 金额 * （1 - 扣点）   amount * (1 - kickback)
        if not obj.order.amount:
            return '无'
        return float(obj.order.amount) * (1 - kickback)

    def get_taobao_tbno(self, obj):
        """
        平台单号
        """
        # rel_qs = OrderTaobaoorderOrders.objects.filter(order=obj)
        # if not rel_qs:
        #     return '无'
        # tbno = ''
        # for rel_obj in rel_qs:
        #     try:
        #         tbno += rel_obj.taobaoorder.tbno + ' |'
        #     except Exception as e:
        #         continue
        # # 去掉最后的 ' |'
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'
        tbno = ''
        for taobao_obj in taobao_qs:
            tbno += taobao_obj.tbno + ', '
        # 去掉最后的 ', '
        return tbno[:-2]

    def get_link_type(self, obj):
        if obj.order.is_guding_url == 1:
            return '固定链接'
        elif obj.order.is_guding_url == 2:
            return '闪购链接'
        else:
            return '未识别'

    @staticmethod
    def get_taobao_order_qs(obj):
        """
        获取大G订单关联的淘宝订单 qs
        """
        rel_qs = obj.order.rel_to_taobao_order.all()
        if not rel_qs:
            return OrderTaobaoorder.objects.none()
        taobao_id_list = []
        for rel_obj in rel_qs:
            try:
                tao_bao_order_obj = rel_obj.taobaoorder
            except Exception as e:
                continue
            taobao_id_list.append(tao_bao_order_obj.id)
        return OrderTaobaoorder.objects.filter(id__in=taobao_id_list)

    def get_taobao_order_pay_time(self, obj):
        """
        获取订单付款时间
        """
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'

        pay_time = taobao_qs.first().tbpayed_time.strftime('%Y-%m-%d %H:%M:%S')

        return pay_time

    def to_representation(self, instance):
        """
        将日期时间格式化为 %Y-%m-%d %H:%M:%S
        @param instance:
        @return:
        """
        blank_fields = [
            '客户昵称', '成本金额', '成本导入时间', '代购费', '证书费', '绳子费', '盒子费', '其它', '多付金额', '附加扣款', '附加补款',
            '货主证书', '利润', '扣点调否', '调扣ID', '差异扣点', '售后金额', '备注', '录单员', '系统状态', '退款金额', '退款状态', '自动状态',
            '流程最近更新者', '订单更新时间', '订单创建时间', '支付方式', '交易截图', '标题货品码', '是否打印', '是否加帐',
            '证书', '发货记录', '货主备注', '场次ID', '班次时间', '拉新专员', '图片地址',
            '扫码历史', '品检状态', '品检类型', '品检备注', '品检人', '品检时间', '预售订单',
            '待结ID', '结扣ID', '结算ID'
        ]
        ret = super(ReserveDownloadOrderFlowSerializer, self).to_representation(instance)
        ret['扫码状态'] = instance.status.name
        for field in blank_fields:
            ret[field] = ''
        return ret

    def get_ban_ci(self, obj):
        return '无'

    class Meta:
        model = OrderFlow
        fields = [
            'order_day', 'fen_dian_name', 'sn', 'category_name', 'quantity', 'amount', 'finance_amount', 'yunfei',
            'kickback', 'should_pay_merchant', 'shipper_name', 'shipper_id', 'zhubo_name', 'zhuli_name',
            'item_status_name', 'taobao_tbno', 'yhq', 'itemcode', 'chang_zhang_name', 'zhibo_type_text',
            'title', 'taobao_order_pay_time', 'link_type', 'scan_code_time', 'ban_ci', 'ban_ci_zhang',
            'shi_chang_ren_yuan', 'zhu_li_2', 'zhu_li_3', 'zhu_li_4', 'chang_kong_1', 'chang_kong_2', 'chang_kong_3',
            'chang_kong_4', 'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', 'chang_zhang2_name', 'code_scaner'
        ]
