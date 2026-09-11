---
type: process
title: 收费协议签署状态机
page_key: processes/ca_fee_agreement_sign
domain: CA证书收费
status: draft
aliases: [agreement_signed 状态机, 协议签署状态流转]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeeAgreementApplication.java
contract_version: "0.1"
---

# 收费协议签署状态机

## 业务定位

本页描述[[tables/ca_fee_order]]中 `agreement_signed` 的 Y/N 两态：`N`（未签署）→ 经签署动作 `signAgreement` → `Y`（已签署）。该标志是**支付的前置门槛**，与 `order_status='PENDING'` 一起构成[[rules/payment_precondition_rule]]的准入条件；不满足即无法发起交e保划扣。

签署时会绑定协议版本号（`agreement_version`，如 V1.0）与签署时间（`agreement_sign_time`），签章后的协议文件存放在 COS 路径（`agreement_file_path`）。可统计口径见[[calibers/agreement_signed_order]]。状态取值来自库分布（`db_dist`），代码中未声明为枚举。

## 需求背景

本页为代码侧签署动作与库侧取值的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。协议版本号与协议模板的治理关系（模板升级是否回溯存量订单）无证据，不做断言。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: 收费协议签署状态机
field: ca_fee_order.agreement_signed
states:
  - value: N
    label: 未签署
    source: db_dist
  - value: Y
    label: 已签署
    source: db_dist
transitions:
  - from: N
    event: 签署收费协议 signAgreement
    to: Y
    evidence: "code_path:CaFeeAgreementApplication.java:signAgreement"
```