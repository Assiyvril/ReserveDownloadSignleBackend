from django.db import models
from user.models import AccountMyuser


class ReserveDownload(models.Model):
    """
    预约下载, 查询大量数据
    """
    TASK_STATUS = (
        (0, '等待创建'),
        (1, '任务创建成功'),
        (2, '任务创建失败'),
        (3, '等待执行'),
        (4, '正在查询'),
        (5, '查询完毕，正在生成文件'),
        (6, '查询失败，任务终止'),
        (7, '文件生成完毕'),
        (8, '文件生成失败'),
        (9, '任务成功，文件已过期'),
    )
    creator = models.ForeignKey(AccountMyuser, verbose_name='创建人', on_delete=models.CASCADE)
    created_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    filter_condition = models.JSONField(verbose_name='筛选条件', null=False, blank=False)
    fendian_info = models.JSONField(verbose_name='店铺信息', null=True, blank=True)
    task_exec_start_time = models.DateTimeField(verbose_name='任务开始执行时间', null=True, blank=True)
    task_exec_end_time = models.DateTimeField(verbose_name='任务执行结束时间', null=True, blank=True)
    task_status = models.IntegerField(verbose_name='任务状态', choices=TASK_STATUS, default=0)
    task_celery_id = models.CharField(verbose_name='celery 任务ID', max_length=255, null=True, blank=True)
    task_result = models.TextField(verbose_name='任务结果', null=True, blank=True)
    file_name = models.CharField(verbose_name='文件名', max_length=255, null=True, blank=True)
    is_success = models.BooleanField(verbose_name='是否成功', default=False)
    tag = models.CharField(verbose_name='标签备注', max_length=255, null=True, blank=True)
    data_count = models.IntegerField(verbose_name='数据量', null=True, blank=True)
    # 24-04-21 添加字段，用于给前端判断文件可否下载。不再使用 is_success 字段来判断，is_success 仅用于判断任务是否成功
    can_download = models.BooleanField(verbose_name='文件可否下载', default=False, help_text='是否可以下载文件，文件生成后，设为True, 过期删除后，将此字段置为False')

    class Meta:
        verbose_name = '预约下载'
        verbose_name_plural = '预约下载'
        db_table = 'reserve_download'
        managed = True
