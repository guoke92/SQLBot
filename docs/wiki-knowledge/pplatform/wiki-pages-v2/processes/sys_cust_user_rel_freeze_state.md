---
type: process
title: 企业用户冻结状态
page_key: sys_cust_user_rel_freeze_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - is_freeze 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code:LocalTypeUserController.java:freeze
  - code:LocalTypeUserController.java:active
  - code:UserFacade.java:updateListFreezeFlag
contract_version: "0.1"
belong: processes
---

企业-用户-产品-角色关联的冻结状态机，作用于 [[sys_cust_user_rel.is_freeze]]：N=激活、Y=冻结。
两个迁移都必须先调 SSO 再改本地关联表，见规则 [[freeze_active_dual_write]]，
过滤未冻结的口径见 [[user_not_frozen]]。

## 需求背景

冻结/解冻是跨系统操作：SSO 侧负责登录态，本地表负责权限过滤，两侧必须一致，
否则出现“能登录但无权限”或相反的不一致。

## 版本演进

- v0（草稿）：状态值来自代码常量，迁移来自控制层与 Facade 调用点。

```ground:process
name: 企业用户冻结状态
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 激活（未冻结）
    source: code_const
  - value: Y
    label: 冻结
    source: code_const
transitions:
  - from: N
    event: POST /sys-web/user/freeze（先 SSO freezePerson，再 updateListFreezeFlag）
    to: Y
    evidence: "code_path:LocalTypeUserController.java:freeze + UserFacade.java:updateListFreezeFlag"
  - from: Y
    event: POST /sys-web/user/active（先 SSO activePerson，再 updateListFreezeFlag）
    to: N
    evidence: "code_path:LocalTypeUserController.java:active + UserFacade.java:updateListFreezeFlag"
```

相关：[[sys_cust_user_rel]]、[[freeze_active_dual_write]]、[[user_not_frozen]]、[[login_user_status_state]]。