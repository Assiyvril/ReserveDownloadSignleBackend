"""
2024-04-27
将 filter_condition 的前端展示可读文本， 改为了在 celery task 中 异步构建， 以减少前端请求的时间
批量更新库里的 filter_condition 的 readable_text 字段
"""
from scripts_public import _setup_django
from commodity_category.models import ShopCategory
from reserve_download.models import ReserveDownload
from shipper.models import ShopShipper
from user.models import AccountMyuser
from order.models import ItemStatus


def build_query_params_text_data(origin_filter_condition):
    """
    通过表单提交参数的
    :return:
    """
    # record_obj = ReserveDownload.objects.filter(id=self.reserve_download_record_id).first()
    # if not record_obj:
    #     return
    # origin_filter_condition = record_obj.filter_condition
    # if not origin_filter_condition:
    #     return
    is_excel_mode = origin_filter_condition.get('is_excel', False)
    if is_excel_mode:
        # 若是 excel 模式， 则不需要构建 readable_text， 直接返回原始的 filter_condition
        return origin_filter_condition
    text_data = {
        'is_ship': '',  # 是否发货
        'end_date': origin_filter_condition.get('end_date', ''),  # 结束日期
        'start_date': origin_filter_condition.get('start_date', ''),  # 开始日期
        'date_type': '',  # 日期类别
        'is_history': '',  # 是否历史
        'zhubo': '',  # 主播名字
        'is_guding_link': '',  # 是否固定链接
        'has_certificate': '',  # 是否有证书
        'live_shift': '',  # 直播班次
        'scanner': '',  # 扫码人名字
        'shipper': '',  # 货主名字
        'scan_code_status': '',  # 扫码状态
        'order_situation': '',  # 订单情况
        'platform_status': '',  # 平台状态
        'pinjianzhuangtai': '',  # 品检状态
        'shichangzhuanyuan': '',  # 市场专员名字
        'commodity_category': '',  # 货品分类
    }
    # 是否发货
    is_ship = origin_filter_condition.get('is_ship', None)
    if is_ship is None:
        text_data['is_ship'] = '全部'
    elif is_ship:
        text_data['is_ship'] = '已发货'
    else:
        text_data['is_ship'] = '未发货'

    # 日期类别
    date_type = origin_filter_condition.get('date_type')
    if date_type == 'order_date':
        text_data['date_type'] = '下单日期'
    else:
        text_data['date_type'] = '扫码日期'

    # 是否历史数据
    is_history = origin_filter_condition.get('is_history', False)
    if is_history:
        text_data['is_history'] = '历史数据'
    else:
        text_data['is_history'] = '当前数据'

    # 主播名字
    zhubo_id_list = origin_filter_condition.get('zhubo_id_list', [])
    if len(zhubo_id_list) == 0:
        text_data['zhubo'] = '全部'
    else:
        zhubo_qs = AccountMyuser.objects.filter(id__in=zhubo_id_list)
        # zhubo_name = ''
        for zhubo_obj in zhubo_qs:
            zhubo_name = zhubo_obj.first_name + '(' + zhubo_obj.notes + ')，'
            text_data['zhubo'] += zhubo_name
        # 去掉最后的 '，'
        text_data['zhubo'] = text_data['zhubo'][:-1]

    # 是否固定链接
    is_guding_link = origin_filter_condition.get('is_Guding_link', None)
    if is_guding_link is None:
        text_data['is_guding_link'] = '全部'
    elif is_guding_link:
        text_data['is_guding_link'] = '固定链接'
    else:
        text_data['is_guding_link'] = '闪购链接'

    # 是否有证书
    has_certificate = origin_filter_condition.get('has_certificate', None)
    if has_certificate is None:
        text_data['has_certificate'] = '全部'
    elif has_certificate:
        text_data['has_certificate'] = '有证书'
    else:
        text_data['has_certificate'] = '无证书'

    # 直播班次
    live_shift_list = origin_filter_condition.get('live_shift_list', [])
    if len(live_shift_list) == 0:
        text_data['live_shift'] = '全部'
    else:
        dict_map = {
            1: '早班',
            2: '中班',
            3: '晚班',
            4: '夜班',
        }
        for live_shift in live_shift_list:
            text_data['live_shift'] += dict_map[live_shift] + '，'
        # 去掉最后的 '，'
        text_data['live_shift'] = text_data['live_shift'][:-1]

    # 扫码人名字
    scanner_id_list = origin_filter_condition.get('scanner_id_list', [])
    if len(scanner_id_list) == 0:
        text_data['scanner'] = '全部'
    else:
        scanner_qs = AccountMyuser.objects.filter(id__in=scanner_id_list)
        for scanner_obj in scanner_qs:
            scanner_name = scanner_obj.first_name + '，'
            text_data['scanner'] += scanner_name
        # 去掉最后的 '，'
        text_data['scanner'] = text_data['scanner'][:-1]

    # 货主名字
    shipper_id_list = origin_filter_condition.get('shipper_id_list', [])
    if len(shipper_id_list) == 0:
        text_data['shipper'] = '全部'
    else:
        shipper_qs = ShopShipper.objects.filter(id__in=shipper_id_list)
        for shipper_obj in shipper_qs:
            shipper_name = shipper_obj.name + '，'
            text_data['shipper'] += shipper_name
        # 去掉最后的 '，'
        text_data['shipper'] = text_data['shipper'][:-1]

    # 扫码状态
    scan_code_status_list = origin_filter_condition.get('scan_code_status', [])
    if len(scan_code_status_list) == 0:
        text_data['scan_code_status'] = '全部'
    else:
        status_qs = ItemStatus.objects.filter(id__in=scan_code_status_list)
        for status_obj in status_qs:
            status_name = status_obj.name + '，'
            text_data['scan_code_status'] += status_name
        # 去掉最后的 '，'
        text_data['scan_code_status'] = text_data['scan_code_status'][:-1]

    # 订单情况
    order_situation_list = origin_filter_condition.get('order_situation_list', [])
    if len(order_situation_list) == 0:
        text_data['order_situation'] = '全部'
    else:
        map_dict = {
            'normal_order': '正常订单',
            'deleted_order': '被删订单',
            'presale_order': '预售订单',
            'super_welfare_order': '超福订单',
            'offline_ship': '线下发货',
            'cost_settlement': '成本结算',
            'kick_settlement': '扣点结算',
            'special_order': '特殊订单',
            'need_bind_goods': '需绑货品',
            're_record_order': '重录订单',
        }
        for order_situation in order_situation_list:
            text_data['order_situation'] += map_dict[order_situation] + '，'
        # 去掉最后的 '，'
        text_data['order_situation'] = text_data['order_situation'][:-1]

    # 平台状态
    platform_status_list = origin_filter_condition.get('platform_status_list', [])
    if len(platform_status_list) == 0:
        text_data['platform_status'] = '全部'
    else:
        map_dict = {
            'all_return': '订单退款',
            'part_return': '部分退款',
            'not_return': '订单未退',
        }
        for platform_status in platform_status_list:
            text_data['platform_status'] += map_dict[platform_status] + '，'
        # 去掉最后的 '，'
        text_data['platform_status'] = text_data['platform_status'][:-1]

    # 品检状态
    pinjianzhuangtai_list = origin_filter_condition.get('pinjianzhuangtai_list', [])
    if len(pinjianzhuangtai_list) == 0:
        text_data['pinjianzhuangtai'] = '全部'
    else:
        map_dict = {
            'eligibility': '品检合格',
            'unqualified': '不合格',
            'unqualified_enter_warehouse': '不合格入库',
            'no_check': '未品检',
        }
        for pinjianzhuangtai in pinjianzhuangtai_list:
            text_data['pinjianzhuangtai'] += map_dict[pinjianzhuangtai] + '，'
        # 去掉最后的 '，'
        text_data['pinjianzhuangtai'] = text_data['pinjianzhuangtai'][:-1]

    # 市场专员名字
    shichangzhuanyuan_id_list = origin_filter_condition.get('shichangzhuanyuan_id_list', [])
    if len(shichangzhuanyuan_id_list) == 0:
        text_data['shichangzhuanyuan'] = '全部'
    else:
        shichangzhuanyuan_qs = AccountMyuser.objects.filter(id__in=shichangzhuanyuan_id_list)
        for shichangzhuanyuan_obj in shichangzhuanyuan_qs:
            shichangzhuanyuan_name = shichangzhuanyuan_obj.first_name + '，'
            text_data['shichangzhuanyuan'] += shichangzhuanyuan_name
        # 去掉最后的 '，'
        text_data['shichangzhuanyuan'] = text_data['shichangzhuanyuan'][:-1]

    # 货品分类
    commodity_category_id_list = origin_filter_condition.get('commodity_category_id_list', [])
    if len(commodity_category_id_list) == 0:
        text_data['commodity_category'] = '全部'
    else:
        category_qs = ShopCategory.objects.filter(id__in=commodity_category_id_list)
        for category_obj in category_qs:
            category_name = ''
            category_family = category_obj.get_my_family()
            if not category_family:
                category_name = category_obj.name
            else:
                for category in category_family:
                    category_name += category.name + '->'
                category_name = category_name[:-2]
            category_name += '，'
            text_data['commodity_category'] += category_name
        # 去掉最后的 '，'
        text_data['commodity_category'] = text_data['commodity_category'][:-1]

    origin_filter_condition['readable_text'] = text_data

    return origin_filter_condition


