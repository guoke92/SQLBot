---
type: process
title: 客户生命周期状态机
page_key: customer-lifecycle-status-machine
domain: 企业建档与准入
status: published
aliases: [客户状态机, cust_status状态机]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户生命周期状态机

本状态机跟踪 `cust_company_info.cust_status` 的客户生命周期阶段，包括新增、生效、冻结、注销、变更中。认证通过后从 ADD 转为 EFFECT，冻结与解冻为可逆操作，注销为终态 WRITEOFF。

## 需求背景

客户状态与认证状态分离：`cust_build_status` 关注认证流程，`cust_status` 关注客户生效后的生命周期管理。冻结操作见 [[freeze]] 概念辨析。

## 版本演进

来源代码路径包括 `CustCompanyInfoApplication.updateCustBuildStatus`、`CustCompanyInfoApplication.freeze`、`CustCompanyInfoApplication.unfreeze`、`CustCompanyInfoApplication.diable` 等。

```ground:state_machine
name: 客户生命周期状态机
field: cust_status
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: code_enum
transitions:
  - from: ADD
    event: 认证通过
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.updateCustBuildStatus 当 after==BUILD_SUCCESS 时更新 cust_status=EFFECT"
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.freeze 调用 custStatusOperator 更新状态"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.unfreeze 调用 custStatusOperator 更新状态"
  - from: EFFECT
    event: 注销
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.diable 调用 custStatusOperator 更新状态"
  - from: EFFECT
    event: 发起变更
    to: CHANGE
    evidence: "code_path:CustCompanyInfoApplication.submitForSimpleAuth 或变更流程中设置 cust_status=CHANGE（需进一步确认）"
```

相关表：[[cust_company_info]]；相关口径：[[effective-company]]