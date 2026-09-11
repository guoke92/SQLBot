---
type: table
title: ca_fee_order CA服务费订单表
page_key: tables/ca_fee_order
domain: CA证书收费
status: draft
aliases: [CA服务费订单, 缴费订单, ca_fee_order]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeePaymentApplication.java
  - code:CaFeeOrderApplication.java
contract_version: "0.1"
---

# ca_fee_order CA服务费订单表

## 业务定位

`ca_fee_order` 是 CA 证书收费的交易单据表：一次首次缴费、到期续费或存量补录对应一条订单，记录**应缴年费、实缴金额、支付方式、收费协议签署信息与交e保划扣流水号**。订单是本域唯一的"付款凭据"，企业侧的账期状态（[[tables/ca_fee_company]]）在订单支付成功后回写。

订单类型区分首次与续费场景（`order_type`），订单状态流转见[[processes/ca_fee_order_state]]。发起支付前必须满足[[rules/payment_precondition_rule|支付前置条件规则]]：订单处于 `PENDING` 且 `agreement_signed='Y'`；协议签署状态自身的流转见[[processes/ca_fee_agreement_sign]]。交e保（[[concepts/bocom]]）是当前唯一支付渠道，其划扣结果落在 `bocom_txn_sts`，对应口径[[calibers/bocom_success]]、[[calibers/bocom_pending_investigation]]、[[calibers/bocom_failure]]。

注意 `order_status` 存在**代码枚举与实际库值不一致**的情况：代码声明 `PENDING/PAID/CLOSED/EXPIRED`，而库中实际出现 `PAIDING`、`UNPAID` 等超出枚举的值。统计口径请以口径页明确取值，不要直接按代码枚举枚举全集。

## 需求背景

本页字段语义来自库表与代码两侧证据，本次语义分析未提供需求文档主张（reqdoc 锚点），故无"双源"证据条目。关开关、手动关闭、服务到期三类关闭原因的业务触发见[[processes/ca_fee_order_state]]与[[rules/renew_remind_rule]]。

## 版本演进

- 本次语义分析未提供与本表相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:columns
table: ca_fee_order
columns:
  - field: order_status
    meaning: 订单状态：PENDING 未缴费 / PAID 已缴费 / CLOSED 已关闭 / EXPIRED 已过期（代码枚举）；DB 实际存在 PAIDING、UNPAID 等超出枚举的值
    evidence: db
  - field: order_type
    meaning: 订单类型：FIRST 首次缴费 / RENEW 即将到期续费 / RENEW_EXPIRED 已到期续费 / STOCK 存量补录
    evidence: code
  - field: annual_fee
    meaning: 应缴年费（元）
    evidence: db
  - field: pay_amount
    meaning: 实缴金额（元）
    evidence: code
  - field: pay_method
    meaning: 支付方式，当前为 BOCOM（交e保）
    evidence: code
  - field: agreement_signed
    meaning: 是否已签署收费协议：Y/N
    evidence: db
  - field: agreement_version
    meaning: 签署时绑定的收费协议版本号，如 V1.0
    evidence: db
  - field: agreement_sign_time
    meaning: 收费协议签署时间
    evidence: db
  - field: agreement_file_path
    meaning: 签章后协议文件 COS 路径
    evidence: db
  - field: bocom_txn_sts
    meaning: 交e保交易状态：00 成功 / 01 失败 / 02 待查证等
    evidence: db
  - field: bocom_plfm_ser_no
    meaning: 交e保平台流水号
    evidence: db
  - field: bocom_plfm_bsn_id
    meaning: 平台业务编号
    evidence: db
  - field: bocom_req_sn
    meaning: 请求流水号
    evidence: db
  - field: invoice_status
    meaning: 发票状态：NONE/PENDING/ISSUED/FAILED
    evidence: code
  - field: close_reason
    meaning: 关闭原因（关开关/手动关闭/服务到期等）
    evidence: db
  - field: company_type
    meaning: 企业角色：SUPPLIER/CORE/PROJECT_COMPANY
    evidence: db
```

相关口径：[[calibers/pending_order]]、[[calibers/paid_order]]、[[calibers/agreement_signed_order]]、[[calibers/bocom_success]]、[[calibers/bocom_pending_investigation]]、[[calibers/bocom_failure]]。