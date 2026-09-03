---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:person-user@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 联系人按企业 code 连接
page_key: 联系人按企业-code-连接
domain: 企业建档
field_targets:
- cust_company_info.code
- cust_person_info.company_code
---
# 联系人按企业 code 连接

ref_cust_company_info 连接 cust_company_info.code，禁止按企业 id 臆造 JOIN。

```ground:rule
rule: person-join-by-code
field_targets:
- cust_company_info.code
- cust_person_info.company_code
impact: query_constraint
content: ref_cust_company_info 连接 cust_company_info.code，禁止按企业 id 臆造 JOIN。
scope: 企业用户、管理员
```

## 关联
- [[cust_company_info]]
- [[cust_person_info]]
