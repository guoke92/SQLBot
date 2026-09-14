---
type: rule
title: 问卷活动仅白名单企业参与
page_key: wenjuan_whitelist_participation
domain: 客户管理
status: draft
aliases: [问卷白名单规则, getSurveyUrl 拒绝]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanDisplayService.java:getSurveyUrl
contract_version: "0.1"
belong: rules
---

`companySurveyWhitelistDao.isParticipating(companyId)` 为 false 时首页返回 `NONE`；`getSurveyUrl` 时抛「企业不在白名单列表中！」。判定位见 [[tables/cust_company_survey_whitelist]]，口径见 [[calibers/wenjuan_whitelist_enabled]]。

## 需求背景

白名单同时控制「看不看得见活动」与「拿不拿得到专属答题链接」两件事，是活动可见范围的第一道闸门；第二个闸门是首个访问用户判定（[[rules/first_visitor_only_ui]]）。

## 版本演进

- 当前观测：白名单 11 行全为有效，含测试数据。

```ground:rule
name: 问卷活动仅白名单企业参与
content: "companySurveyWhitelistDao.isParticipating(companyId) 为 false 时首页返回 NONE；getSurveyUrl 时抛「企业不在白名单列表中！」"
impact: 控制活动可见范围与专属答题链接获取
field_targets:
  - cust_company_survey_whitelist.company_id
  - cust_company_survey_whitelist.enable
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay + WenjuanDisplayService.java:getSurveyUrl"
```