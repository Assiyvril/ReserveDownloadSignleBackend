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


@celery_app.task(name='celery_test_baga', time_limit=SOFT_TIME_LIMIT, max_retries=MAX_RETRY_COUNT)
def test_celery(num):
    """
    测试celery
    :param num:
    :return:
    """
    print(f'{num}号celery 开始执行')
    order_qs = OrderOrder.objects.filter(
        created_time__date__gte='2024-04-01',
        created_time__date__lte='2024-04-02',
    )[0:100].prefetch_related(
        'prefix',
        'category', 'shipper',
        'zhubo', 'zhuli',
        'item_status',
        'play', 'play__changzhang', 'play__banzhang', 'play__shichangzhuanyuan', 'play__zhuli2',
        'play__zhuli3', 'play__zhuli4', 'play__changkong', 'play__changkong1',
        'play__changkong2', 'play__changkong3', 'play__kefu1', 'play__kefu2',
        'play__kefu3', 'play__kefu4', 'play__creator', 'play__classs',
        'rel_to_taobao_order', 'rel_to_taobao_order__taobaoorder',
        'scan_code_flows', 'qdb_orders', 'checkgoodstype',
    )
    flow_qs = OrderFlow.objects.filter(
        order__in=order_qs,
    ).prefetch_related(
        'order', 'order__prefix', 'order__category', 'order__shipper', 'order__zhubo', 'order__zhuli',
        'order__item_status', 'order__play', 'order__play__changzhang', 'order__play__banzhang',
        'order__play__shichangzhuanyuan', 'order__play__zhuli2', 'order__play__zhuli3', 'order__play__zhuli4',
        'order__play__changkong', 'order__play__changkong1', 'order__play__changkong2', 'order__play__changkong3',
        'order__play__kefu1', 'order__play__kefu2', 'order__play__kefu3', 'order__play__kefu4', 'order__play__classs',
        'order__rel_to_taobao_order', 'order__rel_to_taobao_order__taobaoorder',
        'order__scan_code_flows', 'owner', 'status', 'order__qdb_orders', 'order__checkgoodstype',
    )
    od = ReserveDownloadOrderSerializer(order_qs, many=True).data
    fd = ReserveDownloadOrderFlowSerializer(flow_qs, many=True).data

    print(f'{num}号celery 执行结束 order Data Count{len(od)}, flow Data Count{len(fd)}')

