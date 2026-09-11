---
type: rule
title: 冻结企业同时冻结管理员
page_key: freeze_company_freezes_admin
domain: 企业建档与认证
status: draft
aliases:
  - 企业冻结连带管理员
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:freeze
contract_version: "0.1"
---

冻结企业（`cust_status` 置为 `FREEZE`，见 [[customer_status_machine]]）时，系统同时冻结该企业下的管理员用户，使管理员无法登录。这是一条**企业状态对用户状态的级联约束**，说明客户状态变更的影响范围不限于企业实体本身。

```ground:rule
name: 冻结企业同时冻结管理员
content: 冻结企业时，同时冻结该企业下的管理员用户。
impact: 管理员无法登录。
field_targets:
  - cust_status
evidence: "code_path:CustCompanyInfoApplication.java:freeze"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。