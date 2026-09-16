---
type: scenario
title: 问卷与学习活动
page_key: company_survey
domain: GP学习/问卷/企业画像
status: draft
aliases: [问卷白名单, GP学习]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:GP学习/问卷/企业画像"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_company_survey_state]
field_targets:
  - cust_company_survey_whitelist.enable
---

# 问卷与学习活动

问「问卷白名单企业 / 是否答过问卷 / GP 引流弹出」时进入本场景。画像接口无独立落库表，本窗不展开。

问卷主档 [[cust_company_survey_state]]，白名单 [[cust_company_survey_whitelist]]，答卷 [[cust_survey_answer]]。引流埋点 [[gpt_learn_poster_log]]，代码要求企业角色为金融机构才记弹出。

```ground:scenario
scenario: company_survey
hubs:
- table: cust_company_survey_state
  role: master
  grain: 一企问卷状态
  window:
  - id
  - enable
  - create_time
  - update_time
  - first_visitor_lottery_shown
- table: cust_company_survey_whitelist
  role: whitelist
  grain: 一企白名单
  window:
  - id
  - enable
  - create_time
  - update_time
  - company_id
- table: cust_survey_answer
  role: answers
  grain: 一条答卷
  window:
  - id
  - enable
  - create_time
  - update_time
  - company_id
  - survey_code
- table: gpt_learn_poster_log
  role: poster
  grain: 一次弹出/点击
  window:
  - id
  - enable
  - create_time
  - update_time
  - user_id
  - company_id
  - popup_time
  - click_time
shared:
- table: cust_company_info
  role: company
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_company_type
lifecycle: []
```
