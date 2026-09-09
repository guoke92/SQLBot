---
type: process
title: "问卷星首页展示场景"
page_key: wenjuan_home_display_scenario
belong: processes
domain: "customer_survey"
status: published
aliases: ["问卷星首页展示场景", "WenjuanHomeDisplayConfigDTO.displayScene"]
oid: 4
sources: ["code"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 问卷星首页展示场景

**业务定位**：定义问卷星活动在产融首页的展示场景状态机，由 `WenjuanDisplayService` 解析。

## 需求背景

根据活动配置、白名单、首个访问用户和转盘展示状态，决定首页展示 `NONE`（不展示）、`FIRST_VISITOR_LOTTERY`（转盘+中奖弹窗+右下角入口）、`GUIDE_ONLY`（指引弹窗+入口或仅入口）。

## 版本演进

- v0.1 初稿，基于代码枚举与转换证据。

```ground:process
name: "问卷星首页展示场景"
field: "WenjuanHomeDisplayConfigDTO.displayScene"
states:
  - value: "NONE"
    label: "不展示活动"
    source: "code_enum"
  - value: "FIRST_VISITOR_LOTTERY"
    label: "首个用户首次登入：转盘+中奖弹窗+右下角入口"
    source: "code_enum"
  - value: "GUIDE_ONLY"
    label: "首个用户已完成转盘：仅指引弹窗+右下角入口，或已完成仅右下角入口"
    source: "code_enum"
transitions:
  - from: "NONE"
    event: "resolveHomeDisplay(活动配置有效+企业在白名单+首个访问用户+转盘未展示)"
    to: "FIRST_VISITOR_LOTTERY"
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: "FIRST_VISITOR_LOTTERY"
    event: "markLotteryShown(标记转盘已展示)"
    to: "GUIDE_ONLY"
    evidence: "code_path:WenjuanDisplayService.java:markLotteryShown"
  - from: "GUIDE_ONLY"
    event: "resolveHomeDisplay(问卷未完成或已完成，仍为首个用户)"
    to: "GUIDE_ONLY"
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: "NONE"
    event: "非白名单/活动未配置/非首个访问用户"
    to: "NONE"
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```

[[cust_company_survey_whitelist]] [[cust_company_survey_state]] [[whitelist_controls_visibility]] [[first_visitor_exclusive_display]] [[lottery_shown_once]] [[survey_completion_not_persisted]] [[goto_product_stay_home]] [[wenjuan_activity]] [[first_visitor_user]] [[lottery_shown_flag]]