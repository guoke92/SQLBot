---
type: concept
title: "租户标识"
page_key: tenant_code
belong: concepts
domain: gpt_learn
status: published
aliases: ["tenant code", "租户编码"]
oid: 1

sources: ["semantic_analysis.term_bridges", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "db_tenant_code（数据租户标识）；app_tenant_code（逻辑租户标识）"
field_targets: []
adjudication: "boundary"
also_confused_with: ["app_tenant_code"]
scope:
  databases: [lowcode_pplatform]
---

# 租户标识

租户标识涉及两种编码：db_tenant_code（数据租户标识）和 app_tenant_code（逻辑租户标识）。当前业务中弹卡白名单与埋点记录使用 db_tenant_code，app_tenant_code 未参与本模块业务判断。

## 需求背景

需要区分数据租户和逻辑租户，避免混淆，明确业务使用边界。

## 版本演进

- v0.1: 初始版本，来源于术语桥接分析。

## 关联

- [[gpt_learn_poster_log]] 表字段 db_tenant_code 和 app_tenant_code。
- [[cust_company_info]] 表字段 db_tenant_code。
- [[tenant_whitelist_rule]] 使用 db_tenant_code。
```