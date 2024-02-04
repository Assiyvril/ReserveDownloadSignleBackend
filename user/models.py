from django.db import models
from shop.models import ShopDepartment, ShopSerialprefix


class AccountRole(models.Model):
    shop_id = models.IntegerField(default=2)
    role_name = models.CharField('角色名称', max_length=32)
    role_type = models.CharField('角色编码', max_length=5)
    order = models.IntegerField('排序')
    froms = models.CharField('来源', max_length=100, blank=True, null=True)
    desc = models.CharField('描述', max_length=255, blank=True, null=True)
    is_super = models.BooleanField('是否为超管', blank=True, null=True)
    is_permission = models.IntegerField('权限标识', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_role'


class AccountMyuser(models.Model):

    UserTypeChoices = (
        ('1', u'后台人员'),
        ('2', u'录单人员'),
        ('14', u'发货人员'),
        ('3', u'主播'),
        # ('13', u'替播'),
        ('4', u'助理'),
        ('5', u'联络员'),
        ('6', u'财务'),
        ('7', u'市场部'),
        ('11', u'主管'),
        ('12', u'客服主管'),
        ('15', u'P厂长'),
        ('19', u'P班长'),
        ('16', u'P场控'),
        ('17', u'P市场专员'),
        ('18', u'P客服'),
        ('88', u'经理'),
    )

    password = models.CharField('密码', max_length=128)
    username = models.CharField('用户名', unique=True, max_length=150)
    first_name = models.CharField('名称', max_length=30)
    last_name = models.CharField('名称2', max_length=30)
    email = models.CharField('邮箱', max_length=254)
    is_active = models.BooleanField('是否激活')
    notes = models.TextField('备注', blank=True, null=True)
    doprefix = models.ManyToManyField(ShopSerialprefix, verbose_name=u'绑定工作扫码店铺', related_name='myuser_doprefix', blank=True,
                                      help_text=u'管理设置')
    prefix = models.ForeignKey(ShopSerialprefix, models.DO_NOTHING, blank=True, null=True, verbose_name='归属店铺')
    department = models.ForeignKey(ShopDepartment, models.DO_NOTHING, blank=True, null=True,
                                   db_column='department_id', verbose_name='归属部门')
    usertype = models.ForeignKey(AccountRole, models.DO_NOTHING, blank=True, null=True, db_column='usertype_id',
                                 verbose_name='归属角色')
    dingtalk_userid = models.CharField('钉钉ID', max_length=100, blank=True, null=True)
    type = models.CharField('类型', choices=UserTypeChoices, max_length=10, blank=True, null=True)
    date_joined = models.DateTimeField('注册时间')
    last_login = models.DateTimeField('最后登录时间')

    class Meta:
        managed = False
        db_table = 'account_myuser'
