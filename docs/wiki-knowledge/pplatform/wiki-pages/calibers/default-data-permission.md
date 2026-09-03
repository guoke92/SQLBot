---
type: caliber
title: 数据权限默认范围口径
page_key: default-data-permission
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

该口径描述非管理员无权限记录时的默认数据范围，默认与用户组织绑定一致并回填组织ID列表。

## 需求背景

用于数据权限查询时补齐缺省配置，保障数据可见范围可预期。

## 版本演进

初始语义抽取版本，后续需补充默认范围回填的详细流程。

```ground:caliber
name: 数据权限默认范围
predicate: sys_cust_org_user_permission.permission_type = 'SAME_AS_USER_ORG' WHEN record is null or permission_type is blank
scope: 非管理员无权限记录时，默认数据范围与用户组织绑定一致，并回填 orgIdList
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType()
```

相关页面：[[sys_cust_org_user_permission]] [[data-permission]]