---
type: rule
title: 推数产品范围推导
page_key: push_product_scope_deduce
domain: 租户迁移
status: draft
aliases: [产品范围推导, deduceProductCodes]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:MigratoryPointServiceImpl.java#deduceProductCodes"
  - "code:MigratoryPointServiceImpl.java#call"
contract_version: "0.1"
belong: rules
---

未显式指定 `productCodes` 时，用租户已开通产品推导；推租户同步时按平台产品推；企业存在 AMS 经办人或已开 AMS 互通产品时自动追加 AMS。产品码含义见 [[产品编码]]。

```ground:rule
name: 推数产品范围推导
content: "未指定 productCodes 时用租户已开通产品；推租户同步时按平台产品推；企业存在 AMS 经办人或已开 AMS 互通产品时自动追加 AMS"
impact: "决定迁移/推数落到哪些业务系统"
field_targets:
  - tenant_migarory_log.platform_product_code
evidence: "code:MigratoryPointServiceImpl.java#deduceProductCodes,#call"
```

## 需求背景

一个事件可能需同时推给多个业务系统；由调用方逐个指定产品码不可靠，故需服务端按租户开通情况与 AMS 互通情况自动推导。

## 版本演进

由调用方指定演进为服务端推导，并增加 AMS 自动追加逻辑；AMS 分支同时对应 [[ams_migratory_dedup]] 的合并行为。

相关：[[tenant_migarory_log]]、[[outbound_push]]。