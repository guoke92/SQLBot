---
type: process
title: 运营审核状态机（cust_company_info.check_status）
page_key: cust_check_status_state_machine
domain: 准入接入与接入密钥
status: draft
aliases:
  - 运营中台审核状态机
  - CheckStatus 状态流转
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.java:getCheckStatus
contract_version: "0.1"
belong: processes
---

# 运营审核状态机

## 业务定位

该状态机描述 [[tables/cust_company_info|cust_company_info]] 中 `check_status` 字段的取值与流转，是运营中台侧审核结论在本地库的镜像。取值映射 CheckStatus 枚举，由运营中台回调更新，并进一步驱动 [[processes/cust_build_status_state_machine|企业建档准入状态机]]：审核中/退回/通过/拒绝分别对应建档态向 `CUST_BUILDING`、`CUST_CONFIRM_AWAIT`、`BUILD_SUCCESS`、`BUILD_FAIL` 的迁移。

## 需求背景

审核态与本地建档态必须分开存储与展示：`CUST_CHECK_PASS`（见 [[concepts/check_pass|审核通过]]）与 `BUILD_SUCCESS` 虽在同一业务时点联动，但字段与责任人不同，前端展示映射也不同（`CUST_BACK` 与 `CUST_CHECK_INIT` 映射同一前端状态）。

## 版本演进

给定证据只覆盖 `CUST_CHECK_INIT → CUST_CHECK_CHECKING → {BACKTOCUSTOM, PASS, REJECT}` 四条迁移；`CUST_BACK` 与 `CUST_CHECK_INIT` 是否合并待核对。

```ground:process
name: 运营审核状态机
field: cust_company_info.check_status
states:
  - value: CUST_CHECK_INIT
    label: 初始/退回
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户
    source: code_enum
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_enum
  - value: CUST_BACK
    label: 退回（与CUST_CHECK_INIT映射同一前端状态）
    source: code_enum
transitions:
  - from: CUST_CHECK_INIT
    event: 运营中台审核中
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 退回客户
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 审核通过
    to: CUST_CHECK_PASS
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 审核拒绝
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
```

---REVIEW: process | 运营审核状态机
- `CUST_BACK` 与 `CUST_CHECK_INIT` 的差异（是否历史遗留值）未在证据中说明。
- 退回客户（`CUST_CHECK_BACKTOCUSTOM`）之后重新进入审核中的事件未给出。
---END REVIEW---