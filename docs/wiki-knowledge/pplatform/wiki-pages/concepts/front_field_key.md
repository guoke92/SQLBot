---
type: concept
title: 前端字段key
page_key: front_field_key
domain: 资金方规则与异常解决
status: published
aliases:
  - frontKey
  - ruleKey
  - key_name
oid: 1

sources:
  - db:funding_rule_front_cfg
  - db:funding_rule_detail
maps_to: "funding_rule_front_cfg.front_key / funding_rule_detail.rule_key"
field_targets:
  - funding_rule_front_cfg.front_key
  - funding_rule_detail.rule_key
adjudication: "synonym"
also_confused_with:
  - funding_rule_front_cfg.rule_key
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

前端字段key 是规则配置中连接前端展示层与后端存储层的桥梁。[[funding_rule_detail]] 表的 rule_key 字段关联 [[funding_rule_front_cfg]] 表的 front_key 字段，用于确定规则明细对应的前端配置项。

## 需求背景

前端动态渲染规则配置时，每个可配置项都需要一个稳定标识。detail.rule_key 关联 front_cfg.front_key 实现这一映射。front_cfg.key_name 为展示名称，而 front_cfg.rule_key 为另一字段，与 front_key 用途不同。

## 版本演进

边界说明：detail.rule_key 关联 front_cfg.front_key；front_cfg.key_name 为展示名称，front_cfg.rule_key 为另一字段，可能用于前端渲染规则。当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。