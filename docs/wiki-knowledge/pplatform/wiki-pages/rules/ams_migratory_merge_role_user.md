---
type: rule
title: AMS迁移企业已存在时合并角色/用户
page_key: ams_migratory_merge_role_user
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# AMS迁移企业已存在时合并角色/用户

业务定位：在 AMS 产品下，若迁移的企业已存在，则合并新增的管理员/经办人与角色，避免重复建企和建用户。

## 需求背景

当迁移企业已存在于 AMS 系统时，系统按手机号、公司类型、用户类型过滤新增管理员或经办人，并复制角色信息后保存，实现幂等迁移。

## 版本演进

暂无。

```ground:rule
name: AMS迁移企业已存在时合并角色/用户
content: AMS 产品下若企业已存在，按手机号+公司类型+用户类型过滤新增管理员/经办人，复制角色并保存
impact: AMS 迁移幂等，避免重复建企和重复建用户
field_targets:
  - CustPersonInfoDO.phone
  - CustPersonInfoDO.companyType
  - CustPersonInfoDO.userType
evidence: code_path:PlatFormMigratoryApplication.java:migratoryCust AMS分支
```