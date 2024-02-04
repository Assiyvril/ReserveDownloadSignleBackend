from __future__ import absolute_import, unicode_literals
from scripts_public import _setup_django
import datetime
from celery_task.celery_main import celery_app
from reserve_download.models import ReserveDownload
from reserve_download.scripts.inquire_order_info import ReserveDownloadOrderInquirer

"""
预约下载
"""

SOFT_TIME_LIMIT = 60 * 60 * 10  # 任务超时时间 10小时
MAX_RETRY_COUNT = 2  # 任务最大重试次数


@celery_app.task(name='reserve_download_app_task', soft_time_limit=SOFT_TIME_LIMIT, max_retries=MAX_RETRY_COUNT)
def scheduled_download(data_start_date, data_end_date, fendian_id_list, scan_code_status, scan_code_start_date,
                       scan_code_end_date, reserve_download_record_id, file_name):
    """
    定时下载 Task
    定时下载
    @param file_name:  文件名
    @param data_start_date: 数据开始时间
    @param data_end_date: 数据结束时间
    @param fendian_id_list: 店铺id列表
    @param scan_code_status: 扫码状态
    @param scan_code_start_date: 扫码开始时间
    @param scan_code_end_date: 扫码结束时间
    @param reserve_download_record_id: 预约下载记录id
    :return:
    """
    print('celery task  scheduled_download 开始！', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_start_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        task_status=3,
    )
    ReserveDownloadOrderInquirer(
        data_start_date=data_start_date,
        data_end_date=data_end_date,
        fendian_id_list=fendian_id_list,
        scan_code_status_id_list=scan_code_status,
        scan_code_start_date=scan_code_start_date,
        scan_code_end_date=scan_code_end_date,
        reserve_download_record_id=reserve_download_record_id,
        file_name=file_name,
        is_test_mode=False
    ).exec()
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    print('celery task  scheduled_download 结束！', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
