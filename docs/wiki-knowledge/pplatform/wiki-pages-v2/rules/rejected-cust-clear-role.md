---
type: rule
title: 拒绝态企业清角色关联
page_key: rule.rejected-cust-clear-role
domain: 客户角色与端口
status: draft
aliases:
  - BUILD_FAIL 清用户角色绑定
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#addRoleInfo
contract_version: "0.1"
---

# 拒绝态企业清角色关联

当企业 cust_build_status=BUILD_FAIL（拒绝）时，addRoleInfo 会调用 userInfoFacade.delCustUserRole 清掉该企业的用户-角色绑定。也就是说：被拒企业重新提交角色信息时，历史授权会被主动清理，而不是被继承。

这条规则与 [[rules/role-overwrite-add]] 配合，构成「重建」的完整语义：角色集合先删后建，用户-角色绑定在拒绝态下再额外清空。排查「重新提交后用户权限丢失」时，应先确认企业是否处于 BUILD_FAIL。

## 需求背景

需求文档要求「被拒企业重新提交需重新授权」，本规则是其实现侧的清关联动作。

## 版本演进

- 在 BUILD_FAIL 分支增加 delCustUserRole 调用，避免被拒企业的陈旧用户-角色绑定被沿用。

```ground:rule
name: 拒绝态企业清角色关联
content: 当企业 cust_build_status=BUILD_FAIL（拒绝）时，addRoleInfo 会调用 userInfoFacade.delCustUserRole 清掉该企业的用户-角色绑定。
impact: 被拒企业重新提交时会清理历史角色授权
field_targets:
  - cust_role_info.role_type
evidence: code_path:CustRoleApplication.java#addRoleInfo（CustBuildStatusEnum.BUILD_FAIL 分支）
```

## 关联

- [[rules/role-overwrite-add]]
- [[tables/cust_role_info]]
- [[processes/cust-role-status]]