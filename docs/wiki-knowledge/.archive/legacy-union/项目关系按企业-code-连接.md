---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-enterprise-rel@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 项目关系按企业 code 连接
page_key: 项目关系按企业-code-连接
domain: 项目管理
field_targets:
- cust_company_info.code
- cust_project_rel.company_code
---
# 项目关系按企业 code 连接

cust_project_rel 通过 ref_cust_project_rel_cust_company_info 连接 cust_company_info.code，禁止按企业 id 臆造 JOIN。

```ground:rule
rule: join-company-by-code
field_targets:
- cust_company_info.code
- cust_project_rel.company_code
impact: query_constraint
content: cust_project_rel 通过 ref_cust_project_rel_cust_company_info 连接 cust_company_info.code，禁止按企业
  id 臆造 JOIN。
scope: 项目成员、资金方、核心企业查询
```

## 关联
- [[cust_company_info]]
- [[cust_project_rel]]
