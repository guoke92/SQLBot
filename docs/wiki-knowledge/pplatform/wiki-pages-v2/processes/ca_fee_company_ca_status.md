---
type: process
title: CA签章状态机
page_key: ca_fee_company_ca_status
domain: CA证书收费
status: draft
aliases:
  - CA签章状态
  - ca_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code
contract_version: "0.1"
belong: processes
---

CA 签章状态机作用于 [[ca_fee_company]] 的 `ca_status`，**不是**一个由本地业务流驱动的状态机：它是签章中台状态归一化后同步的结果。语义分析中区分了两组取值来源——来自 DB 分布（`db_dist`）的 `NORMAL`／`CANCELLED`／`UNKNOWN`，以及来自代码常量（`code_const`）的 `APPLYING`／`EXPIRED`／`FAIL`；两组的归一化关系在当前证据中缺失，故未给出迁移边。

收费判定只依赖其中三个归一口径：`NORMAL`（[[ca_status_normal]]）、`CANCELLED`（[[ca_status_cancelled]]）、`UNKNOWN`（[[ca_status_unknown]]）。

## 需求背景

CA 状态与收费状态是两条正交语义（见 [[ca_service_fee]] 辨析）：`ca_status` 描述证书有效性，`pay_status` 描述费用缴纳。失效状态会触发提示与重置开通状态，未知状态作为查询失败／未注册的兜底展示。

## 版本演进

- v0（本页）：依据语义分析建立状态清单；`db_dist` 与 `code_const` 两组取值的映射关系未在证据中给出，待补。

```ground:process
name: CA签章状态
field: ca_fee_company.ca_status
states:
  - value: NORMAL
    label: CA正常
    source: db_dist
  - value: CANCELLED
    label: CA注销/作废/失效
    source: db_dist
  - value: UNKNOWN
    label: CA状态未知
    source: db_dist
  - value: APPLYING
    label: CA申请中
    source: code_const
  - value: EXPIRED
    label: CA已过期
    source: code_const
  - value: FAIL
    label: CA申请失败
    source: code_const
transitions: []
```