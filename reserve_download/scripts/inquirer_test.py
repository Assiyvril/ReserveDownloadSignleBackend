"""
查询器的测试用例
"""
import time
from scripts_public import _setup_django
from reserve_download.models import ReserveDownload
from order.models import OrderOrder, OrderTaobaoorder
from reserve_download.scripts.inquire_order_info import OrderInquireByCode


class TestToOrderInquireByCode:
    """
    对 OrderInquireByCode 类进行测试
    """

    def __init__(self, dataCount, is_history=False, code_mode='big_g'):
        self.dataCount = dataCount
        self.is_history = is_history
        self.code_mode = code_mode

        self.record_obj_id = None
        self.file_name = None
        self.order_code_list = []
        self.available_fendian_id_list = []

    def build_test_data(self):
        """
        生成测试数据
        :return:
        """
        # 1，生成文件名
        file_name = f'静宇单元测试_{self.code_mode}模式_码量{self.dataCount}_历史{str(self.is_history)}_{int(time.time())}.xlsx'
        self.file_name = file_name
        print('生成文件名完毕:', file_name)
        # 2，生成记录对象
        record_obj = ReserveDownload.objects.create(
            creator_id=6623, filter_condition={'name': '静宇单元测试 code模式'}, fendian_info={}, task_status=1, is_success=False,
            tag='单元测试 by 静宇', file_name=file_name,
        )
        self.record_obj_id = record_obj.id
        print('生成记录对象完毕, ID 为:', self.record_obj_id)

        # 3，生成订单数据
        if self.code_mode == 'big_G':
            # 从2024-04-01 到 2024-04-21 的订单数据
            order_qs = OrderOrder.objects.filter(
                day__gte='2024-04-01', day__lte='2024-04-21'
            )[0:self.dataCount]
            order_sn_list = order_qs.values_list('sn', flat=True)
            for sn in order_sn_list:
                data = {
                    'check_success': True,
                    'order_code': sn,
                }
                self.order_code_list.append(data)
            print('order_code_list 生成完毕, 数量为', len(self.order_code_list), self.order_code_list)
            # 生成可用的店铺ID， 从 order_qs 的店铺中，随机取出 二分之一的店铺ID，作为可用店铺ID
            all_fendian_id_list = order_qs.values_list('prefix__id', flat=True)
            # 去重
            all_fendian_id_list = list(set(all_fendian_id_list))
            self.available_fendian_id_list = all_fendian_id_list[0:int(len(all_fendian_id_list) / 2)]
            print('available_fendian_id_list 生成完毕， 数量为',len(self.available_fendian_id_list), self.available_fendian_id_list)
        else:
            # 平台订单号，从2024-04-01 到 2024-04-21 的订单数据
            taobao_order_qs = OrderTaobaoorder.objects.filter(
                created_time__gte='2024-04-01', created_time__lte='2024-04-21'
            )[0:self.dataCount]
            taobao_order_sn_list = taobao_order_qs.values_list('tbno', flat=True)
            for sn in taobao_order_sn_list:
                data = {
                    'check_success': True,
                    'order_code': sn,
                }
                self.order_code_list.append(data)
            print('order_code_list 生成完毕', len(self.order_code_list), self.order_code_list)
            # 生成可用的店铺ID， 从 taobao_order_qs 的店铺中，随机取出 二分之一的店铺ID，作为可用店铺ID
            all_fendian_id_list = taobao_order_qs.values_list('prefix__id', flat=True)
            # 去重
            all_fendian_id_list = list(set(all_fendian_id_list))
            self.available_fendian_id_list = all_fendian_id_list[0:int(len(all_fendian_id_list) / 2)]
            print('available_fendian_id_list 生成完毕， 数量为',len(self.available_fendian_id_list), self.available_fendian_id_list)

    def go_test(self):
        """
        开始测试
        :return:
        """
        # 1，生成测试数据
        self.build_test_data()
        print('----- 测试数据生成完毕 ----')
        # 2，开始查询
        inquirer = OrderInquireByCode(
            parse_order_code_list=self.order_code_list,
            available_fendian_id_list=self.available_fendian_id_list,
            order_code_mode=self.code_mode,
            is_history=self.is_history,
            reserve_download_record_id=self.record_obj_id,
            file_name=self.file_name,
        )
        print('查询器实例化完毕！ ')
        # 3，先测试 inquirer 的 only_check_count 方法
        is_pass_check_count, msg = inquirer.only_check_count()
        print('only_check_count 校验数量 测试完毕！', is_pass_check_count, msg)
        # 4，再测试 inquirer 的 exec 方法
        print('inquirer 的 order_code_list：', inquirer.order_code_list)
        inquirer.exec()
        print('inquirer.exec() 执行完毕！')
        print('请检查记录对象， ID为', self.record_obj_id, '的任务状态，是否为 7，文件生成完毕')



if __name__ == '__main__':
    test_obj = TestToOrderInquireByCode(dataCount=200, is_history=True, code_mode='platform')
    test_obj.go_test()
