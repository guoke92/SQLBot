---
type: concept
title: 企业ID
page_key: company_id
belong: concepts
domain: 支付宝蚂蚁档案与清算
status: published
aliases: ["companyId", "operator.companyId"]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: company_id
field_targets: []
adjudication: synonym
also_confused_with: ["outerSerialNo", "businessNo"]
scope:
  databases: [lowcode_pplatform]
---

企业ID 明确指企业主数据 ID，用于标识租户或企业实体。区别于流水号（outerSerialNo）和业务号（businessNo），不可混淆。

## 需求背景

支付宝清分查询、客户端查询等场景均依赖企业ID 定位租户数据，必填约束保证查询能够精确定位。

## 版本演进

初始定义，暂无变更。边界说明来自语义分析 term_bridges。

[[tables/ProjectAlipayClearingConfigQryDTO]] [[rules/支付宝清分配置查询企业ID必填]] [[rules/客户端查询平台产品编码必填]]