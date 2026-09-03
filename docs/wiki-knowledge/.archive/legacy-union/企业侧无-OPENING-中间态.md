---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking-products@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 企业侧无 OPENING 中间态
page_key: 企业侧无-OPENING-中间态
domain: 产品与配置
field_targets:
- cust_interworking_product.open_status
---
# 企业侧无 OPENING 中间态

cust_interworking_product.open_status 只有 OPENED 一种写值（查询即开通模式，授权通过直接终态）；无 OPENING/NOT_OPENED。前端展示的 OPENING 是未开通的展示态非落库值。

```ground:rule
rule: no-opening-intermediate
field_targets:
- cust_interworking_product.open_status
impact: query_constraint
content: cust_interworking_product.open_status 只有 OPENED 一种写值（查询即开通模式，授权通过直接终态）；无
  OPENING/NOT_OPENED。前端展示的 OPENING 是未开通的展示态非落库值。
scope: 互通产品开通率统计
```

## 关联
- [[cust_interworking_product]]
