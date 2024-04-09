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


- 品检状态 ？ OrderOrder  的 is_checkgoods （无代码）
- 是否发货 ？ ItemStatus 的 sendgoodstype =1 为发货， =0 为未发货， （无代码）

- 员工 ？  OrderFlow 的 owner 和 OrderOrder 的 creator （改为扫码人）
- 平台状态  ？  OrderOrder 中的 autostatus （无代码）
- ~~金额调整 ？ OrderOrder 的 finance_payamount （无代码）（搁置）~~

- 订单情况 ？ OrderOrder 的 status （订单核对状态）（无代码）
    - is_presale  
    - tradetype  交易类型
    - balancetype
    - is_bindgoods
    - is_reorder