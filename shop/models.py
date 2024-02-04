from django.conf import settings
from django.db import models


class ShopDepartment(models.Model):

    COMP_TYPES = (
        (0, u'无任何构架'),
        (1, u'总公司构架'),
        (2, u'抖音分公司构架'),
        # (3, u'拼多多分公司'),
        (4, u'平洲分公司构架'),
        (5, u'万源公司构架'),
        (6, u'达人项目构架'),
        (7, u'项目三构架'),
        (8, u'供应链构架'),
    )

    shop_id = models.IntegerField(default=2, db_column='shop_id',
                                  verbose_name=u'所属商户ID')
    name = models.CharField(u'名称', max_length=31,
                            help_text=u'事业部的名称，例如事业一部，可以包括多个分店')
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               related_name='leader', verbose_name=u'负责人',
                               on_delete=models.PROTECT)
    in_company = models.PositiveIntegerField(u'公司构架', choices=COMP_TYPES,
                                             default=0)
    workordertype_id = models.IntegerField(default=1, verbose_name='审批流程，不用关注')
    notes = models.TextField(u'备注', null=True, blank=True,
                             help_text=u'仅管理员可见')
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    sort = models.PositiveIntegerField(u'排序', default=200,
                                       help_text=u'从小到大显示')
    is_active = models.BooleanField(u'是否生效', default=True,
                                    help_text=u'无效的不会在APP中显示')

    class Meta:
        managed = False
        db_table = 'shop_department'


class ShopSerialprefix(models.Model):
    SRC_TYPES = (
        (u'1', u'淘宝'),
        (u'2', u'抖音'),
        (u'3', u'拼多多'),
        (u'4', u'微拍堂'),
        (u'5', u'快手'),
        (u'6', u'私域'),
        (u'7', u'今日头条'),
        (u'8', u'tikto'),
        (u'9', u'视频号'),
        (u'10', u'小红书'),
    )
    name = models.CharField('名称', max_length=31)
    prefix = models.CharField('前缀', max_length=7)
    notes = models.TextField('备注', blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey(ShopDepartment, models.DO_NOTHING, blank=True, null=True)
    sort = models.IntegerField('排序', default=1)
    is_active = models.BooleanField('激活状态', blank=True, null=True, default=True)
    in_company = models.IntegerField('所属公司', blank=True, null=True, default=1)
    shop = models.IntegerField(default=2, db_column='shop_id')
    src = models.CharField(u'平台类型', choices=SRC_TYPES, default='1', max_length=2)
    platform_store_name = models.CharField(u'电商平台上的店铺名', null=True, blank=True, max_length=255, help_text=u'仅管理员可见')
    platform_store_id = models.CharField(u'电商平台上的店铺ID', null=True, blank=True, max_length=255, help_text=u'仅管理员可见')
    is_auto_qic = models.BooleanField(verbose_name='是否开启API绑码功能', default=False, help_text='只有开启此功能的店铺才能使用 大G QIC 绑码模块')
    auto_qic_date = models.DateField(verbose_name='开启API绑码功能的日期', blank=True, null=True, help_text='记录开启的日期')

    class Meta:
        managed = False
        db_table = 'shop_serialprefix'


class AccountDoprefix(models.Model):
    """扫码工作店铺表"""
    myuser_id = models.IntegerField('myuser_id', blank=True, null=True)
    serialprefix_id = models.IntegerField('serialprefix_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_myuser_doprefix'
