---
type: rule
title: SPECIFIED 权限必须填写 org_id_list
page_key: specified_requires_org_id_list
domain: 数据权限与组织
status: draft
aliases: [SPECIFIED 必填组织]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
belong: rules
---

把 [[tables/sys_cust_org_user_permission]].permission_type 保存为 SPECIFIED 时，org_id_list 必填；而 SAME_AS_USER_ORG 不需要填，其组织范围由用户组织绑定回填。组织ID的取值域见 [[concepts/org_identity_bridge]]，状态流转见 [[processes/data_permission_type_fsm]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义（「仅 SPECIFIED 必填；SAME_AS_USER_ORG 时由用户组织绑定回填」）得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: SPECIFIED 必填 org_id_list
statement: permission_type=SPECIFIED 时 org_id_list 必填；SAME_AS_USER_ORG 时由用户组织绑定回填
condition: 保存数据权限
action: 校验 org_id_list 非空，否则拒绝落库
evidence: code_path:DataPermissionApplication.java#saveDataPermission / #saveDataPermissionBatch
```