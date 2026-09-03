---
type: rule
title: 指定组织时必须提供组织列表
page_key: specified-org-requires-org-list
domain: 客户角色与数据权限组织
status: published
aliases:
  - saveDataPermission
oid: 1
sources:
  - code_path
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则防止指定组织权限无实际范围。

## 需求背景

来自 DataPermissionApplication.saveDataPermission() 的参数校验逻辑。

## 版本演进

初始语义抽取版本，后续需补充 orgIdList 的有效性校验规则。

```ground:rule
name: 指定组织时必须提供组织列表
content: 当保存数据权限且 permissionType=SPECIFIED 时，orgIdList 不能为空
impact: 防止指定组织权限无实际范围
field_targets:
  - sys_cust_org_user_permission.permission_type
  - sys_cust_org_user_permission.org_id_list
evidence: code_path:DataPermissionApplication.java:saveDataPermission()
```

相关页面：[[sys_cust_org_user_permission]] [[data-permission]]