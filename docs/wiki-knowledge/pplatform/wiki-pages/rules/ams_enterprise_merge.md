---
type: rule
title: AMS存量企业合并迁移
page_key: ams_enterprise_merge
domain: 租户迁移
status: published
aliases: []
oid: 20
sources: [code, reqdoc]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：支持讯易链与 AMS 存量企业数据合并。

## 需求背景
需求侧确认：AMS 与讯易链存量企业需数据合并，保留一条。代码：PlatFormMigratoryApplication.java:migratoryCust AMS分支。

## 版本演进
v0.1 基于代码与需求双源。

```ground:rule
name: AMS存量企业合并迁移
content: AMS 产品迁移时，先按 certNo/socialUnifiedCode 和 tenant 查已存在企业；存在则增量补齐角色、管理员、经办人，不重复建档
impact: 支持讯易链与 AMS 存量企业数据合并
field_targets: [cust_company_info, cust_person_info, cust_role_info]
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust AMS分支 + reqdoc:AMS 与讯易链存量企业需数据合并，保留一条"
```

关联：[[enterprise_data_merge]] [[customer_migration]]