---
type: rule
title: 状态更新乐观匹配
page_key: status_update_optimistic_match
domain: 企业建档与认证
status: draft
aliases:
  - 状态更新前置条件
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
belong: rules
---

更新 `cust_build_status` 时，写条件要求 before 状态、`enable='Y'`、主数据标识同时匹配；任一不满足则更新 0 行，状态不会被覆盖。

```ground:rule
name: 状态更新乐观匹配
content: 更新 cust_build_status 时要求 before 状态、enable=Y、data_type=主数据同时匹配，否则更新 0 行
impact: 并发/脏数据下状态不被覆盖
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.enable
  - cust_company_info.data_type
evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
```

## 需求背景

状态机迁移由消息回调与运营中台审核共同驱动，存在并发与重复投递的可能。以"期望前置状态"作为更新条件，可以保证迁移只在合法起点上发生，也让 [[processes/cust_build_status_state_machine]] 的迁移表具有可验证性。

## 版本演进

v0 初稿：以 `updateCustBuildStatus` 的实现固化。更新 0 行时的补偿/告警策略未在给定证据中体现。

关联：[[calibers/main_data_judgment]]、[[processes/cust_build_status_state_machine]]。