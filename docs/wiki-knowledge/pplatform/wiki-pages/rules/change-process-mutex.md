---
type: rule
title: 变更流程互斥
page_key: change-process-mutex
belong: rules
domain: 企业建档与准入
status: published
aliases: [变更互斥]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_build_status, cust_company_info.data_type]
scope:
  databases: [lowcode_pplatform]
---

# 变更流程互斥

本规则规定存在在途变更流程时不允许再次发起变更，防止并发变更。

## 需求背景

企业变更流程涉及企业资料修改，在途流程互斥可避免数据冲突和状态混乱。该规则基于 [[in-transit-process]] 口径判断在途状态。

## 版本演进

证据来自代码路径 `ApplyCompanyInfoApplication.judgeHaveApplyingRecord`。

```ground:rule
name: 变更流程互斥
content: 存在在途变更流程时不允许再次发起变更
impact: 防止并发变更
field_targets:
  - cust_company_info.data_type
  - cust_company_info.cust_build_status
evidence: "code_path:ApplyCompanyInfoApplication.judgeHaveApplyingRecord"
```

相关表：[[cust_company_info]]；相关口径：[[in-transit-process]]