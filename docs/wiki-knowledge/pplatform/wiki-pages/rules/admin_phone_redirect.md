---
type: rule
title: 管理员手机号变更跳转规则
page_key: rule_admin_phone_redirect
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.getRedirectPage", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_change_cfg.item_code, cust_change_record.oper_cust_info, cust_person_info.phone]
coverage_note: 变更配置/变更记录
scope:
  databases: [lowcode_pplatform]
---

该规则决定变更提交后的页面跳转：若最新变更记录包含 `UN0012` 或 `UN0013` 变更项，且新旧管理员手机号不同，且当前登录用户手机号不等于新手机号，则跳转变更提交成功页；否则跳转运营中台变更待办页。

## 需求背景

暂无特定需求声明。

```ground:rule
name: "管理员手机号变更跳转规则"
content: "若最新变更记录包含 UN0012 或 UN0013 变更项，且新旧管理员手机号不同，且当前登录用户手机号不等于新手机号，跳转变更提交成功页；否则跳转运营中台变更待办页"
impact: "影响前端页面路由"
field_targets:
  - "cust_change_cfg.item_code"
  - "cust_change_record.oper_cust_info"
  - "cust_person_info.phone"
evidence: "code_path:CustChangeApplication.getRedirectPage"
```

## 版本演进

暂无。

相关：[[cust_change_cfg]] [[cust_change_record]] [[cust_person_info]]