def build_excel_mode_text_data(origin_filter_condition):
    is_excel_mode = origin_filter_condition.get('is_excel', False)
    if not is_excel_mode:
        # 若不是 excel 模式， 则不需要构建 readable_text， 直接返回原始的 filter_condition
        return origin_filter_condition
    text_data = {
        'is_history': '',  # 是否历史
        'excel_file_mode': '',  # excel 文件模式
    }
    # 是否历史数据
    is_history = origin_filter_condition.get('is_history', False)
    if is_history:
        text_data['is_history'] = '历史数据'
    else:
        text_data['is_history'] = '当前数据'

    # excel 文件模式
    excel_file_mode = origin_filter_condition.get('excel_file_mode', '')
    if excel_file_mode == 'big_G':
        text_data['excel_file_mode'] = '大G单号'
    else:
        text_data['excel_file_mode'] = '平台单号'

    origin_filter_condition['readable_text'] = text_data

    return origin_filter_condition


def batch_update():
    """
    进行批量更新
    :return:
    """

    record_qs = ReserveDownload.objects.all().order_by('-id')
    for record_obj in record_qs:
        origin_filter_condition = record_obj.filter_condition
        if not origin_filter_condition:
            print('record_id:', record_obj.id, '没有 filter_condition')
            continue
        read_text = origin_filter_condition.get('readable_text', {})
        if read_text:
            print('record_id:', record_obj.id, '已经有 readable_text')
            continue
        # 生成 readable_text
        is_excel_mode = origin_filter_condition.get('is_excel', False)
        if is_excel_mode:
            # 若是 excel 模式
            print('record_id:', record_obj.id, '是 excel 模式')
            new_filter_condition = build_excel_mode_text_data(origin_filter_condition)
        else:
            # 若不是 excel 模式
            print('record_id:', record_obj.id, '是 params 模式')
            new_filter_condition = build_query_params_text_data(origin_filter_condition)

        # 更新
        record_obj.filter_condition = new_filter_condition
        record_obj.save()
        print('record_id:', record_obj.id, '更新完毕')


if __name__ == '__main__':
    batch_update()
