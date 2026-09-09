---
type: rule
title: 企业管理员数据权限固定为 ALL
page_key: enterprise-admin-data-permission-all
belong: rules
domain: 客户角色与数据权限组织
status: published
aliases:
  - getByUserCompanyType
oid: 1
sources:
  - code_path
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则描述企业管理员查询数据权限时直接返回 ALL，不受组织数据范围限制。

## 需求背景

来自 DataPermissionApplication.getByUserCompanyType() 的查询分支逻辑。

## 版本演进

初始语义抽取版本，后续需补充管理员降级或变更时的数据权限再计算。

```ground:rule
name: 企业管理员数据权限固定为 ALL
content: 查询数据权限时，若用户为企业指定角色管理员，直接返回 permissionType=ALL，不查询实际记录
impact: 管理员不受组织数据范围限制
field_targets:
  - sys_cust_org_user_permission.permission_type
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType()
```

相关页面：[[sys_cust_org_user_permission]] [[data-permission]] [[admin]]