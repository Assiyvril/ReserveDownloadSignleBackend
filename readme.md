# 预约导出

## 2024-04-08 完全复刻“直播订单”模块的筛选条件

### 新增的筛选条件

- 货主   OrderOrder 中的 shipper
- 主播   OrderOrder 中的 zhubo    ||   OrderOrder -> OrderPlay -> zhubo
- 扫码状态   OrderOrder 中的  item_status
- 货品分类  OrderOrder 中的  category
- 班次   OrderOrder -> OrderPlay -> classs （LiveShiftSchedule 直播排班）
- 链接类型 （固定 or 闪购） OrderOrder 中的  is_guding_url 为 1 的是固定链接，为 0 的是闪购链接
- 证书情况 （有证书 or 无证书） OrderOrder 中的 is_zhengshu 为 1 的是有证书，为 0 的是无证书
- 市场专员  OrderOrder -> OrderPlay -> shichangzhuanyuan
- 是否发货 ？ ItemStatus 的 sendgoodstype =1 为发货， =0 为未发货， （无代码）

- 员工 ？  OrderFlow 的 owner 和 OrderOrder 的 creator （改为扫码人）




- 品检状态 ？ OrderOrder  的 is_checkgoods （无代码） 
品检合格   check1  is_checkgoods = 1
不合格 check2  is_checkgoods = 2
不合格入库  check3 is_checkgoods = 3
未品检 check0  is_checkgoods = 0



- 平台状态  ？  OrderOrder 中的 autostatus （无代码）
订单未退 a1,  autostatus ！= 2
订单退款 a2,  autostatus = 2
部分退款 a3,  autostatus = 11


- 订单情况 ？ OrderOrder 的 status （订单核对状态）（无代码） 直播订单模块中的 isdelete
    - is_presale  
    - tradetype  交易类型
    - balancetype
    - is_bindgoods
    - is_reorder

正常订单  d1    order_order.status  ！= '0'
被删订单  d2    order_order.status='0'
预售订单  d3    order_order.status<>'0' and order_order.is_presale=true
超福订单  d4    order_order.status<>'0' and order_order.tradetype=1
线下发货  d5    order_order.status<>'0' and (order_order.tradetype=0 or  order_order.tradetype isnull) and order_order.amount<=30
成本结算  d6    order_order.status<>'0' and order_order.balancetype=2
扣点结算  d7    order_order.status<>'0' and (order_order.balancetype<>2 or order_order.balancetype isnull
特殊订单  d8    order_order.status<>'0' and order_order.tradetype=2
需绑货品  d9    and order_order.status<>'0' and order_order.is_bindgoods=true
重录订单  d10   and order_order.status<>'0' and order_order.is_reorder=1


# 04-22 字段梳理
## 目前留空的

扫码历史      大哥也空
品检状态      大哥也空
品检类型      大哥也空
品检备注      大哥也空
品检人       大哥也空
品检时间      大哥也空
预售订单      大哥也空
待结ID        大哥也空
结扣ID        大哥也空
结算ID        大哥也空
成本导入时间      大哥也空
录单员           大哥也空
交易截图        大哥也空
标题货品码       大哥也空


代购费      order.fee
证书费      order.certificate
绳子费      order.shengzi
盒子费      order.box
其它        order.other
多付金额     order.overage
图片地址     QiDeBaoOrderInfo(order_qdborderlist 启德宝订单信息表) 的 picurl
备注        order.desc
自动状态     order.autostatus
订单创建时间    order.created_time
证书           order.is_zhengshu 有或无
发货记录        order.sendgoodstype  
货主备注        order.shipper_memo
场次ID         order.play__id
班次时间        order-->play-->classs  start_time - end_time
是否打印        order.printstatus

流程最近更新者    ? orderFlow.owner

客户昵称    ？
成本金额    ？
附加扣款    ？
附加补款    ？
货主证书    ？
利润       ？
扣点调否    ？
调扣ID     ？  
差异扣点    ？
售后金额    ？
系统状态    ？
退款金额    ？
退款状态    ？
订单更新时间   ?
支付方式      ?
是否加帐      ?
拉新专员      ?
杂项支出      ?
销售专员      ?
转粉专员      ?
关联店铺      ?