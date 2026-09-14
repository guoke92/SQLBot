---
type: process
title: 问卷星活动首页展示场景决策
page_key: wenjuan_home_display_scene
domain: 客户管理
status: draft
aliases: [displayScene, 首页展示场景, 活动UI决策]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - code_path:WenjuanController.java:markLotteryShown
  - code_path:WenjuanDisplayService.java:markLotteryShown
contract_version: "0.1"
belong: processes
---

这是接口返回的展示决策，不落库：`WenjuanHomeDisplayConfigDTO.displayScene` 由 `resolveHomeDisplay` 每次实时计算，取值集合见 [[enums/wenjuan_home_display_scene]]。决策依赖白名单（[[calibers/wenjuan_whitelist_enabled]]）、企业首个访问用户判定（[[concepts/first_visitor]]）以及外部问卷星的完成态（[[rules/survey_status_not_persisted]]）。

## 需求背景

首页活动 UI 分三档：完全不出活动（`NONE`）、只出指引弹窗 + 右下角问卷入口（`GUIDE_ONLY`）、抽奖转盘 + 中奖弹窗 + 右下角入口（`FIRST_VISITOR_LOTTERY`）。转盘只在「白名单企业 + 企业首个访问用户 + 转盘未展示」三者同时成立时给出，前端动效结束后回调 `mark-lottery-shown` 降档为 `GUIDE_ONLY`，实现防刷新重复。活动企业的首个访问用户还会被留在产融首页（[[rules/stay_on_home_for_survey]]）。

## 版本演进

- 答题完成态实时向问卷星查询，本地不缓存，因此同一用户在完成后再次进入首页会直接落到 `GUIDE_ONLY`。
- 状态判定键为 `WenjuanHomeDisplayConfigDTO.displayScene`，无对应落库字段。

```ground:process
name: 问卷星活动首页展示场景（非落库，接口返回的展示决策）
field: WenjuanHomeDisplayConfigDTO.displayScene
states:
  - value: NONE
    label: 不展示任何活动UI
    source: code_enum
  - value: FIRST_VISITOR_LOTTERY
    label: 转盘抽奖+中奖弹窗+右下角问卷入口
    source: code_enum
  - value: GUIDE_ONLY
    label: 指引弹窗+右下角问卷入口
    source: code_enum
transitions:
  - from: NONE
    event: 活动未配置 / userId或companyId为空 / 企业不在白名单
    to: NONE
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: NONE
    event: 白名单企业但非企业首个访问用户
    to: NONE
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: NONE
    event: 白名单企业 + 首个访问用户 + 转盘未展示
    to: FIRST_VISITOR_LOTTERY
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
  - from: FIRST_VISITOR_LOTTERY
    event: 前端动效结束调用 /cust-web/wenjuan/mark-lottery-shown
    to: GUIDE_ONLY
    evidence: "code_path:WenjuanController.java:markLotteryShown + WenjuanDisplayService.java:markLotteryShown"
  - from: FIRST_VISITOR_LOTTERY
    event: 转盘已展示且问卷星 isSurveyCompleted=true（只留右下角入口，不弹指引）
    to: GUIDE_ONLY
    evidence: "code_path:WenjuanDisplayService.java:resolveHomeDisplay"
```