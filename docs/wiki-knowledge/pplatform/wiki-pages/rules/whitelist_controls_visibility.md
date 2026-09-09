---
type: rule
title: "白名单决定问卷活动可见性"
page_key: whitelist_controls_visibility
belong: rules
domain: "customer_survey"
status: published
aliases: ["白名单决定问卷活动可见性"]
oid: 13
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_whitelist.enable]
scope:
  databases: [lowcode_pplatform]
---

# 白名单决定问卷活动可见性

**业务定位**：白名单控制问卷星活动企业的参与资格。

## 需求背景

非白名单企业不展示任何活动 UI。该规则通过 `WenjuanDisplayService.resolveHomeDisplay` 实现，仅当企业存在于白名单且 `enable=Y` 时才可能进入活动展示流程。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:rule
name: "白名单决定问卷活动可见性"
content: "仅 cust_company_survey_whitelist 中 enable=Y 的企业可参与问卷星活动"
impact: "非白名单企业返回空展示配置，不展示任何活动UI"
field_targets:
  - "cust_company_survey_whitelist.enable"
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```

[[cust_company_survey_whitelist]] [[survey_whitelist]] [[wenjuan_activity]] [[wenjuan_home_display_scenario]]