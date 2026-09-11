---
type: rule
title: 变更前置校验
page_key: change_precondition_check
domain: 企业建档与认证
status: draft
aliases:
  - 在途变更拦截
oid: 1
scope:
  databases: []
sources:
  - code:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
contract_version: "0.1"
---

当企业存在**在途变更流程**时，不允许发起新的变更。判定条件为：存在 `data_type = '2'`（申请数据，见 [[process_apply_data]]）的记录，且该记录的认证状态不在 `BUILD_SUCCESS` / `BUILD_FAIL` 两个终态内（见 [[enterprise_auth_status_machine]]）。

该规则用于防止并发变更，与 [[auth_status_conditional_update]] 一起构成建档/变更链路的并发保护。

```ground:rule
name: 变更前置校验
content: 企业存在在途变更流程（data_type='2' 且 cust_build_status 不在 BUILD_SUCCESS/BUILD_FAIL）时，不允许发起新的变更。
impact: 防止并发变更。
field_targets:
  - data_type
  - cust_build_status
evidence: "code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。