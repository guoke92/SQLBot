---
type: rule
title: 数据权限保存需企业管理员
page_key: data-permission-save-admin-required
belong: rules
domain: 客户角色与数据权限组织
status: published
aliases:
  - assertCurrentUserIsAdminOfTargetCompany
oid: 1
sources:
  - code_path
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则要求保存数据权限时必须由目标企业内的指定角色类型管理员操作。

## 需求背景

来自 DataPermissionApplication.assertCurrentUserIsAdminOfTargetCompany() 的越权防护逻辑。

## 版本演进

初始语义抽取版本，后续需补充管理员代理或特许操作流程。

```ground:rule
name: 数据权限保存需企业管理员
content: 保存数据权限时，要求 companyId/companyType 与当前登录会话一致，且当前登录用户为企业下指定角色类型的启用管理员，否则拒绝
impact: 防止越权配置数据权限
field_targets:
  - sys_cust_org_user_permission.user_id
  - sys_cust_org_user_permission.company_id
  - sys_cust_org_user_permission.company_type
  - sys_cust_org_user_permission.permission_type
evidence: code_path:DataPermissionApplication.java:assertCurrentUserIsAdminOfTargetCompany()
```

相关页面：[[sys_cust_org_user_permission]] [[admin]] [[data-permission]]