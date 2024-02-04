from enum import Enum


# 订单金额核对状态
class OrderCheckedStatus(Enum):
    DELETED = '0'  # 已删除
    UNCERTIFIED = '1'  # 待核对
    CERTIFIED = '2'  # 已核对
    VERIFY_ERROR = '3'  # 核对有误
    MANUAL_CERTIFIED = '4'  # 人工已核对
    SYSTEM_CERTIFIED = '5'  # 系统已核对
    FINANCE_CERTIFIED = '6'  # 财务已核对


# 订单流程状态
class OrderFlowStatus(Enum):
    SYNC_NOT_STARTED = '1'  # 暂未同步
    ORDER_REFUNDED = '2'  # 订单退款
    TRANSACTION_SUCCESSFUL = '3'  # 交易成功
    REFUND_CREATED = '4'  # 退款创建
    REFUND_CLOSED = '5'  # 退款关闭
    ORDER_DELIVERED = '7'  # 订单发货
    TRANSACTION_CLOSED = '8'  # 交易关闭
    WAITING_FOR_DELIVERY = '9'  # 等待发货
    WAITING_FOR_PAYMENT = '10'  # 等待付款
    PARTIAL_REFUND = '11'  # 部分退款
    NEW_ORDER = '12'  # 新增订单
    ORDER_NOT_REFUNDED = '13'  # 订单未退
