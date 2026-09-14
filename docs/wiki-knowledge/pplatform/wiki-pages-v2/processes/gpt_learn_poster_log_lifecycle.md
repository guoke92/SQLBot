---
type: process
title: 智能审核引流卡片埋点生命周期
page_key: gpt_learn_poster_log_lifecycle
domain: 客户管理
status: draft
aliases: [引流卡片生命周期, poster lifecycle, 弹窗状态机]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:GptLearnService.java:validateFinanceUser
  - code_path:GptLearnService.java:checkPosterStatus
  - code_path:GptLearnService.java:recordPosterClick
  - db:gpt_learn_poster_log
contract_version: "0.1"
belong: processes
---

状态机的落点是 [[tables/gpt_learn_poster_log]] 的 `popup_time` / `click_time`：`SHOWN` 等价于新写入一行且 `popup_time` 有值，`CLICKED` 等价于该行 `click_time` 有值。前置校验对应三条规则：[[rules/gpt_learn_finance_only]]、[[rules/poster_allowed_tenant]]、[[rules/poster_popup_max_count]]；术语见 [[concepts/gpt_learn]]。

## 需求背景

卡片按「打扰频次可控、投放范围可控」设计：不弹（`NOT_SHOW`）由三类原因造成——企业不是金融机构、租户不在灰度名单、同一用户在该企业的弹出次数已达上限；只有全部通过才落埋点并返回 `recordId`。点击回写要求 `recordId + userId + companyId` 三者匹配，否则抛「埋点记录不存在或已记录点击」，因此 `CLICKED` 是单次可达的终态。

## 版本演进

- 当前观测：全表 252 行，`enable` 全 `Y`，`db_tenant_code` 仅 `beehive-scf.qhhrly.cn`，说明投产投放面很窄。
- `INIT` / `NOT_SHOW` / `SHOWN` / `CLICKED` 为代码语义状态，字典中无对应落库枚举列，仅 `popup_time`/`click_time` 有无值可判定。

```ground:process
name: 智能审核引流卡片埋点生命周期
field: gpt_learn_poster_log.popup_time / gpt_learn_poster_log.click_time
states:
  - value: INIT
    label: 未评估
    source: code_const
  - value: NOT_SHOW
    label: 不弹出（非金融机构 / 租户不允许 / 已达弹出上限）
    source: code_const
  - value: SHOWN
    label: 已弹出并落埋点（popup_time 有值）
    source: code_const
  - value: CLICKED
    label: 已点击（click_time 有值）
    source: code_const
transitions:
  - from: INIT
    event: 企业类型非 CustCompanyTypeEnum.FINANCE（validateFinanceUser 抛「仅金融机构用户可使用」）
    to: NOT_SHOW
    evidence: "code_path:GptLearnService.java:validateFinanceUser"
  - from: INIT
    event: isPosterAllowedTenant(dbTenantCode)=false
    to: NOT_SHOW
    evidence: "code_path:GptLearnService.java:checkPosterStatus"
  - from: INIT
    event: countByUserAndCompany(userId,companyId) >= maxPosterCount
    to: NOT_SHOW
    evidence: "code_path:GptLearnService.java:checkPosterStatus"
  - from: INIT
    event: 校验通过，createPopupRecord 写入 gpt_learn_poster_log(popup_time)
    to: SHOWN
    evidence: "code_path:GptLearnService.java:checkPosterStatus"
  - from: SHOWN
    event: POST /app-web/gptlearn/recordPosterClick(recordId) 且 recordId+userId+companyId 匹配成功
    to: CLICKED
    evidence: "code_path:GptLearnService.java:recordPosterClick"
  - from: SHOWN
    event: recordClick 未匹配（抛「埋点记录不存在或已记录点击」）
    to: SHOWN
    evidence: "code_path:GptLearnService.java:recordPosterClick"
```