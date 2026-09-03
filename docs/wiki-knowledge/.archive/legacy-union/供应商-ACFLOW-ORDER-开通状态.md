---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-onboarding@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 供应商 ACFLOW/ORDER 开通状态
page_key: 供应商-ACFLOW-ORDER-开通状态
domain: 企业建档
field_targets:
- cust_project_rel.status
---
# 供应商 ACFLOW/ORDER 开通状态

企业角色为 SUPPLIER 且产品为 ACFLOW 或 ORDER 时，cust_project_rel.status 写 '1'，否则 '0'。

```ground:rule
rule: supplier-acflow-status
field_targets:
- cust_project_rel.status
impact: query_constraint
content: 企业角色为 SUPPLIER 且产品为 ACFLOW 或 ORDER 时，cust_project_rel.status 写 '1'，否则 '0'。
scope: 供应商项目关联写入
```

## 关联
- [[cust_project_rel]]
