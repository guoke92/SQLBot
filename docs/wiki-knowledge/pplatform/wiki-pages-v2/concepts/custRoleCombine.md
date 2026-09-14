---
type: concept
title: custRoleCombine 企业角色组合
page_key: custRoleCombine
domain: 平台产品配置
status: draft
aliases: [custRoleCombine, 企业角色组合, cust_role_combine]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:platform_product.cust_role_combine
maps_to: platform_product.cust_role_combine
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
field_targets: [platform_product.cust_role_combine]
---

custRoleCombine、「企业角色组合」与 `cust_role_combine` 是同一语义，映射到 [[tables/platform_product]] 的 `cust_role_combine`。

边界：该字段为文本格式，需解析为 Set<Set<String>>——外层集合表示可接受的组合，内层集合表示同一组合内的角色集合。判定逻辑见 [[calibers/cust-role-combine-check]] 与 [[rules/cust-role-combine-check]]。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/platform_product]]
- 口径：[[calibers/cust-role-combine-check]]
- 规则：[[rules/cust-role-combine-check]]
- 术语：[[concepts/companyType]]

相关：[[platform_product]]
