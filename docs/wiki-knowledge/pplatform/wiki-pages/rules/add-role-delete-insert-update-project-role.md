---
type: rule
title: 添加角色时先删后插并更新项目角色
page_key: add-role-delete-insert-update-project-role
belong: rules
domain: 客户角色与数据权限组织
status: published
aliases:
  - addRoleInfo
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_project_rel.company_type, cust_role_info.ref_cust_company_info, cust_role_info.role_type]
scope:
  databases: [lowcode_pplatform]
---

该规则描述添加企业角色时的整体替换策略及项目角色同步行为。

## 需求背景

来自 CustRoleApplication.addRoleInfo() 实现，需关注多角色场景下项目角色可能被覆盖为首个角色的风险。

## 版本演进

初始语义抽取版本，后续需补充历史审计保留方案。

```ground:rule
name: 添加角色时先删后插并更新项目角色
content: addRoleInfo 先删除该企业所有 cust_role_info 记录，再按传入 roleType JSON 数组逐条插入新角色；同时将关联项目 cust_project_rel.companyType 更新为首个非空角色类型，并触发项目联系人同步
impact: 角色记录整体替换，历史审计丢失；项目关联企业角色可能被覆盖为首个角色，可能导致多角色项目丢失
field_targets:
  - cust_role_info.role_type
  - cust_role_info.ref_cust_company_info
  - cust_project_rel.company_type
evidence: code_path:CustRoleApplication.java:addRoleInfo()
```

相关页面：[[cust_role_info]] [[cust_project_rel]] [[enterprise-role]]