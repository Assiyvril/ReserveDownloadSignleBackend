from django.db import models

from commodity_category.models import ShopCategory
from shop.models import ShopDepartment
from user.models import AccountMyuser


class MainShipper(models.Model):
    shop_id = models.IntegerField(verbose_name=u'所属商户ID', default=2)
    department = models.ForeignKey(ShopDepartment, verbose_name=u'所属部门',
                                   related_name='main_shipper', null=True,
                                   blank=True, on_delete=models.PROTECT)
    # avatar = ProcessedImageField(upload_to=uuid_file_path, null=True,
    #                              blank=True, verbose_name=u'货主头像',
    #                              format='JPEG',
    #                              options={'quality': settings.IMAGE_QUANLITY},
    #                              help_text=u'建议大小为300x300')
    avatar = models.TextField(u'货主头像', null=True, blank=True,
                              help_text=u'建议大小为300x300')
    name = models.CharField(u'货主名称', max_length=255,
                            help_text=u'在APP中录单的时候可以看到的货主名')
    zone = models.CharField(u'所在地区', max_length=255, null=True, blank=True,
                            help_text=u'建议写上所在市/县，例如 揭阳、四会等')
    contact = models.CharField(u'联系人', max_length=255, null=True,
                               blank=True,
                               help_text=u'联系信息只在后台记录，APP端不会看到')
    phone = models.CharField(u'手机号', max_length=255, null=True, blank=True)
    payee = models.CharField(u'收款人', max_length=255, null=True, blank=True)
    bankname = models.CharField(u'开户行', max_length=255, null=True,
                                blank=True)
    bankcode = models.CharField(u'银行卡', max_length=255, null=True,
                                blank=True)
    is_active = models.BooleanField(u'是否生效', default=True,
                                    help_text=u'无效的货主不会在APP中显示')
    openid = models.CharField(u'openid', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = u'货主'
        verbose_name_plural = u'货主'
        db_table = 'shop_mainshipper'


SCORE_STARS = (
    (0, u''),
    (1, u'☆'),
    (2, u'☆☆'),
    (3, u'☆☆☆'),
    (4, u'☆☆☆☆'),
    (5, u'☆☆☆☆☆'),
)

S_DEPARTMENT = (
    (0, u'无部门'),
    (1, u'产品部'),
    (2, u'供应链'),
    (3, u'丝巾部'),
    (4, u'市场部'),
    # (5, u'标品部'),
    # (6, u'翠境项目'),
    # (7, u'金马项目'),
    # (8, u'翡翠毛货项目'),
    # (9, u'周干妈项目'),
    # (10, u'钻石工厂项目'),
    # (11, u'晶石项目'),
    # (12, u'平洲工厂'),
    # (13, u'彩宝项目'),
    # (14, u'珍珠项目'),
)


class ShopShipper(models.Model):
    """
        小货主 / 子货主
        """
    # 基本信息 名称、所属部门、归属部门、关联大货主、头像、停播日期、停播天数、关联市场专员、
    # 是否生效、是否分享、是否次日结、是否引流、是否下线、非引流ID、标签
    name = models.CharField(u'货主名称', max_length=31, help_text=u'在APP中录单的时候可以看到的货主名')
    department = models.ForeignKey(
        ShopDepartment, verbose_name=u'所属部门', related_name='shipper', null=True, blank=True, on_delete=models.PROTECT
    )
    shipper_department = models.PositiveSmallIntegerField(u'归属部门', choices=S_DEPARTMENT, default=0, null=True)
    mainshipper = models.ForeignKey(MainShipper, verbose_name=u'所属货主', related_name='mainshipper', null=True, blank=True,
                                    on_delete=models.PROTECT)
    """
    为了兼容原有数据，avatar 其实是货主的身份证照片，所以新建一个 logo 字段作为头像照片
    """
    avatar = models.TextField(null=True, blank=True, verbose_name=u'货主身份证图片链接')
    logo = models.TextField(null=True, blank=True, verbose_name=u'货主头像图片链接')

    stop_day = models.DateField(u'停播日期', null=True, blank=True)
    day_count = models.PositiveIntegerField(u'停播天数', null=True, default=0, blank=True)
    # TODO 这里改成了 AccountMyuser，需要提醒大哥
    marketmaster = models.ForeignKey(
        AccountMyuser, related_name='shipper_marketmaster', verbose_name=u'关联拉新专员', null=True, blank=True, on_delete=models.PROTECT
    )
    is_active = models.BooleanField(u'是否生效', default=True, help_text=u'无效的货主不会在APP中显示')
    is_share = models.BooleanField(u'是否分享', default=False, help_text=u'是否分享该货主数据')
    is_nextdayend = models.BooleanField(u'是否次日结', default=False, help_text=u'勾选则具备次日结算订单权限')
    is_yingliu = models.BooleanField(u'是否引流号', default=False)
    is_down = models.BooleanField(u'是否下线', default=False, help_text=u'下线以后不可再排班。但可以查看数据')
    shipper_id = models.PositiveIntegerField(u'非引流ID', null=True, blank=True)
    other_name = models.CharField(u'货主标签', null=True, blank=True, max_length=5)

    # 其他信息：所在地区、联系人、联系人手机号、排序、对应货品分类（多选）、备注
    zone = models.CharField(u'所在地区', max_length=31, null=True, blank=True, help_text=u'建议写上所在市/县，例如 揭阳、四会等')
    contact = models.CharField(u'联系人', max_length=31, null=True, blank=True, help_text=u'联系信息只在后台记录，APP端不会看到')
    phone = models.CharField(u'手机号', max_length=31, null=True, blank=True)
    order = models.PositiveIntegerField(u'排序', default=200, help_text=u'从小到大显示')
    categories = models.ManyToManyField(ShopCategory, verbose_name=u'产品分类', blank=True, related_name='shippers')
    notes = models.TextField(u'备注', null=True, blank=True, help_text=u'仅管理员可见')

    # 价格范围： 价格范围1、价格范围2
    price1 = models.PositiveIntegerField(u'价格范围1', default=0, help_text=u'类型为整数，表示价格范围的下限，用于搜索')
    price2 = models.PositiveIntegerField(u'价格范围2', default=0, help_text=u'类型为整数，表示价格范围的上限，用于搜索')

    # 平台扣点： 淘宝、抖音、快手、多多、Tikto、视频号、小红书
    kickback = models.FloatField(u'淘宝扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')
    kickback_dy = models.FloatField(u'抖音扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')
    kickback_dd = models.FloatField(u'多多扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')
    kickback_ks = models.FloatField(u'快手扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')
    kickback_tikto = models.FloatField(u'tikto扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')
    kickback_shipin = models.FloatField(u'视频号扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')
    kickback_xhs = models.FloatField(u'小红书扣点', default=0, help_text=u'类型为小数，例如：扣点10%，应该填写 0.1')

    # 货主等级： 等级、历史成交额、成交率、合格率、供货率、配合度、品质率、是否白名单
    level = models.FloatField(u'货主等级', null=True, blank=True, default=0)
    cj_amount = models.FloatField(u'历史成交额', null=True, blank=True, default=0)
    cj_rate = models.FloatField(u'成交率', null=True, blank=True, default=0)
    hg_rate = models.FloatField(u'合格率', null=True, blank=True, default=0)
    gh_rate = models.FloatField(u'供货率', null=True, blank=True, default=0)
    ph_rate = models.FloatField(u'配合度', null=True, blank=True, default=0)
    pz_rate = models.FloatField(u'品质率', null=True, blank=True, default=0)
    is_whitelist = models.BooleanField(u'是否加入白名单', default=False, help_text=u'是否加入白名单')

    # 货主评分： 综合评分/平均分、款式评分、品质评分、销售技巧评分、性价比评分
    score = models.FloatField(u'综合评分', default=0)
    pinzhi = models.PositiveSmallIntegerField(u'品质评分', choices=SCORE_STARS, default=0, null=True)  # 去掉null=True会migrate失败
    kuanshi = models.PositiveSmallIntegerField(u'款式评分', choices=SCORE_STARS, default=0, null=True)
    xingjiabi = models.PositiveSmallIntegerField(u'性价比评分', choices=SCORE_STARS, default=0, null=True)
    xiaoshoujiqiao = models.PositiveSmallIntegerField(u'销售技巧评分', choices=SCORE_STARS, default=0, null=True)

    # 开户信息：收款人、开户行、银行卡号、账号间隔天数
    payee = models.CharField(u'收款人', max_length=255, null=True, blank=True)
    bankname = models.CharField(u'开户行', max_length=255, null=True, blank=True)
    bankcode = models.CharField(u'银行卡', max_length=255, null=True, blank=True)
    # 箱号必填
    casenumber = models.CharField(u'箱号', max_length=255, null=True, blank=True)
    bill_days = models.PositiveIntegerField(u'账单间隔天数', default=15, help_text=u'默认情况为15天，特殊货主会有调整')

    # 额外
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    # shop_id 必须填写
    shop_id = models.IntegerField(verbose_name=u'所属商户', default=2)

    # 为空，不管这些字段
    hour_money = models.FloatField(u'每小时销售额', null=True, blank=True)
    hour_profit = models.FloatField(u'每小时收益', null=True, blank=True)
    check_rate = models.FloatField(u'结款率', null=True, blank=True)
    hour_count = models.PositiveIntegerField(u'每小时件数', null=True, blank=True)

    class Meta:
        verbose_name = u'子货主表'
        verbose_name_plural = u'子货主表'
        unique_together = ('name',)
        db_table = 'shop_shipper'


IMG_TYPES = (
    ('1', u'产品图片'),
    ('2', u'货主证件/资格'),
    ('3', u'其它'),
)


class ShipperImage(models.Model):
    shipper = models.ForeignKey(ShopShipper, verbose_name=u'所属货主', related_name='images', on_delete=models.PROTECT)
    # file = ProcessedImageField(upload_to=uuid_file_path, verbose_name=u'图片文件',
    #                            format='JPEG', options={'quality': settings.IMAGE_QUANLITY})
    file = models.TextField(null=True, blank=True, verbose_name='图片路径')
    type = models.CharField(u'类型', choices=IMG_TYPES, default='1', max_length=1)
    is_deleted = models.BooleanField(u'是否删除', default=False)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name = u'货主图片'
        verbose_name_plural = u'货主图片'
        db_table = 'shop_shipper_image'


class KickList(models.Model):
    shop_id = models.IntegerField(verbose_name=u'所属商户', default=2)
    shipper = models.ForeignKey(ShopShipper, related_name='kicklist_shipper', verbose_name=u'shipper', null=True, blank=True, on_delete=models.PROTECT)
    startday = models.DateField(u'开始日期', null=True, blank=True)
    endday = models.DateField(u'结束日期', null=True, blank=True)
    kickback = models.FloatField(u'实际扣点', default=0)
    kickback_dy = models.FloatField(u'实际扣点', default=0)
    kickback_dd = models.FloatField(u'多多扣点', default=0)
    kickback_ks = models.FloatField(u'快手扣点', default=0)
    kickback_tikto = models.FloatField(u'tikto扣点', default=0)
    kickback_shipin = models.FloatField(u'shipin扣点', default=0)
    is_active = models.BooleanField(u'是否启用', default=False)
    creator = models.ForeignKey(AccountMyuser, related_name='KickList_creator', verbose_name=u'操作人',
                                on_delete=models.PROTECT)
    created_time = models.DateTimeField(u'created_time', null=True, blank=True)

    class Meta:
        verbose_name = u'扣点记录'
        verbose_name_plural = u'扣点记录'
        db_table = 'finance_kicklist'   # 兼容浩枫的表名，不影响他使用