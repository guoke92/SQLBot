---
type: concept
title: 迁移客户
page_key: migratory_cust
domain: 租户迁移
status: draft
aliases: [migratoryCust]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
maps_to: "tenant_migarory_log.type = 'migratoryCust' 或 name = '迁移客户'"
field_targets:
  - tenant_migarory_log.type
  - tenant_migarory_log.name
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

“迁移客户”是业务侧对客户（企业）级迁移动作的称呼，库中以类型码 `migratoryCust` 出现，二者同义（adjudication: synonym），取数口径见 [[migration_cust_log]]。该术语同时对应代码入口 `PlatFormMigratoryApplication.java:migratoryCust`，是同一动作在库与代码两侧的命名。

## 需求背景

客户迁移不仅写 [[tenant_migarory_log]]，还会初始化 [[migratory_user_record]] 并处理企业已存在时的合并分支，相关规则见 [[migratory_user_record_init]]、[[ams_company_merge]]、[[company_sync_lock]]。

## 版本演进

- v0（草稿）：DB 侧 synonym 判定成立；代码侧入口为 `PlatFormMigratoryApplication.java:migratoryCust`。

关联页面：[[tenant_migarory_log]]、[[migration_cust_log]]、[[existing_user]]。