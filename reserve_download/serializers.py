from rest_framework import serializers

from commodity_category.models import ShopCategory
from order.models import ItemStatus, OrderTaobaoorder, OrderOrder, OrderFlow, QiDeBaoOrderInfo
from reserve_download.models import ReserveDownload
from shipper.models import ShopShipper
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
    created_time = serializers.DateTimeField(read_only=True, help_text='记录创建时间', label='创建时间', format='%Y-%m-%d %H:%M:%S')
    task_exec_start_time = serializers.DateTimeField(read_only=True, help_text='任务开始执行时间', label='任务开始执行时间', format='%Y-%m-%d %H:%M:%S')
    task_exec_end_time = serializers.DateTimeField(read_only=True, help_text='任务执行结束时间', label='任务执行结束时间', format='%Y-%m-%d %H:%M:%S')
    is_excel_mode = serializers.SerializerMethodField(read_only=True, help_text='是否Excel模式', label='是否Excel模式')

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

    def get_is_excel_mode(self, obj):
        """
        是否历史数据
        """
        return obj.filter_condition.get('is_excel', False)

    class Meta:
        model = ReserveDownload
        fields = ['id', 'creator_name', 'creator_id', 'created_time', 'filter_condition', 'fendian_info', 'task_status', 'task_exec_start_time',
                  'task_exec_end_time', 'data_count', 'file_url', 'fen_dian_name_text', 'is_excel_mode',
                  'task_status_text', 'task_celery_id', 'task_result', 'file_name', 'is_success', 'tag', 'can_download']


