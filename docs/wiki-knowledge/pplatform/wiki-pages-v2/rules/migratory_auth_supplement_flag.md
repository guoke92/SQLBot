---
type: rule
title: 迁移授权书补签标记
page_key: migratory_auth_supplement_flag
domain: 租户迁移
status: draft
aliases: [授权书补签标记写入]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
belong: rules
---

迁移时按渠道新旧决定是否展示授权书补签入口：新渠道无需补签，旧渠道需补签。两侧标记成对写入，互为反向。

```ground:rule
name: 迁移授权书补签标记
content: "newAuthAggrementFlag=true → migarory_auth_aggrement_flag=Y 且 auth_aggrement_supplement_flag=N；false → N 且 Y"
impact: "控制旧渠道企业是否展示授权书补签入口"
field_targets:
  - cust_company_info.migarory_auth_aggrement_flag
  - cust_company_info.auth_aggrement_supplement_flag
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

新渠道迁移时已具备合法授权书，旧渠道存量企业的授权书需要客户补签，因此迁移落库时就应决定入口是否展示，而不是等客户操作时再判断。

## 版本演进

由"全部展示补签入口"演进为按渠道标记区分；标记来源于上游 `newAuthAggrementFlag`。

相关：[[cust_company_info]]、[[pending_agreement_pull]]。