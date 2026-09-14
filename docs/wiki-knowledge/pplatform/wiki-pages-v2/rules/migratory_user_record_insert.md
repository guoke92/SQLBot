---
type: rule
title: 迁移用户记录落库
page_key: migratory_user_record_insert
domain: 租户迁移
status: draft
aliases: [迁移用户记录写入, is_login 初值 N]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
belong: rules
---

人员落库后按 `user_id + db_tenant_code` 查 [[migratory_user_record]]，不存在则插入并置 `is_login='N'`。这条写入是首登提示状态机的来源动作，见 [[migratory_user_login_prompt]]。

```ground:rule
name: 迁移用户记录落库
content: "人员落库后，按 user_id+db_tenant_code 查 migratory_user_record，不存在则插入并置 is_login='N'"
impact: "为『首登弹升级提示、仅弹一次』提供判定依据"
field_targets:
  - migratory_user_record.user_id
  - migratory_user_record.db_tenant_code
  - migratory_user_record.is_login
evidence: "code:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

存量用户首次登录（当前迁移批次内）弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，一个用户仅弹一次；因此迁移时须为每个迁移人员预置未登录记录。

## 版本演进

记录仅在不存在时插入（已存在不重置为 N），保证"只弹一次"不被重复迁移破坏；品牌名取自 [[贴牌]]。

相关：[[migratory_user_first_login]]、[[tenant_code]]。