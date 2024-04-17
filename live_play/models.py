from django.db import models

from shipper.models import ShopShipper, MainShipper
from shop.models import ShopSerialprefix
from user.models import AccountMyuser


class ShopScheduleRecords(models.Model):
    """
    店铺排班
    """
    shop_id = models.IntegerField(verbose_name=u'所属商户ID', default=2)
    prefix = models.ForeignKey(ShopSerialprefix, related_name='prefix_schedule_records', verbose_name=u'所属分店',
                               on_delete=models.PROTECT)
    start_live = models.CharField(u'开播时间', max_length=31)
    end_live = models.CharField(u'下播时间', max_length=31)
    start_day = models.DateField(u'开始日期', null=True, blank=True)
    end_day = models.DateField(u'结束日期', null=True, blank=True)
    desc = models.TextField(u'备注', null=True, blank=True)
    is_active = models.BooleanField(u'是否启用', default=True)


class Seller(models.Model):

    SEX = (
        (0, u'无'),
        (1, u'男'),
        (2, u'女'),
    )

    """卖手"""
    shop_id = models.IntegerField(verbose_name=u'所属商户', default=2)
    mainshipper = models.ForeignKey(MainShipper, verbose_name=u'所属货主', related_name='seller_mainshipper', null=True,
                                    blank=True, on_delete=models.PROTECT)
    sex = models.IntegerField(u'性别', choices=SEX, default=0, null=True, blank=True)
    avatar = models.TextField(u'头像', null=True, blank=True, help_text=u'建议大小为300x300')
    name = models.CharField(u'卖手名字', max_length=255, null=True, blank=True)
    contact = models.CharField(u'联系人', max_length=255, null=True, blank=True)
    phone = models.CharField(u'手机号', max_length=255, null=True, blank=True)
    identitycard = models.CharField(u'身份证', max_length=255, null=True, blank=True)
    livename = models.CharField(u'直播间昵称', max_length=255, null=True, blank=True)
    is_active = models.BooleanField(u'是否生效', default=True, help_text=u'卖手')

    class Meta:
        verbose_name = u'总卖手表'
        verbose_name_plural = u'总卖手表'
        unique_together = ('name',)