class ReserveDownloadOrderSerializer(serializers.ModelSerializer):
    """
    导出订单
    """
    order_day = serializers.CharField(source='day', read_only=True, help_text='下单日期', label='下单日期')
    fen_dian_name = serializers.CharField(source='prefix.name', read_only=True, help_text='店铺名称', label='店铺名称', default='')
    category_name = serializers.SerializerMethodField(help_text='货品', label='货品', read_only=True)
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

    total_paid = serializers.SerializerMethodField(read_only=True, help_text='实付金额，所有平台订单的 p_amount 之和', label='实付金额')
    # 24-04-25 新增
    """ 扫码历史, 品检状态, 代购费, 证书费, 绳子费, 盒子费, 其它费用, 多付金额, 图片地址, 备注, 自动状态, 订单创建时间, 证书, 发货记录, 货主备注, 场次ID, 班次时间, 是否打印,
        流程最近更新者, 预售订单, 系统状态, 退款状态, 品检类型, 品检备注, 品检人, 品检时间, 交易截图,  成本金额, 附加扣款, 附加补款, 调扣ID, 退款金额, 订单更新时间, 是否加帐
        分类一级、分类二级、分类三级、分类四级、最晚发货时间"""
    scan_code_history = serializers.SerializerMethodField(read_only=True, help_text='扫码历史, 最新的一条 order_flow_obj ', label='扫码历史')
    scan_code_status = serializers.SerializerMethodField(read_only=True, help_text='扫码状态, 当前的状态名 ', label='扫码状态')
    check_good_status = serializers.CharField(source='get_is_checkgoods_display', read_only=True, help_text='品检状态', label='品检状态', default='')
    dai_gou_fee = serializers.FloatField(source='fee', read_only=True, help_text='代购费', label='代购费', default=0)
    zheng_shu_fee = serializers.FloatField(source='certificate', read_only=True, help_text='证书费', label='证书费', default=0)
    sheng_zi_fee = serializers.FloatField(source='shengzi', read_only=True, help_text='绳子费', label='绳子费', default=0)
    he_zi_fee = serializers.FloatField(source='box', read_only=True, help_text='盒子费', label='盒子费', default=0)
    other_fee = serializers.FloatField(source='other', read_only=True, help_text='其它', label='其它', default=0)
    duo_fu_jin_e = serializers.FloatField(source='overage', read_only=True, help_text='多付金额', label='多付金额', default=0)
    goods_image_url = serializers.SerializerMethodField(read_only=True, help_text='商品图片地址', label='图片地址')
    desc = serializers.CharField(read_only=True, help_text='备注', label='备注', default='')
    auto_status_text = serializers.SerializerMethodField(read_only=True, help_text='自动状态', label='自动状态')
    order_create_time = serializers.DateTimeField(source='created_time', read_only=True, help_text='订单创建时间', label='订单创建时间', format='%Y-%m-%d %H:%M:%S')
    zheng_shu = serializers.SerializerMethodField(read_only=True, help_text='证书', label='证书')
    fa_huo_ji_lu = serializers.SerializerMethodField(read_only=True, help_text='发货记录', label='发货记录')
    shipper_memo = serializers.CharField(read_only=True, help_text='货主备注', label='货主备注', default='')
    chang_ci_id = serializers.IntegerField(source='play_id', read_only=True, help_text='场次ID', label='场次ID', default='')
    ban_ci_time = serializers.SerializerMethodField(read_only=True, help_text='班次时间', label='班次时间')
    is_print = serializers.SerializerMethodField(read_only=True, help_text='是否打印', label='是否打印')
    flow_newest_updater = serializers.SerializerMethodField(read_only=True, help_text='流程最近更新者', label='流程最近更新者')
    is_presale_order = serializers.SerializerMethodField(read_only=True, help_text='预售订单', label='预售订单')
    system_status = serializers.SerializerMethodField(read_only=True, help_text='系统状态', label='系统状态')
    refund_status = serializers.SerializerMethodField(read_only=True, help_text='退款状态', label='退款状态')
    check_good_category = serializers.SerializerMethodField(read_only=True, help_text='品检类型', label='品检类型')
    checkgoods_desc = serializers.CharField(read_only=True, help_text='品检备注', label='品检备注', default='')
    checkgoods_checker = serializers.CharField(source='checkgoods_creator.first_name', read_only=True, help_text='品检人', label='品检人', default='')
    checkgoods_time = serializers.DateTimeField(source='checkgoods_created_time', read_only=True, help_text='品检时间', label='品检时间', format='%Y-%m-%d %H:%M:%S')
    trade_screenshot = serializers.SerializerMethodField(read_only=True, help_text='交易截图', label='交易截图')
    cost_amount = serializers.FloatField(source='costamount', read_only=True, help_text='成本金额', label='成本金额', default=0)
    additional_deduction = serializers.FloatField(source='addlamount1', read_only=True, help_text='附加扣款', label='附加扣款', default=0)
    additional_payment = serializers.FloatField(source='addlamount2', read_only=True, help_text='附加补款', label='附加补款', default=0)
    deduction_id = serializers.IntegerField(source='activitykick_id', read_only=True, help_text='调扣ID', label='调扣ID', default=0)
    refund_amount = serializers.FloatField(source='refund_fee', read_only=True, help_text='退款金额', label='退款金额', default=0)
    order_update_time = serializers.DateTimeField(source='last_modified', read_only=True, help_text='订单更新时间', label='订单更新时间', format='%Y-%m-%d %H:%M:%S')
    is_add_account = serializers.SerializerMethodField(read_only=True, help_text='是否加帐', label='是否加帐')
    category_level_1 = serializers.SerializerMethodField(read_only=True, help_text='分类一级', label='分类一级')
    category_level_2 = serializers.SerializerMethodField(read_only=True, help_text='分类二级', label='分类二级')
    category_level_3 = serializers.SerializerMethodField(read_only=True, help_text='分类三级', label='分类三级')
    category_level_4 = serializers.SerializerMethodField(read_only=True, help_text='分类四级', label='分类四级')
    delivery_time_dead_line = serializers.DateTimeField(source='latestdeliverytime', read_only=True, help_text='最晚发货时间', label='最晚发货时间',
                                                        default=None, format='%Y-%m-%d %H:%M:%S')

    def get_category_name(self, obj):
        category_obj = obj.category
        if not category_obj:
            return '未知'
        category_family = category_obj.get_my_family()
        if not category_family:
            return category_obj.name
        name = ''
        for item in category_family:
            name += item.name + '->'
        return name[:-2]

    def get_scan_code_history(self, obj):
        order_flow_obj = self.get_newest_order_flow_obj(obj)
        try:
            if not order_flow_obj:
                return '无'
            if not order_flow_obj.old_status:
                return '无'
            return order_flow_obj.old_status.name
        except Exception as e:
            return '无'

    def get_scan_code_status(self, obj):
        order_flow_obj = self.get_newest_order_flow_obj(obj)
        if not order_flow_obj:
            return '无'
        return order_flow_obj.status.name

    def get_goods_image_url(self, obj):
        qi_de_bao_order_obj = QiDeBaoOrderInfo.objects.filter(order=obj).first()
        if not qi_de_bao_order_obj:
            return '无'
        return qi_de_bao_order_obj.picurl or '无'

    def get_auto_status_text(self, obj):
        auto_status = obj.autostatus
        map_dict = {
            '1': '暂未同步',
            '2': '订单退款',
            '3': '交易成功',
            '4': '退款创建',
            '5': '退款关闭',
            '7': '订单发货',
            '8': '交易关闭',
            '9': '等待发货',
            '10': '等待付款',
            '11': '部分退款',
            '12': '新增订单',
            '13': '订单未退',
        }
        return map_dict.get(auto_status, '未知')

    def get_zheng_shu(self, obj):
        """
        证书
        :param obj:
        :return:
        """
        if obj.is_zhengshu == 1:
            return '有证书'
        elif obj.is_zhengshu == 0:
            return '无证书'

    def get_fa_huo_ji_lu(self, obj):
        """
        发货记录
        :param obj:
        :return:
        """
        iem_satus_obj = obj.item_status
        if not iem_satus_obj:
            return '未知'
        sendgoodstype = iem_satus_obj.sendgoodstype
        if sendgoodstype == 1:
            return '已发货'
        elif sendgoodstype == 0:
            return '未发货'
        else:
            return '无记录'

    def get_ban_ci_time(self, obj):
        live_play_obj = obj.play
        if not live_play_obj:
            return '未知'
        live_shift_schedule_obj = live_play_obj.classs
        if not live_shift_schedule_obj:
            return '未知'
        start_time = live_shift_schedule_obj.start_time
        end_time = live_shift_schedule_obj.end_time
        if not start_time or not end_time:
            return '未知'
        return f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"

    def get_is_print(self, obj):
        printstatus = obj.printstatus
        if printstatus:
            return '已打印'
        else:
            return '未打印'

    def get_flow_newest_updater(self, obj):
        order_flow_obj = self.get_newest_order_flow_obj(obj)
        if not order_flow_obj:
            return '无'
        owner = order_flow_obj.owner
        if not owner:
            return '无'
        return owner.first_name

    def get_is_presale_order(self, obj):
        if obj.is_presale:
            return '预售'
        else:
            return '非预售'

    def get_system_status(self, obj):
        system_status = obj.status
        if not system_status:
            return '未知'
        map_dict = {
            '0': '已删除',
            '1': '待核对',
            '2': '已核对',
            '3': '核对有误',
            '4': '人工已核对',
            '5': '系统已核对',
            '6': '财务已核对',
        }
        return map_dict.get(system_status, '未知')

    def get_refund_status(self, obj):
        auto_status = obj.autostatus
        if auto_status == '2':
            return '已退款'
        elif auto_status == '11':
            return '部分退款'
        else:
            return '未退款'

    def get_check_good_category(self, obj):
        check_good_type_dict_obj = obj.checkgoodstype
        if not check_good_type_dict_obj:
            return '未知'
        if check_good_type_dict_obj.parent.id != 32:
            return '未知'
        return check_good_type_dict_obj.label or '无'

    def get_trade_screenshot(self, obj):
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'
        img_url = None
        for taobao_obj in taobao_qs:
            if taobao_obj.img_list:
                img_url = taobao_obj.img_list
                break
        if not img_url:
            return '无'
        return img_url

    def get_is_add_account(self, obj):
        live_play_obj = obj.play
        if not live_play_obj:
            return '未知'
        if live_play_obj.is_add >=1:
            return '正常'
        else:
            return '加账'

    def get_category_level_1(self, obj):
        category_obj = obj.category
        if not category_obj:
            return '未知'
        if category_obj.level == 1:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 1:
                    name = item.name
                    break
            return name

    def get_category_level_2(self, obj):
        category_obj = obj.category
        if not category_obj:
            return '未知'
        if category_obj.level == 2:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 2:
                    name = item.name
                    break
            return name

    def get_category_level_3(self, obj):
        category_obj = obj.category
        if not category_obj:
            return '未知'
        if category_obj.level == 3:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 3:
                    name = item.name
                    break
            return name

    def get_category_level_4(self, obj):
        category_obj = obj.category
        if not category_obj:
            return '未知'
        if category_obj.level == 4:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 4:
                    name = item.name
                    break
            return name

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
        # 计算应付商家， 金额 * （1 - 扣点）   amount * (1 - kickback) 保留两位小数
        if not obj.amount:
            return '无'
        return round(float(obj.amount) * (1 - kickback), 2)

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

    @staticmethod
    def get_newest_order_flow_obj(obj):
        # newest_order_flow_obj_id = obj.orderflow_id
        # if not newest_order_flow_obj_id:
        #     return OrderFlow.objects.none()
        order_flow_obj = OrderFlow.objects.filter(order_id=obj.id).order_by('-created_time').first()
        if not order_flow_obj:
            return OrderFlow.objects.none()
        return order_flow_obj

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
            '拉新专员', '杂项支出', '销售专员', '转粉专员', '关联店铺', '支付方式', '货主证书', '利润', '扣点调否', '差异扣点', '售后金额',
            '待结ID', '结扣ID', '结算ID', '成本导入时间', '录单员', '标题货品码', '客户昵称',
        ]
        ret = super(ReserveDownloadOrderSerializer, self).to_representation(instance)
        for field in blank_fields:
            ret[field] = '暂无'
        return ret

    def get_scan_code_time(self, obj):
        """
        扫码时间
        """
        # order_flow_obj = OrderFlow.objects.filter(order=obj).order_by('-created_time').first()
        # newest_order_flow_obj_id = obj.orderflow_id
        # if not newest_order_flow_obj_id:
        #     return '无'

        order_flow_obj = self.get_newest_order_flow_obj(obj)
        if not order_flow_obj:
            return '无'
        return order_flow_obj.created_time.strftime('%Y-%m-%d %H:%M:%S')

    def get_code_scaner(self, obj):
        order_flow_obj = obj.scan_code_flows.all().order_by('-created_time').first()
        if not order_flow_obj:
            return '无'
        return order_flow_obj.owner.first_name

    def get_ban_ci(self, obj):
        live_play_obj = obj.play
        if not live_play_obj:
            return '未知'
        live_shift_schedule_obj = live_play_obj.classs
        if not live_shift_schedule_obj:
            return '未知'
        map_dict = {
            1: '早班',
            2: '中班',
            3: '晚班',
            4: '夜班',
        }
        class_tag = live_shift_schedule_obj.classtag
        if class_tag not in map_dict:
            return '未知'
        return map_dict.get(class_tag, '未知')

    def get_total_paid(self, obj):
        """
        实付金额
        :param obj:
        :return:
        """
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'
        total_paid = 0
        for taobao_obj in taobao_qs:
            total_paid += taobao_obj.p_amount
        return total_paid

    class Meta:
        model = OrderOrder
        fields = [
            'order_day', 'fen_dian_name', 'sn', 'category_name', 'quantity', 'amount', 'finance_amount', 'yunfei',
            'kickback', 'should_pay_merchant', 'shipper_name', 'shipper_id', 'zhubo_name', 'zhuli_name',
            'item_status_name', 'taobao_tbno', 'yhq', 'itemcode', 'chang_zhang_name', 'zhibo_type_text',
            'title', 'taobao_order_pay_time', 'link_type', 'scan_code_time', 'ban_ci', 'ban_ci_zhang',
            'shi_chang_ren_yuan', 'zhu_li_2', 'zhu_li_3', 'zhu_li_4', 'chang_kong_1', 'chang_kong_2', 'chang_kong_3',
            'chang_kong_4', 'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', 'chang_zhang2_name', 'code_scaner', 'total_paid',
            'scan_code_history', 'scan_code_status', 'check_good_status', 'dai_gou_fee', 'zheng_shu_fee', 'sheng_zi_fee', 'he_zi_fee',
            'other_fee', 'duo_fu_jin_e', 'goods_image_url', 'desc', 'auto_status_text', 'order_create_time', 'zheng_shu',
            'fa_huo_ji_lu', 'shipper_memo', 'chang_ci_id', 'ban_ci_time', 'is_print', 'flow_newest_updater',
            'is_presale_order', 'system_status', 'refund_status', 'check_good_category', 'checkgoods_desc',
            'checkgoods_checker', 'checkgoods_time', 'trade_screenshot', 'cost_amount', 'additional_deduction',
            'additional_payment', 'deduction_id', 'refund_amount', 'order_update_time', 'is_add_account',
            'category_level_1', 'category_level_2', 'category_level_3', 'category_level_4', 'delivery_time_dead_line',
            'desc_shz_gj'
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
    """
    导出订单 - 历史状态
    以 OrderFlow 为核心
    """
    order_day = serializers.CharField(source='order.day', read_only=True, help_text='下单日期', label='下单日期')
    fen_dian_name = serializers.CharField(source='order.prefix.name', read_only=True, help_text='店铺名称', label='店铺名称', default='')
    category_name = serializers.SerializerMethodField(help_text='货品', label='货品', read_only=True)
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

    total_paid = serializers.SerializerMethodField(read_only=True, help_text='实付金额，所有平台订单的 p_amount 之和', label='实付金额')
    # 24-04-25 新增
    """ 扫码历史, 品检状态, 代购费, 证书费, 绳子费, 盒子费, 其它费用, 多付金额, 图片地址, 备注, 自动状态, 订单创建时间, 证书, 发货记录, 货主备注, 场次ID, 班次时间, 是否打印,
        流程最近更新者, 预售订单, 系统状态, 退款状态, 品检类型, 品检备注, 品检人, 品检时间, 交易截图,  成本金额, 附加扣款, 附加补款, 调扣ID, 退款金额, 订单更新时间, 是否加帐
        分类一级、分类二级、分类三级、分类四级、最晚发货时间"""
    scan_code_history = serializers.CharField(source='old_status.name', read_only=True, help_text='扫码历史, 上一条状态 ', label='扫码历史', default='无')
    scan_code_status = serializers.CharField(source='status.name', read_only=True, help_text='扫码状态, 当前的状态名 ', label='扫码状态')
    check_good_status = serializers.CharField(source='order.get_is_checkgoods_display', read_only=True, help_text='品检状态', label='品检状态', default='')
    dai_gou_fee = serializers.FloatField(source='order.fee', read_only=True, help_text='代购费', label='代购费', default=0)
    zheng_shu_fee = serializers.FloatField(source='order.certificate', read_only=True, help_text='证书费', label='证书费', default=0)
    sheng_zi_fee = serializers.FloatField(source='order.shengzi', read_only=True, help_text='绳子费', label='绳子费', default=0)
    he_zi_fee = serializers.FloatField(source='order.box', read_only=True, help_text='盒子费', label='盒子费', default=0)
    other_fee = serializers.FloatField(source='order.other', read_only=True, help_text='其它', label='其它', default=0)
    duo_fu_jin_e = serializers.FloatField(source='order.overage', read_only=True, help_text='多付金额', label='多付金额', default=0)
    goods_image_url = serializers.SerializerMethodField(read_only=True, help_text='商品图片地址', label='图片地址')
    desc = serializers.CharField(read_only=True, help_text='备注', label='备注', default='')
    auto_status_text = serializers.SerializerMethodField(read_only=True, help_text='自动状态', label='自动状态')
    order_create_time = serializers.DateTimeField(source='order.created_time', read_only=True, help_text='订单创建时间', label='订单创建时间',
                                                  format='%Y-%m-%d %H:%M:%S')
    zheng_shu = serializers.SerializerMethodField(read_only=True, help_text='证书', label='证书')
    fa_huo_ji_lu = serializers.SerializerMethodField(read_only=True, help_text='证书', label='证书')
    shipper_memo = serializers.CharField(read_only=True, help_text='货主备注', label='货主备注', default='')
    chang_ci_id = serializers.IntegerField(source='order.play_id', read_only=True, help_text='场次ID', label='场次ID', default='')
    ban_ci_time = serializers.SerializerMethodField(read_only=True, help_text='班次时间', label='班次时间')
    is_print = serializers.SerializerMethodField(read_only=True, help_text='是否打印', label='是否打印')
    flow_newest_updater = serializers.CharField(read_only=True, source='owner.first_name', help_text='流程最近更新者', label='流程最近更新者')
    is_presale_order = serializers.SerializerMethodField(read_only=True, help_text='预售订单', label='预售订单')
    system_status = serializers.SerializerMethodField(read_only=True, help_text='系统状态', label='系统状态')
    refund_status = serializers.SerializerMethodField(read_only=True, help_text='退款状态', label='退款状态')
    check_good_category = serializers.SerializerMethodField(read_only=True, help_text='品检类型', label='品检类型')
    checkgoods_desc = serializers.CharField(read_only=True, help_text='品检备注', label='品检备注', default='')
    checkgoods_checker = serializers.CharField(source='order.checkgoods_creator.first_name', read_only=True, help_text='品检人', label='品检人', default='')
    checkgoods_time = serializers.DateTimeField(source='order.checkgoods_created_time', read_only=True, help_text='品检时间', label='品检时间',
                                                format='%Y-%m-%d %H:%M:%S')
    trade_screenshot = serializers.SerializerMethodField(read_only=True, help_text='交易截图', label='交易截图')
    cost_amount = serializers.FloatField(source='order.costamount', read_only=True, help_text='成本金额', label='成本金额', default=0)
    additional_deduction = serializers.FloatField(source='order.addlamount1', read_only=True, help_text='附加扣款', label='附加扣款', default=0)
    additional_payment = serializers.FloatField(source='order.addlamount2', read_only=True, help_text='附加补款', label='附加补款', default=0)
    deduction_id = serializers.IntegerField(source='order.activitykick_id', read_only=True, help_text='调扣ID', label='调扣ID', default=0)
    refund_amount = serializers.FloatField(source='order.refund_fee', read_only=True, help_text='退款金额', label='退款金额', default=0)
    order_update_time = serializers.DateTimeField(source='order.last_modified', read_only=True, help_text='订单更新时间', label='订单更新时间',
                                                  format='%Y-%m-%d %H:%M:%S')
    is_add_account = serializers.SerializerMethodField(read_only=True, help_text='是否加帐', label='是否加帐')
    category_level_1 = serializers.SerializerMethodField(read_only=True, help_text='分类一级', label='分类一级')
    category_level_2 = serializers.SerializerMethodField(read_only=True, help_text='分类二级', label='分类二级')
    category_level_3 = serializers.SerializerMethodField(read_only=True, help_text='分类三级', label='分类三级')
    category_level_4 = serializers.SerializerMethodField(read_only=True, help_text='分类四级', label='分类四级')
    delivery_time_dead_line = serializers.DateTimeField(source='order.latestdeliverytime', read_only=True, help_text='最晚发货时间', label='最晚发货时间',
                                                        default=None, format='%Y-%m-%d %H:%M:%S')
    desc_shz_gj = serializers.CharField(source='order.desc_shz_gj', read_only=True, help_text='收货组跟进', label='收货组跟进', default='')

    def get_goods_image_url(self, obj):
        qi_de_bao_order_obj = QiDeBaoOrderInfo.objects.filter(order=obj.order).first()
        if not qi_de_bao_order_obj:
            return '无'
        return qi_de_bao_order_obj.picurl or '无'

    def get_auto_status_text(self, obj):
        auto_status = obj.order.autostatus
        map_dict = {
            '1': '暂未同步',
            '2': '订单退款',
            '3': '交易成功',
            '4': '退款创建',
            '5': '退款关闭',
            '7': '订单发货',
            '8': '交易关闭',
            '9': '等待发货',
            '10': '等待付款',
            '11': '部分退款',
            '12': '新增订单',
            '13': '订单未退',
        }
        return map_dict.get(auto_status, '未知')

    def get_zheng_shu(self, obj):
        """
        证书
        :param obj:
        :return:
        """
        if obj.order.is_zhengshu == 1:
            return '有证书'
        elif obj.order.is_zhengshu == 0:
            return '无证书'

    def get_fa_huo_ji_lu(self, obj):
        """
        发货记录
        :param obj:
        :return:
        """
        iem_satus_obj = obj.order.item_status
        if not iem_satus_obj:
            return '未知'
        sendgoodstype = iem_satus_obj.sendgoodstype
        if sendgoodstype == 1:
            return '已发货'
        elif sendgoodstype == 0:
            return '未发货'
        else:
            return '无记录'

    def get_ban_ci_time(self, obj):
        live_play_obj = obj.order.play
        if not live_play_obj:
            return '未知'
        live_shift_schedule_obj = live_play_obj.classs
        if not live_shift_schedule_obj:
            return '未知'
        start_time = live_shift_schedule_obj.start_time
        end_time = live_shift_schedule_obj.end_time
        if not start_time or not end_time:
            return '未知'
        return f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"

    def get_is_print(self, obj):
        printstatus = obj.order.printstatus
        if printstatus:
            return '已打印'
        else:
            return '未打印'

    # def get_flow_newest_updater(self, obj):
    #     order_flow_obj = self.get_newest_order_flow_obj(obj)
    #     if not order_flow_obj:
    #         return '无'
    #     owner = order_flow_obj.owner
    #     if not owner:
    #         return '无'
    #     return owner.first_name

    def get_is_presale_order(self, obj):
        if obj.order.is_presale:
            return '预售'
        else:
            return '非预售'

    def get_system_status(self, obj):
        system_status = obj.order.status
        if not system_status:
            return '未知'
        map_dict = {
            '0': '已删除',
            '1': '待核对',
            '2': '已核对',
            '3': '核对有误',
            '4': '人工已核对',
            '5': '系统已核对',
            '6': '财务已核对',
        }
        return map_dict.get(system_status, '未知')

    def get_refund_status(self, obj):
        auto_status = obj.order.autostatus
        if auto_status == '2':
            return '已退款'
        elif auto_status == '11':
            return '部分退款'
        else:
            return '未退款'

    def get_check_good_category(self, obj):
        check_good_type_dict_obj = obj.order.checkgoodstype
        if not check_good_type_dict_obj:
            return '未知'
        if check_good_type_dict_obj.parent.id != 32:
            return '未知'
        return check_good_type_dict_obj.label or '无'

    def get_trade_screenshot(self, obj):
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'
        img_url = None
        for taobao_obj in taobao_qs:
            if taobao_obj.img_list:
                img_url = taobao_obj.img_list
                break
        if not img_url:
            return '无'
        return img_url

    def get_is_add_account(self, obj):
        live_play_obj = obj.order.play
        if not live_play_obj:
            return '未知'
        if live_play_obj.is_add >= 1:
            return '正常'
        else:
            return '加账'

    def get_category_level_1(self, obj):
        category_obj = obj.order.category
        if not category_obj:
            return '未知'
        if category_obj.level == 1:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 1:
                    name = item.name
                    break
            return name

    def get_category_level_2(self, obj):
        category_obj = obj.order.category
        if not category_obj:
            return '未知'
        if category_obj.level == 2:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 2:
                    name = item.name
                    break
            return name

    def get_category_level_3(self, obj):
        category_obj = obj.order.category
        if not category_obj:
            return '未知'
        if category_obj.level == 3:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 3:
                    name = item.name
                    break
            return name

    def get_category_level_4(self, obj):
        category_obj = obj.order.category
        if not category_obj:
            return '未知'
        if category_obj.level == 4:
            return category_obj.name
        else:
            name = None
            category_family = category_obj.get_my_family()
            if not category_family:
                return '未知'
            for item in category_family:
                if item.level == 4:
                    name = item.name
                    break
            return name
    ##### ---

    def get_category_name(self, obj):
        category_obj = obj.order.category
        if not category_obj:
            return '未知'
        category_family = category_obj.get_my_family()
        if not category_family:
            return category_obj.name
        name = ''
        for item in category_family:
            name += item.name + '->'
        return name[:-2]

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
        return round(float(obj.order.amount) * (1 - kickback), 2)

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
            '拉新专员', '杂项支出', '销售专员', '转粉专员', '关联店铺', '支付方式', '货主证书', '利润', '扣点调否', '差异扣点', '售后金额',
            '待结ID', '结扣ID', '结算ID', '成本导入时间', '录单员', '标题货品码', '客户昵称',
        ]
        ret = super(ReserveDownloadOrderFlowSerializer, self).to_representation(instance)
        # ret['扫码状态'] = instance.status.name
        for field in blank_fields:
            ret[field] = '暂无'
        return ret

    def get_ban_ci(self, obj):
        return '无'

    def get_total_paid(self, obj):
        """
        实付金额
        :param obj:
        :return:
        """
        taobao_qs = self.get_taobao_order_qs(obj)
        if not taobao_qs:
            return '无'
        total_paid = 0
        for taobao_obj in taobao_qs:
            total_paid += taobao_obj.p_amount
        return total_paid

    class Meta:
        model = OrderFlow
        fields = [
            'order_day', 'fen_dian_name', 'sn', 'category_name', 'quantity', 'amount', 'finance_amount', 'yunfei',
            'kickback', 'should_pay_merchant', 'shipper_name', 'shipper_id', 'zhubo_name', 'zhuli_name',
            'item_status_name', 'taobao_tbno', 'yhq', 'itemcode', 'chang_zhang_name', 'zhibo_type_text',
            'title', 'taobao_order_pay_time', 'link_type', 'scan_code_time', 'ban_ci', 'ban_ci_zhang',
            'shi_chang_ren_yuan', 'zhu_li_2', 'zhu_li_3', 'zhu_li_4', 'chang_kong_1', 'chang_kong_2', 'chang_kong_3',
            'chang_kong_4', 'ke_fu_1', 'ke_fu_2', 'ke_fu_3', 'ke_fu_4', 'chang_zhang2_name', 'code_scaner', 'total_paid',
            'scan_code_history', 'scan_code_status', 'check_good_status', 'dai_gou_fee', 'zheng_shu_fee', 'sheng_zi_fee', 'he_zi_fee',
            'other_fee', 'duo_fu_jin_e', 'goods_image_url', 'desc', 'auto_status_text', 'order_create_time', 'zheng_shu',
            'fa_huo_ji_lu', 'shipper_memo', 'chang_ci_id', 'ban_ci_time', 'is_print', 'flow_newest_updater',
            'is_presale_order', 'system_status', 'refund_status', 'check_good_category', 'checkgoods_desc',
            'checkgoods_checker', 'checkgoods_time', 'trade_screenshot', 'cost_amount', 'additional_deduction',
            'additional_payment', 'deduction_id', 'refund_amount', 'order_update_time', 'is_add_account',
            'category_level_1', 'category_level_2', 'category_level_3', 'category_level_4', 'delivery_time_dead_line',
            'desc_shz_gj'
        ]


class ShopShipperChoiceListSerializer(serializers.ModelSerializer):
    """
    小货主下拉列表，
    id 和 name
    """
    class Meta:
        model = ShopShipper
        fields = ['id', 'name']


class ZhuboChoiceListSerializer(serializers.ModelSerializer):
    """
    主播下拉列表，
    id 和 name
    """
    name = serializers.SerializerMethodField(read_only=True, help_text='主播名称', label='主播名称')

    def get_name(self, obj):
        nick_name = obj.first_name or '无姓名'
        stage_name = obj.notes or '无艺名'
        name = nick_name + '(' + stage_name + ')'
        return name

    class Meta:
        model = AccountMyuser
        fields = ['id', 'name']


class UserFirstNameChoiceListSerializer(serializers.ModelSerializer):
    """
    普通用户下拉列表
    """
    name = serializers.CharField(source='first_name', read_only=True, help_text='市场专员/厂长名称', label='市场专员名称')

    class Meta:
        model = AccountMyuser
        fields = ['id', 'name']
