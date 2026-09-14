---
type: concept
title: 问卷（两套并存）
page_key: wenjuan
domain: 客户管理
status: draft
aliases: [Wenjuan, 问卷星活动, Survey, 调研问卷, 调研答案]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:CustSurveyController.java:submit
  - code_path:WenjuanController.java:syncAndDisplayConfig
  - code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - db:cust_survey_answer
  - db:cust_company_survey_state
contract_version: "0.1"
maps_to: cust_survey_answer.survey_code
field_targets:
  - cust_survey_answer.survey_code
  - cust_company_survey_state.company_id
adjudication: boundary
also_confused_with:
  - cust_company_survey_state.company_id
  - cust_company_survey_whitelist.company_id
belong: concepts
field_targets: [cust_survey_answer.survey_code]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实) 需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）通篇未出现 GP学习引流、问卷星活动、企业画像（Profile）的任何业务规则或流程表述，无法形成双源锚点。

「问卷」在本系统中是两套互不相干的实现，页面与接口前缀都会出现 "survey/wenjuan" 字样，极易混用。

- 落库题库问卷：`CustSurveyController`（`/cust-web/survey`），答案写 [[tables/cust_survey_answer]]，问卷范围见 [[calibers/survey_code_xyl_2024_q1]]，有效记录口径见 [[calibers/cust_survey_answer_enabled]]。
- 外部问卷星活动：`WenjuanController`（`/cust-web/wenjuan`），答卷完成态不落库（[[rules/survey_status_not_persisted]]），只落企业级活动状态 [[tables/cust_company_survey_state]]，白名单见 [[tables/cust_company_survey_whitelist]]、展示决策见 [[processes/wenjuan_home_display_scene]]。

## 需求背景

两套问卷的业务目标不同：前者是站内调研，答案留在本地便于统计；后者是运营活动（转盘抽奖 + 问卷入口），答卷由问卷星持有，本地只关心「谁是企业首个访问用户」与「转盘是否已展示」。因此不能把 `cust_survey_answer` 的行数、题号当作活动参与度，也不能用 `cust_company_survey_state` 判断调研是否完成。

## 版本演进

- 当前观测：落库问卷只有一份（`XYL_2024_Q1`，338 行，题号 1-6），活动侧企业状态 11 行、白名单 11 家。
- 文档侧无对应业务规则表述（见页首 document_claim，未证实）。

相关：[[cust_survey_answer]]
