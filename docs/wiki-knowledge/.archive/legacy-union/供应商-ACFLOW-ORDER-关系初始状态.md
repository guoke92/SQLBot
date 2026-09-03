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
title: 供应商 ACFLOW/ORDER 关系初始状态
page_key: 供应商-ACFLOW-ORDER-关系初始状态
domain: project-enterprise
field_targets:
- cust_project_rel.company_type
- cust_project_rel.status
- tenant_project.platform_product_code
---
# 供应商 ACFLOW/ORDER 关系初始状态

自动注册保存关系时，company_type=SUPPLIER 且 platform_product_code 为 ACFLOW 或 ORDER 才写 status='1'，否则写 '0'。

```ground:rule
rule: supplier-product-status
field_targets:
- cust_project_rel.company_type
- cust_project_rel.status
- tenant_project.platform_product_code
impact: query_constraint
content: 自动注册保存关系时，company_type=SUPPLIER 且 platform_product_code 为 ACFLOW 或 ORDER
  才写 status='1'，否则写 '0'。
scope: 自主注册无项目码自动绑定、关系状态统计
```

## 关联
- [[cust_project_rel]]
- [[tenant_project]]
