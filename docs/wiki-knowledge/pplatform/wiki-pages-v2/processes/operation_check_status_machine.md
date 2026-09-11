---
type: process
title: 运营审核状态机（check_status）
page_key: operation_check_status_machine
domain: 企业建档与认证
status: draft
aliases:
  - check_status 流转
  - 运营中台审核状态机
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:submitCust
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:reSubmit
  - db:cust_company_info.check_status
contract_version: "0.1"
---

本流程描述 `cust_company_info.check_status`（见 [[check_status]]）的流转，表达**运营中台对单次提交的审核结果**，与企业的整体认证状态（[[enterprise_auth_status_machine]]）不是同一维度：前者是一次审核的结果，后者是建档全过程的状态，边界说明见 [[auth_status]]。

流转主干为：初始化 → 审核中 → 审核通过 / 退回客户；退回客户后客户可重新提交再次进入审核中。审核中同时进入认证状态机的“认证中”，审核通过 / 退回会驱动认证状态迁移为认证成功 / 待客户确认。

```ground:process
name: 运营审核状态机
field: check_status
states:
  - value: CUST_CHECK_INIT
    label: 初始化
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: db_dist
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户
    source: code_enum
  - value: EFFECT
    label: 生效
    source: db_dist
transitions:
  - from: CUST_CHECK_INIT
    event: 提交运营中台审核
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: CUST_CHECK_CHECKING
    event: 运营审核通过
    to: CUST_CHECK_PASS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CHECK_CHECKING
    event: 运营审核退回
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CHECK_BACKTOCUSTOM
    event: 客户重新提交
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java:reSubmit"
```

## 需求背景

暂无需求文档主张。注意该状态集合中同时出现审核语义（`CUST_CHECK_*`）与生命周期语义（`EFFECT`），且 `CUST_CHECK_CHECKING`、`EFFECT` 来源于数据库分布而非代码枚举，说明该字段可能存在语义混用或多来源写入。

## 版本演进

- v0.1：依据语义分析建立状态机页，登记 6 个状态（4 个代码枚举值 + 2 个数据库分布值）与 4 条流转及其代码证据。