from django.db import models
from enum import Enum
"""
浩峰的字典
"""


class StatusEnum(Enum):
    # 启用状态
    Enable = 1
    # 停用状态
    Disable = 0


class Dict(models.Model):
    created_at = models.DateTimeField(blank=True, null=True, auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    cname = models.CharField(max_length=200, blank=True, null=True)
    ename = models.CharField(max_length=200, blank=True, null=True)
    status = models.SmallIntegerField(blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'xda_dictionaries'

    @classmethod
    def search_dict(cls, name):
        return DictDetail.objects. \
            filter(models.Q(parent__cname=name) | models.Q(parent__ename=name)). \
            filter(status=StatusEnum.Enable.value). \
            order_by('-sort').all()


# 字典详情
class DictDetail(models.Model):
    created_at = models.DateTimeField(blank=True, null=True, auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    sort = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey(Dict, on_delete=models.CASCADE, db_constraint=False,
                               db_column='dictionary_id', related_query_name="detail")

    class Meta:
        managed = False
        db_table = 'xda_dictionary_details'