class LiveShiftSchedule(models.Model):
    """
    直播排班
    """
    CLASSTAG = (
        (1, u'早班'),
        (2, u'中班'),
        (3, u'晚班'),
        (4, u'夜班'),
    )

    shop_id = models.IntegerField(verbose_name=u'所属商户ID', default=2)
    prefix = models.ForeignKey(ShopSerialprefix, related_name='prefix_classs', verbose_name=u'所属分店', on_delete=models.PROTECT)
    creator = models.ForeignKey(AccountMyuser, related_name='creator_classs', verbose_name=u'创建者', on_delete=models.PROTECT)
    shipper = models.ForeignKey(ShopShipper, related_name='shipper_classs', verbose_name=u'货主', on_delete=models.PROTECT)
    classtable = models.ForeignKey(ShopScheduleRecords, related_name='classtable_classs', verbose_name=u'店铺排班表', on_delete=models.PROTECT, null=True, blank=True)
    zhubo = models.ForeignKey(AccountMyuser, related_name='zhubo_classs', verbose_name=u'主播', on_delete=models.PROTECT)
    start_time = models.DateTimeField(u'开场时间', db_index=True)
    end_time = models.DateTimeField(u'结束时间', db_index=True, null=True, blank=True)
    desc = models.TextField(u'备注', null=True, blank=True)
    count = models.PositiveIntegerField(u'订单数量', default=0)
    kpi = models.DecimalField(u'KPI', max_digits=15, decimal_places=2, default=0, help_text=u'KPI数值')
    classtag = models.PositiveIntegerField(u'班次', choices=CLASSTAG, default=0)
    day = models.DateField(u'下单日期', null=True, blank=True)
    seller = models.ForeignKey(Seller, verbose_name=u'卖手', related_name='class_seller', null=True, blank=True, on_delete=models.PROTECT)
    first_sms = models.PositiveIntegerField(u'预约成功提醒', default=0)   # 是否要预约成功提醒
    myalert_sms = models.PositiveIntegerField(u'播前提醒', default=0)   # 是否要播前提醒
    first_sms_time = models.DateTimeField(u'预约成功提醒', db_index=True, null=True, blank=True)  # 预约成功提醒时间
    myalert_sms_time = models.DateTimeField(u'播前提醒', db_index=True, null=True, blank=True)  # 播前提醒时间
    is_checkcomplete = models.PositiveIntegerField(u'巡检完成', default=0)  # 是否巡检完成
    checkcreator = models.ForeignKey(AccountMyuser, related_name='巡检人', verbose_name=u'创建者', null=True, blank=True,
                                     on_delete=models.PROTECT)
    checktime = models.DateTimeField(u'巡检时间', db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = u'直播排班'
        verbose_name_plural = u'直播排班'
        db_table = 'order_class'


class OrderPlay(models.Model):
    """
    直播场次
    """
    ZHI_BO_TYPE_CHOICES = (
        (0, '默认播货'),
        (1, '定制走播'),
        (2, '定制自营'),
        (3, '定制调货'),
        (4, '共享平台'),
        (5, '自营成品'),
        (6, '自营代购'),
        (7, '播后加账'),
        (8, '货主混播'),
    )
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间', blank=True, null=True)
    desc = models.TextField('备注', blank=True, null=True)
    count = models.IntegerField('订单数量', default=0)
    is_add = models.SmallIntegerField('是否加账', blank=True, null=True, default=0)
    zhibo_type = models.IntegerField('播货类型', blank=True, null=True, default=0, choices=ZHI_BO_TYPE_CHOICES)

    shop_id = models.IntegerField('商户', default=2)
    changzhang = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='changzhang_play', verbose_name='场长')
    changzhang1 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='changzhang1_play', verbose_name='场长2')

    banzhang = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='班次长', related_name='banzhang')
    # 场控
    changkong = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='场控1', related_name='changkong')
    changkong1 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='场控2', related_name='changkong1')
    changkong2 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='场控3', related_name='changkong2')
    changkong3 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='场控4', related_name='changkong3')
    # 市场专员
    shichangzhuanyuan = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='市场专员', related_name='shichangzhuanyuan')
    # 助理
    zhuli1 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='助理1', related_name='zhuli1')
    zhuli2 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='助理2', related_name='zhuli2')
    zhuli3 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='助理3', related_name='zhuli3')
    zhuli4 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='助理4', related_name='zhuli4')
    # 客服
    kefu1 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='客服1', related_name='kefu1')
    kefu2 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='客服2', related_name='kefu2')
    kefu3 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='客服3', related_name='kefu3')
    kefu4 = models.ForeignKey(AccountMyuser, blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name='客服4', related_name='kefu4')

    # ### 关联字段 ###
    creator = models.ForeignKey(AccountMyuser, models.DO_NOTHING, verbose_name='创建人', related_name='play_creator')
    shipper = models.ForeignKey(ShopShipper, models.DO_NOTHING, verbose_name='货主')
    zhubo = models.ForeignKey(AccountMyuser, models.DO_NOTHING, blank=True, null=True, verbose_name='主播',
                              db_column='player_id', related_name='play_zhubo')
    classs = models.ForeignKey(LiveShiftSchedule, models.DO_NOTHING, blank=True, null=True, verbose_name='关联排班',
                               related_name='play_class')
    # ### 暂不需要 ###
    # is_discount = models.SmallIntegerField('是否引流款', blank=True, null=True)
    # discount_kickback = models.FloatField('是否引流款审批', blank=True, null=True)
    # discount_balance = models.FloatField('审批人', blank=True, null=True)
    # is_discount_pass = models.SmallIntegerField('引流款审批时间', blank=True, null=True)
    # discount_passor_id = models.IntegerField('引流扣点', blank=True, null=True)
    # discount_limit_amount = models.FloatField('额度余额', blank=True, null=True)
    # discount_pass_time = models.DateTimeField('限制金额', blank=True, null=True)
    # discount_limit_num = models.IntegerField('限制数量', blank=True, null=True)
    # play_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_play'
