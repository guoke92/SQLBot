---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:product-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 两套 open_status 不可混用
page_key: 两套-open_status-不可混用
domain: 产品与配置
field_targets:
- tenant_product.open_status
---
# 两套 open_status 不可混用

tenant_product.open_status（Y/P/N）与 cust_auth_application.open_status（NOT_OPENED/OPENING/OPENED）是两套独立枚举体系；同名不同值域。租户侧查询'已开通'只有 Y；企业侧 OPENED 与 OPENING 都算。

```ground:rule
rule: two-open-status-systems
field_targets:
- tenant_product.open_status
impact: query_constraint
content: tenant_product.open_status（Y/P/N）与 cust_auth_application.open_status（NOT_OPENED/OPENING/OPENED）是两套独立枚举体系；同名不同值域。租户侧查询'已开通'只有
  Y；企业侧 OPENED 与 OPENING 都算。
scope: 按开通状态过滤产品/租户/企业
```

## 关联
- [[tenant_product]]
