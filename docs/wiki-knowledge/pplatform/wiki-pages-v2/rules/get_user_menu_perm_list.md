---
type: rule
title: 登录后获取菜单权限接口
page_key: get_user_menu_perm_list
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 登录菜单接口
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getUserMenuPermList
  - reqdoc:sso-login-menu-perm
contract_version: "0.1"
belong: rules
---

登录后菜单权限获取接口：SaaSAuthController.getUserMenuPermList(LoginMenuDTO) →
saaSAuthService.getUserMenuPermList。

## 需求背景

文档主张“登录后获取菜单接口：LocalTypeMenuService/UserFacade 返回 LoginMenuDTO”，
代码侧已确认控制层入口 getUserMenuPermList 及其服务调用；菜单数据加载在本次语义分析中
未展开到 LocalTypeMenuService/UserFacade 内部实现。

## 版本演进

- v0（草稿）：规则同时有代码与需求文档来源（双源）。

```ground:rule
name: 登录后获取菜单权限接口
content: "getUserMenuPermList(LoginMenuDTO) 由 SaaSAuthController 暴露，转 saaSAuthService.getUserMenuPermList 返回登录菜单权限。"
impact: "登录后前端菜单与权限入口，依赖当前登录用户与企业上下文（Cookie/缓存）。"
field_targets: []
evidence: "code_path:SaaSAuthController.java:getUserMenuPermList + reqdoc:sso-login-menu-perm"
```

相关：[[login_init_cookie]]、[[login_user_status_state]]。