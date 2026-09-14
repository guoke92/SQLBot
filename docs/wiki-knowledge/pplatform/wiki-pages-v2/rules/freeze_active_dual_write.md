---
type: rule
title: 冻结/解冻双写 SSO 与本地关联表
page_key: freeze_active_dual_write
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 冻结解冻双写
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:freeze
  - code:LocalTypeUserController.java:active
contract_version: "0.1"
belong: rules
---

冻结与解冻必须先在 SSO 侧生效，再更新本地关联表冻结标记。

## 需求背景

SSO 登录状态与产融关联表冻结标记必须一致，否则出现能登录但无权限 / 相反的不一致；
过滤口径见 [[user_not_frozen]]，状态机见 [[sys_cust_user_rel_freeze_state]]。

## 版本演进

- v0（草稿）：规则来自控制层调用顺序证据。

```ground:rule
name: 冻结/解冻双写 SSO 与本地关联表
content: "freeze 先调 saaSAuthService.freezePerson(custId, idList, companyType) 同步 SSO，再 userFacade.updateListFreezeFlag(..., UserFreezeEnum.FREEZE) 置 sys_cust_user_rel.is_freeze；active 反向。"
impact: "SSO 登录状态与产融关联表冻结标记必须一致，否则出现能登录但无权限/相反的不一致。"
field_targets:
  - sys_cust_user_rel.is_freeze
evidence: "code_path:LocalTypeUserController.java:freeze/active"
```

相关：[[sys_cust_user_rel]]、[[sys_cust_user_rel_freeze_state]]、[[user_not_frozen]]。