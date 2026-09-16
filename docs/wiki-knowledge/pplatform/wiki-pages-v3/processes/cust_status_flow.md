---
type: process
title: 企业状态机
page_key: cust_status_flow
domain: 企业建档与认证状态机
status: draft
aliases: [企业状态流转]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCompanyInfoApplication.java", "code:CustChangeApplication.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [cust_company_info.cust_status]
---

作用于 [[cust_company_info]] 的 `cust_status`（字典 [[cust_status]]）。建档成功推动 `ADD → EFFECT`；发起变更进入 `CHANGE`；冻结/解冻/注销只在本列发生。有效企业口径见 [[effective_company]]，变更中见 [[in_change_company]]。`FAILURE` 在枚举中，当前没有迁入证据。

```ground:process
name: 企业状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: CHANGE
    label: 变更
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: FAILURE
    label: 失效
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
  - from: EFFECT
    event: 发起企业变更
    to: CHANGE
    evidence: "code_path:CustCompanyInfoApplication.java:doIfNecessaryChange"
  - from: EFFECT
    event: 冻结企业
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻企业
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```
