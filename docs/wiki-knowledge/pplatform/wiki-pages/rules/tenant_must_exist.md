---
type: rule
title: 迁移租户必须存在
page_key: tenant_must_exist
belong: rules
domain: 租户迁移
status: published
aliases: []
oid: 21
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：阻断租户缺失时的企业迁移。

## 需求背景
保证迁移源租户配置有效。

## 版本演进
v0.1 基于代码证据。

```ground:rule
name: 迁移租户必须存在
content: migratoryCust 的 AMS 分支按 enable='Y' 和 db_tenant_code 查 tenant_setting_config；不存在则抛 BccpUserExceptionEnum.COMMON_EXCEPTION
impact: 阻断租户缺失时的企业迁移
field_targets: [tenant_setting_config]
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

关联：[[tenant_migration]]