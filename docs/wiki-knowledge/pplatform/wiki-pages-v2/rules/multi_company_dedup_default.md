---
type: rule
title: 多公司列表去重取默认
page_key: multi_company_dedup_default
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 多公司去重
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getCurrentCustList
contract_version: "0.1"
belong: rules
---

用户拥有多家公司时，当前企业列表需按 (companyId + companyType) 去重，重复取默认记录。

## 需求背景

同一企业在多角色下只展示一条，默认企业优先，避免选择公司与后续企业上下文写入
（[[login_init_cookie]]）出现歧义。

## 版本演进

- v0（草稿）：规则来自代码去重逻辑。

```ground:rule
name: 多公司列表去重取默认
content: "getCurrentCustList 按 (companyId+companyType) 去重，重复时取 default_flag='Y' 的记录，其余取首条。"
impact: "同一企业在多角色下只展示一条，默认企业优先。"
field_targets:
  - cust_company_info.id
  - cust_company_info.cust_company_type
evidence: "code_path:SaaSAuthController.java:getCurrentCustList"
```

相关：[[cust_company_info]]、[[login_init_cookie]]。