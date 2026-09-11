---
type: rule
title: 迁移人员记录初始化
page_key: migratory_user_record_init
domain: 租户迁移
status: draft
aliases: [迁移用户记录初始化, migratory_user_record 建档]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
contract_version: "0.1"
---

本规则保证每一位被迁移过来的人员都有一条可追踪的迁移用户记录，且初始状态一定是“未登录”，为后续登录弹窗的一次性判断提供入口。

```ground:rule
name: 迁移人员记录初始化
content: 迁移客户时，对保存的人员，若 migratory_user_record 中不存在该用户在该租户下的记录，则创建记录，is_login 初始化为 'N'。
impact: 迁移用户跟踪
field_targets:
  - migratory_user_record
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

## 需求背景

初始化动作与 [[eject_msg_once]]、[[migratory_user_not_login]] 构成完整链路：迁移时建档（N）→ 登录时命中口径 → 弹出并翻转为 Y → 不再弹。去重键为“用户 + 租户”，与 [[migratory_user_record]] 的 user_id、db_tenant_code 字段对应。

## 版本演进

- v0（草稿）：规则来自代码证据；同一用户跨租户迁移时会各建一条记录，此行为符合当前映射，未观察到跨租户去重。

关联页面：[[migratory_user_record]]、[[existing_user]]、[[migratory_user_login_state]]、[[ams_company_merge]]。