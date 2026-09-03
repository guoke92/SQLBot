---
type: rule
title: 企业状态操作合法性检查
page_key: company-status-operation-legal-check
domain: 企业建档与准入
status: published
aliases: [状态操作合法性检查]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_status]
scope:
  databases: [lowcode_pplatform]
---

# 企业状态操作合法性检查

本规则要求冻结/解冻/注销操作时检查当前客户状态是否在允许列表中，非法状态操作抛出异常。

## 需求背景

企业生命周期状态操作（冻结、解冻、注销）需要合法状态前置检查，防止非法跳转，保证 [[customer-lifecycle-status-machine]] 的完整性。

## 版本演进

证据来自代码路径 `CustCompanyInfoApplication.custStatusOperator`。

```ground:rule
name: 企业状态操作合法性检查
content: 冻结/解冻/注销操作时检查当前客户状态是否在允许列表中
impact: 非法状态操作抛出异常
field_targets:
  - cust_company_info.cust_status
evidence: "code_path:CustCompanyInfoApplication.custStatusOperator"
```

相关表：[[cust_company_info]]；相关概念：[[freeze]]