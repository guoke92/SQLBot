---
type: concept
title: 迁移批次
page_key: migration_batch
domain: 租户迁移
status: published
aliases: [批次号]
oid: 18
maps_to: "tenant_migarory_log.batch_no"
field_targets: [tenant_migarory_log.batch_no]
adjudication: synonym
also_confused_with: []
boundary: ""
sources: [db]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：迁移批次号，对应 tenant_migarory_log.batch_no。

## 需求背景
迁移采用分批次、可控策略（document_claim，未证实）——DB:tenant_migarory_log.batch_no 存在，但给定代码未展示批次控制调度。

## 版本演进
v0.1 术语同义，基于 DB 字段。

关联：[[tenant_migarory_log]]