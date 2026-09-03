---
type: caliber
title: "问卷活动参与白名单"
page_key: "survey_whitelist"
domain: "customer_survey"
status: published
aliases: ["问卷活动参与白名单"]
oid: 6
sources: ["code"]
contract_version: "0.1"
field_targets: [cust_company_survey_whitelist.company_id, cust_company_survey_whitelist.enable]
scope:
  databases: [lowcode_pplatform]
---

# 问卷活动参与白名单

**业务定位**：定义问卷星活动是否对该企业开放的判断标准。

## 需求背景

用于 `resolveHomeDisplay` 判断白名单企业是否可参与活动。非白名单企业返回空展示配置。

## 版本演进

- v0.1 初稿，基于代码证据。

```ground:caliber
name: "问卷活动参与白名单"
predicate: "cust_company_survey_whitelist.enable = 'Y' AND cust_company_survey_whitelist.company_id = :companyId"
scope: "问卷星活动是否对该企业开放"
evidence: "code"
```

[[cust_company_survey_whitelist]] [[whitelist_controls_visibility]] [[wenjuan_activity]]