---
type: concept
title: 迁移租户
page_key: migratory_tenant
domain: 租户迁移
status: draft
aliases: [migratoryTenant]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
maps_to: "tenant_migarory_log.type = 'migratoryTenant' 或 name = '迁移租户'"
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
belong: concepts
---

“迁移租户”是业务侧对租户级迁移动作的称呼，代码与库中以类型码 `migratoryTenant` 出现，二者为同义关系（adjudication: synonym），在 [[tenant_migarory_log]] 上分别落在 type 与 name 两个字段。取数时不要只匹配其一，口径见 [[migration_tenant_log]]。

## 需求背景

该术语的判定完全依赖 DB 值分布证据（db），未在代码中找到枚举常量定义；因此本页不给出枚举页，字段取值以值分布为准。

## 版本演进

- v0（草稿）：synonym 判定成立，别名集合仅 `migratoryTenant`。

关联页面：[[tenant_migarory_log]]、[[migration_tenant_log]]、[[migratory_project]]、[[migratory_cust]]。