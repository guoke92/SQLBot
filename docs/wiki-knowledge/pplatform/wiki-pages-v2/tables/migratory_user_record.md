---
type: table
title: migratory_user_record（迁移用户记录表）
page_key: migratory_user_record
domain: 租户迁移
status: draft
aliases: [迁移用户记录, 存量用户记录表]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
contract_version: "0.1"
---

migratory_user_record 记录“哪些用户是迁移来的存量用户”。它把用户（user_id，关联企业人员）与数据租户（db_tenant_code）绑定，并用 is_login 与 enable 两个标志位驱动登录后的升级提示逻辑。它是 [[existing_user]] 这一术语在数据上的落点，也是 [[migratory_user_login_state]] 状态机与 [[eject_msg_once]] 规则的载体。



## 需求背景

本表的存在意义是为“迁移用户登录后只弹一次升级消息”提供幂等依据：弹出由 is_login 的 N→Y 翻转来去重，见 [[eject_msg_once]] 与 [[migratory_user_not_login]]。user_id 与 db_tenant_code 的语义来自代码证据，说明本表由迁移客户流程（`PlatFormMigratoryApplication.java:migratoryCust`）写入，而非独立维护的配置表。

## 版本演进

- v0（草稿）：字段语义来自 db（is_login / enable）与 code（user_id / db_tenant_code）两类证据；记录初始化行为不在本页展开，归入 [[migratory_user_record_init]]。

关联页面：[[migratory_user_login_state]]、[[existing_user]]、[[eject_msg_once]]。