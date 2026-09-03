---
type: concept
title: "问卷星活动"
page_key: "wenjuan_activity"
domain: "customer_survey"
status: published
aliases: ["问卷星", "wenjuan", "问卷活动"]
oid: 10
sources: ["code"]
contract_version: "0.1"
maps_to: "WenjuanDisplayService 使用的外部问卷星系统"
field_targets: []
adjudication: "boundary"
also_confused_with: ["调研问卷"]
boundary: "由 /cust-web/wenjuan 控制展示，答卷完成态实时查询问卷星，不落库"
scope:
  databases: [lowcode_pplatform]
---

# 问卷星活动

**业务定位**：外部问卷星系统，用于产融首页活动展示。

## 需求背景

通过 `WenjuanDisplayService` 控制展示，答卷状态实时查询不落库。问卷星活动仅对企业内首个访问用户展示，并依赖白名单表控制参与资格。

## 版本演进

- v0.1 初稿，基于术语桥边界判定。

[[cust_company_survey_whitelist]] [[wenjuan_home_display_scenario]] [[whitelist_controls_visibility]]