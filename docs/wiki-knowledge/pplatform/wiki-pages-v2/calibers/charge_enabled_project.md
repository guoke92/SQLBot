---
type: caliber
title: 收费项目
page_key: calibers/charge_enabled_project
domain: CA证书收费
status: draft
aliases: [charge_enabled=Y, 已开启收费项目]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_project_config
contract_version: "0.1"
---

# 收费项目

## 业务定位

以[[tables/ca_fee_project_config]]的 `charge_enabled='Y'` 判定，表示该项目已开启 CA 收费。它是[[rules/rule_engine_priority|规则引擎优先级]]的**第一道闸**：项目未开启收费即整体放行，不进入后续豁免与金额判定。业务上回答"这个项目到底收不收 CA 服务费"。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 收费项目
predicate: "ca_fee_project_config.charge_enabled = 'Y'"
scope: ca_fee_project_config
evidence: code
```