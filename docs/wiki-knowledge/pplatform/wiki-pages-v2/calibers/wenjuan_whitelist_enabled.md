---
type: caliber
title: 问卷活动参与企业白名单口径
page_key: wenjuan_whitelist_enabled
domain: 客户管理
status: draft
aliases: [白名单口径, isParticipating 口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - db:cust_company_survey_whitelist.enable
contract_version: "0.1"
belong: calibers
---

活动可见范围的判定口径：企业需同时满足「在 [[tables/cust_company_survey_whitelist]] 中登记」且 `enable = 'Y'`。对应规则 [[rules/wenjuan_whitelist_participation]]，影响首页展示决策 [[processes/wenjuan_home_display_scene]] 与专属答题链接获取。

## 需求背景

白名单是活动投放的第一道闸门：未命中的企业首页返回 `NONE`，直接调 `getSurveyUrl` 也会被拒绝。DB 观测 11 行 `enable` 全为 `Y`，尚无失效样例。

## 版本演进

- 当前观测：`enable` 全 `Y`（11 行），`enable='N'` 的实际行为未被验证。

```ground:caliber
name: 问卷活动参与企业白名单
predicate: cust_company_survey_whitelist.enable = 'Y'
scope: WenjuanDisplayService.isParticipating(companyId) 判定是否展示活动与获取专属答题链接
evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay + db:cust_company_survey_whitelist.enable 全 Y（11 行）"
```