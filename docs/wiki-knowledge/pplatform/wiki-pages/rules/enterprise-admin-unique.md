---
type: rule
title: 企业管理员唯一性
page_key: enterprise-admin-unique
domain: 企业建档与准入
status: published
aliases: [管理员唯一性校验]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.company_type, cust_person_info.ref_cust_company_info, cust_person_info.user_type]
scope:
  databases: [lowcode_pplatform]
---

# 企业管理员唯一性

本规则要求同一企业下同一角色类型只能有一个有效管理员，新增或变更管理员时校验，违反则抛异常。

## 需求背景

企业管理员承担主账号职责，唯一性保证管理职责清晰。该规则依赖 `user_type`、`company_type`、`ref_cust_company_info` 三个字段组合判断。

## 版本演进

证据来自代码路径 `CustPersonApplication.checkBeforeSave`。

```ground:rule
name: 企业管理员唯一性
content: 同一企业下同一角色类型只能有一个有效管理员
impact: 新增或变更管理员时校验，违反则抛异常
field_targets:
  - cust_person_info.user_type
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
evidence: "code_path:CustPersonApplication.checkBeforeSave"
```

相关表：[[联系人_客户人员]]；相关概念：[[admin]]

相关：[[cust_person_info]]
