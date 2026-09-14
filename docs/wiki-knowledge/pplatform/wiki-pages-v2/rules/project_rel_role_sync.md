---
type: rule
title: 项目关联角色同步规则
page_key: project_rel_role_sync
domain: 客户角色与端口
status: draft
aliases:
  - 项目角色同步
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:addRoleInfo
contract_version: "0.1"
belong: rules
---

该规则把 [[cust_role_info]] 的变更传导到 [[cust_project_rel]]，使项目维度也能识别客户身份。

## 需求背景

添加客户角色后，企业所有项目关系记录的 companyType 被统一更新为“第一个角色值”，即项目侧只保留单一角色快照，与客户角色侧的多值集合并不等价。该同步无外键约束，属业务派生关系（derived）。

## 版本演进

- v0（draft）：依据 addRoleInfo 代码路径成页。

```ground:rule
name: 项目关联角色同步规则
content: "添加客户角色后，将该企业所有 cust_project_rel 记录的 companyType 更新为第一个角色值。"
impact: 影响 cust_project_rel.company_type
field_targets:
  - cust_project_rel.company_type
evidence: "code_path:CustRoleApplication.java:addRoleInfo"
```