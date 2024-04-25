from __future__ import absolute_import, unicode_literals

import time

from scripts_public import _setup_django
import datetime
from celery_task.celery_main import celery_app
from reserve_download.models import ReserveDownload
from reserve_download.scripts.inquire_order_info import ReserveDownloadOrderInquirer, OrderInquireByCode, TestInquire

"""
预约下载
"""

SOFT_TIME_LIMIT = 60 * 60 * 10  # 任务超时时间 10小时
MAX_RETRY_COUNT = 2  # 任务最大重试次数


@celery_app.task(name='reserve_download_app_task', soft_time_limit=SOFT_TIME_LIMIT, max_retries=MAX_RETRY_COUNT)
def scheduled_download_by_params(query_param_dict, reserve_download_record_id, file_name):
    """
    定时下载 Task
    定时下载
    @param file_name:  文件名
    @param query_param_dict: post 任务参数
    @param reserve_download_record_id: 预约下载记录id
    :return:
    """
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_start_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        task_status=3,
    )
    ReserveDownloadOrderInquirer(
        query_param_dict=query_param_dict,
        reserve_download_record_id=reserve_download_record_id,
        file_name=file_name,
    ).exec()
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )


@celery_app.task(name='reserve_download_by_upload_excel', soft_time_limit=SOFT_TIME_LIMIT, max_retries=MAX_RETRY_COUNT)
def scheduled_download_by_upload_excel(parse_excel_data, available_fendian_id_list, order_code_mode, is_history, reserve_download_record_id, file_name):
    """
    定时下载 Task
    定时下载
    @param file_name:  文件名
    @param reserve_download_record_id: 预约下载记录id
    @param parse_excel_data: 解析的excel数据
    @param available_fendian_id_list: 可用店铺id列表
    @param order_code_mode: 订单号模式
    @param is_history: 是否历史状态
    """
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_start_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        task_status=3,
    )
    OrderInquireByCode(
        parse_order_code_list=parse_excel_data,
        available_fendian_id_list=available_fendian_id_list,
        order_code_mode=order_code_mode,
        is_history=is_history,
        reserve_download_record_id=reserve_download_record_id,
        file_name=file_name,
    ).exec()
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )


@celery_app.task(name='celery_test_baga', soft_time_limit=SOFT_TIME_LIMIT, max_retries=MAX_RETRY_COUNT)
def test_celery(num):
    """
    测试celery
    :param num:
    :return:
    """
    print(num, '号celery 开始执行, 20秒后结束')
    obj = ReserveDownload.objects.filter(
        created_time__date=datetime.datetime.now().strftime('%Y-%m-%d'),
    ).first()
    print('调用 orm 测试 ID', obj.id)
    TestInquire(num).exec()
    # print('调用类方法测试', ti.exec())
    print(num, '号celery 执行结束')

