---
type: rule
title: 迁移自动开通产品
page_key: migration_auto_active_product
domain: 租户迁移
status: published
aliases: []
oid: 25
sources: [code, reqdoc]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：迁移后企业自动获得产品权限。

## 需求背景
需求侧确认：迁移后自动开通产品。代码：PlatFormMigratoryApplication.java:migratoryCust 调用 autoActiveProduct。

## 版本演进
v0.1 基于代码与需求双源。

```ground:rule
name: 迁移自动开通产品
content: migratoryCust 对关联项目取 tenant_project.platform_product_code 并调用 autoActiveProduct 开通
impact: 迁移后企业自动获得产品权限
field_targets: [cust_auth_application, tenant_product]
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust + reqdoc:迁移后自动开通产品"
```

关联：[[customer_migration]]