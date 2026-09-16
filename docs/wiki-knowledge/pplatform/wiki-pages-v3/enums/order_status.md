---
type: enum
title: order_status
page_key: order_status
domain: CA证书收费
status: draft
aliases: [订单状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeOrderStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [ca_fee_order_status]
---

# order_status

[[ca_fee_order]] 的 `order_status`。代码枚举 `CaFeeOrderStatusEnum`（displayName 如下），流转见 [[ca_fee_order_status]]。

与企业 [[pay_status]] 同名 `PAID` 不是同一列：订单未缴是 `PENDING`，企业未缴是 `UNPAID`。

`EXPIRED`（已过期）在枚举和 `@ApiModelProperty` 里都有，但 `CaFeeOrderService` 只写入 `PENDING` / `PAID` / `CLOSED`，没有任何 `EXPIRED` 赋值；库分布也是 0。不是废弃字段，是声明了却未落地。

库里另有 `PAIDING` 1 条、`UNPAID` 1 条，代码枚举没有这两值，也没有写入路径。`UNPAID` 与企业缴费状态同名，不能当成订单状态用。

```ground:enum
enum: order_status
fields: [ca_fee_order.order_status]
values:
  "PENDING":
    label: "未缴费"
  "PAID":
    label: "已缴费"
  "CLOSED":
    label: "已关闭"
  "EXPIRED":
    label: "已过期"
    note: "枚举已声明；无写入路径，库分布 0"
  "PAIDING":
    note: "库中 1 条；代码枚举未声明，无写入路径"
  "UNPAID":
    note: "库中 1 条；代码枚举未声明。UNPAID 是企业 pay_status 的值"
```
