---
type: caliber
title: 批量查询条数上限口径
page_key: batch_query_limit
domain: 外部渠道与银行对接
status: draft
aliases:
  - 批量查询条数上限口径
  - batchQuery 100
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#batchQuery
contract_version: "0.1"
belong: calibers
---

# 批量查询条数上限口径

## 业务定位

该口径规定标准开放接口批量查询 `batchQuery` 的单次入参条数上限为 100 条（`size(queryReqs) <= 100`），是接口层的入参校验约束。

## 需求背景

批量查询要在全租户上下文（[[calibers/all_tenant_context]]）下按企业维度展开，单次条数不设上限会放大跨租户检索的压力；100 条是当前代码中唯一可确认的阈值。渠道接入方需按此上限拆分请求。

## 版本演进

- v0.1（本页首版）：阈值来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 批量查询条数上限口径
predicate: "size(queryReqs) <= 100"
scope: batchQuery 入参校验
evidence: "code:CustAccessApplication#batchQuery"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/all_tenant_context]]、[[calibers/cust_company_info_enable_active]]
- 规则：[[rules/nonstandard_inbound_all_tenant]]