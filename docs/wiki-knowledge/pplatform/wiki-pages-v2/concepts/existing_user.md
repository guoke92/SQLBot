---
type: concept
title: 存量用户
page_key: existing_user
domain: 租户迁移
status: draft
aliases: [迁移用户]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
maps_to: "migratory_user_record 中记录的用户"
field_targets:
  - migratory_user_record.user_id
  - migratory_user_record.db_tenant_code
  - migratory_user_record.is_login
adjudication: boundary
also_confused_with: [新用户]
contract_version: "0.1"
---

“存量用户”指迁移动作发生前已存在的用户，其判定在数据上是“在 [[migratory_user_record]] 中存在（user_id + db_tenant_code）记录”。与新用户的边界是：新用户没有该记录，因此不会被登录弹窗逻辑覆盖（见 [[migratory_user_not_login]]、[[eject_msg_once]]）。别称“迁移用户”在语料中与存量用户混用，按 boundary 处理：两者在本主题下同指。

## 需求背景

(document_claim 锚定，双源) 需求文档《产融平台数据迁移涉及的改造需求V1.2》主张：存量用户点击【登录】，输入用户、密码/短信验证码后可登录成功，进入到产融平台内页可以看到企业状态为“已认证”，产品中心处至少已经开通了一个产品。该主张 code_status=confirmed，双源证据为 `code_path:PlatFormMigratoryApplication.java:migratoryCust + reqdoc:产融平台数据迁移涉及的改造需求V1.2`——代码在迁移客户时自动开通产品（autoActiveProduct）并设置企业状态，与需求一致。本页为 concept 页，不作锚点块，双源证据登记于上方 frontmatter sources。

## 版本演进

- v0（草稿）：boundary 判定成立，别称“迁移用户”与 [[migratory_user_record]] 记录一一对应。
- (document_claim，未证实) 需求文档另提及“注册/登录入口统一到产融平台”，语义分析标记为 uncovered（无代码证据），仅作记录，不影响本页映射。

关联页面：[[migratory_user_record]]、[[migratory_user_login_state]]、[[eject_msg_once]]、[[migratory_cust]]。