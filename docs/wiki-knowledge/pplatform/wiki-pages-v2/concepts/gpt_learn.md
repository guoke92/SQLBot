---
type: concept
title: GP学习 / 智能审核引流
page_key: gpt_learn
domain: 客户管理
status: draft
aliases: [GptLearn, 引流卡片, 智能审核, saas中登]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnService.java:recordPosterClick
  - code_path:GptLearnService.java:validateFinanceUser
  - db:gpt_learn_poster_log
contract_version: "0.1"
maps_to: gpt_learn_poster_log.id
field_targets:
  - gpt_learn_poster_log.id
  - gpt_learn_poster_log.popup_time
  - gpt_learn_poster_log.click_time
adjudication: boundary
also_confused_with:
  - cust_company_survey_state.company_id
belong: concepts
field_targets: [gpt_learn_poster_log.id]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实) 需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）通篇未出现 GP学习引流、问卷星活动、企业画像（Profile）的任何业务规则或流程表述，无法形成双源锚点。

名称里有「学习」，但它不是在线的学习业务：实为向外部 SaaS 中登同步登录信息并引流跳转的埋点链路，`recordId` 就是 [[tables/gpt_learn_poster_log]] 的 `id`。仅对 FINANCE 企业开放（[[rules/gpt_learn_finance_only]]），并按租户灰度（[[rules/poster_allowed_tenant]]），生命周期见 [[processes/gpt_learn_poster_log_lifecycle]]。

## 需求背景

链路的三个入口——同步登录信息、查询是否弹卡、记录点击——都先做金融机构校验；弹卡还受租户白名单与弹出次数上限约束，点击则以 `recordId + userId + companyId` 匹配保证单次回写。业务目标是让目标企业用户在登录后看到引流卡片并点击跳转，因此埋点表同时是「频次控制表」和「点击回执表」。

## 版本演进

- 当前观测：埋点 252 行，`enable` 全 `Y`，租户仅 `beehive-scf.qhhrly.cn`，投放面很窄。
- 文档侧无对应业务规则表述（见页首 document_claim，未证实）。

相关：[[gpt_learn_poster_log]]
