---
type: rule
title: 角色全量覆盖规则
page_key: role_full_overwrite
domain: 客户角色与端口
status: draft
aliases:
  - addRoleInfo 全量覆盖
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:addRoleInfo
contract_version: "0.1"
belong: rules
---

该规则约束 [[cust_role_info]] 的写入方式：不是增量合并，而是按企业维度先清后建。

## 需求背景

客户角色以“全量覆盖”方式维护，保证企业角色集合与上游传入的 roleType 数组完全一致；由于每条记录 code 重生成、状态回落 ADD，覆盖后需要重新激活。与项目关系的联动见 [[project_rel_role_sync]]。

## 版本演进

- v0（draft）：依据 addRoleInfo 代码路径成页。

```ground:rule
name: 角色全量覆盖规则
content: "客户角色通过 addRoleInfo 全量覆盖：先按企业 code 删除旧角色，再按 roleType JSON 数组逐个插入新角色，默认状态为 ADD；每个角色 code 重新生成，roleType 去除引号，dbTenantCode 取自关联企业。"
impact: 影响 cust_role_info 表记录增删和 role_type 值
field_targets:
  - cust_role_info.role_type
  - cust_role_info.status
  - cust_role_info.ref_cust_company_info
evidence: "code_path:CustRoleApplication.java:addRoleInfo"
```