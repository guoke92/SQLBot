---
type: process
title: 问卷星首页展示场景（WenjuanHomeDisplayConfigDTO.displayScene）
page_key: processes/wenjuan_home_display_scene
domain: 问卷
status: draft
aliases:
  - displayScene
  - 首页展示场景
  - 转盘指引展示规则
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# 问卷星首页展示场景（WenjuanHomeDisplayConfigDTO.displayScene）

该状态机描述[[concepts/wenjuan]]（问卷星活动）在首页上「给用户看什么」的三种展示场景，取值承载在 `WenjuanHomeDisplayConfigDTO.displayScene` 上：`NONE`（不展示活动 UI）、`FIRST_VISITOR_LOTTERY`（首个用户首次登入：转盘 + 中奖弹窗 + 右下角入口）、`GUIDE_ONLY`（仅指引弹窗／右下角入口）。

场景解析统一在 `WenjuanDisplayService.resolveHomeDisplay` 中完成。进入 `FIRST_VISITOR_LOTTERY` 的前提是「白名单企业 + 首个访问用户 + 抽奖未展示」，三者缺一不可，其中白名单判定见 [[calibers/wenjuan_whitelist_company]]，首个访问用户定义见 [[concepts/first_visitor]]。抽奖已展示但问卷未完成时降级为 `GUIDE_ONLY`；问卷已完成同样停在 `GUIDE_ONLY`——完成态的判定不落库，而是实时查询问卷星，见 [[calibers/wenjuan_no_persist_completion]] 与 [[concepts/survey_completed]]。企业非首个访问用户时直接落到 `NONE`。

本场景状态与[[tables/cust_company_survey_state]]中的 `first_visitor_lottery_shown` / `first_visitor_lottery_shown_time` 直接对应：抽奖展示一旦被写入，后续访问就不可能再回到 `FIRST_VISITOR_LOTTERY`。

## 需求背景

本分析未提供该状态机的需求文档（reqdoc_claims）证据。待业务补充：`GUIDE_ONLY` 在问卷完成后的保留时长、以及 `NONE` 与「非白名单企业」在埋点上的区分方式。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:process
name: 问卷星首页展示场景
field: WenjuanHomeDisplayConfigDTO.displayScene
states:
  - value: NONE
    label: 不展示活动UI
    source: code_enum
  - value: FIRST_VISITOR_LOTTERY
    label: 首个用户首次登入：转盘+中奖弹窗+右下角入口
    source: code_enum
  - value: GUIDE_ONLY
    label: 仅指引弹窗/右下角入口
    source: code_enum
transitions:
  - from: NONE
    event: 白名单企业、首个访问用户、抽奖未展示
    to: FIRST_VISITOR_LOTTERY
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - from: FIRST_VISITOR_LOTTERY
    event: 抽奖已展示且问卷未完成
    to: GUIDE_ONLY
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - from: GUIDE_ONLY
    event: 问卷已完成
    to: GUIDE_ONLY
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - from: FIRST_VISITOR_LOTTERY
    event: 非企业首个访问用户
    to: NONE
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
```

相关页面：[[tables/cust_company_survey_state]]、[[tables/cust_company_survey_whitelist]]、[[concepts/wenjuan]]、[[concepts/first_visitor]]、[[concepts/survey_completed]]、[[calibers/wenjuan_whitelist_company]]、[[calibers/wenjuan_no_persist_completion]]。