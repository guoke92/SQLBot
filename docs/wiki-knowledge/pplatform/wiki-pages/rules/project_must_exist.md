---
type: rule
title: 项目必须存在才可关联
page_key: project_must_exist
domain: 租户迁移
status: published
aliases: []
oid: 22
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：防止企业迁移关联到无效项目。

## 需求背景
保证迁移时的项目关联有效。

## 版本演进
v0.1 基于代码证据。

```ground:rule
name: 项目必须存在才可关联
content: setCustProjectRel 按 projectId 查询 tenant_project；为 null 抛 IllegalArgumentException
impact: 防止企业迁移关联到无效项目
field_targets: [tenant_project, cust_project_rel]
evidence: "code_path:PlatFormMigratoryApplication.java:setCustProjectRel"
```

关联：[[project_migration]]