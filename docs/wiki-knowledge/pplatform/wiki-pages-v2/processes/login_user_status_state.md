---
type: process
title: 登录用户系统状态
page_key: login_user_status_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sys_user.user_status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:init
  - code:UserFacade.java:getUserStatusEnum
contract_version: "0.1"
belong: processes
---

（document_claim，未证实）文档主张“SaaS 登录：SaaSAuthService.login → SsoBlackWhiteListService 黑白名单校验 →
SSO 返回 token → UserFacade 加载用户 → LocalTypeMenuService 加载菜单”，该链路在给定语义分析中为 uncovered，
本文仅作为版本演进记录，不作为契约。

登录用户系统状态机，作用于 [[sys_user.user_status]]：INIT（初始）→ NORMAL（正常）→ FREEZE（冻结）。
初始化由 SSO 登录 init 写入 NORMAL；企业冻结/用户冻结（[[sys_cust_user_rel.is_freeze]]=Y 映射）置 FREEZE。
菜单接口与验证码策略见 [[get_user_menu_perm_list]]、[[login_captcha_policy]]。

## 需求背景

用户首次登录处于 INIT，完成企业上下文初始化后才可正常使用；一旦企业或用户被冻结，
登录用户需同步进入 FREEZE，与本地关联表冻结标记保持一致。

## 版本演进

- v0（草稿）：状态值来自代码枚举，迁移来自 init 与状态映射代码。
- （document_claim，未证实）登录全链路（login / SsoBlackWhiteListService / token / UserFacade / LocalTypeMenuService）待代码核实。

```ground:process
name: 登录用户系统状态
field: sys_user.user_status
states:
  - value: INIT
    label: 初始
    source: code_enum
  - value: NORMAL
    label: 正常
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
transitions:
  - from: INIT
    event: SSO 登录初始化 init
    to: NORMAL
    evidence: "code_path:SaaSAuthController.java:init(ssoFacade.updateSysUserStatus(...,UserStatusEnum.NORMAL))"
  - from: NORMAL
    event: 企业冻结/用户冻结（is_freeze=Y 映射）
    to: FREEZE
    evidence: "code_path:UserFacade.java:getUserStatusEnum"
```

相关：[[sys_user]]、[[sys_cust_user_rel_freeze_state]]、[[freeze_active_dual_write]]。