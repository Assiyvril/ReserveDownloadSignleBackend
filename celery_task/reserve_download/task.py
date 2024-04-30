from __future__ import absolute_import, unicode_literals

import time

from scripts_public import _setup_django
import datetime
from celery_task.celery_main import celery_app
from reserve_download.models import ReserveDownload
from order.models import OrderFlow, OrderOrder
from reserve_download.serializers import ReserveDownloadOrderSerializer, ReserveDownloadOrderFlowSerializer
from reserve_download.scripts.inquire_order_info import ReserveDownloadOrderInquirer, OrderInquireByCode

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
    try:
        ReserveDownloadOrderInquirer(
            query_param_dict=query_param_dict,
            reserve_download_record_id=reserve_download_record_id,
            file_name=file_name,
        ).exec()
    except Exception as e:
        ReserveDownload.objects.filter(
            id=reserve_download_record_id
        ).update(
            task_result=str(e),
        )

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
    try:
        OrderInquireByCode(
            parse_order_code_list=parse_excel_data,
            available_fendian_id_list=available_fendian_id_list,
            order_code_mode=order_code_mode,
            is_history=is_history,
            reserve_download_record_id=reserve_download_record_id,
            file_name=file_name,
        ).exec()
    except Exception as e:
        ReserveDownload.objects.filter(
            id=reserve_download_record_id
        ).update(
            task_result=str(e),
        )
    ReserveDownload.objects.filter(
        id=reserve_download_record_id
    ).update(
        task_exec_end_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
