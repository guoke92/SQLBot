---
type: caliber
title: 问卷白名单企业
page_key: survey_whitelist_company
domain: GP学习/问卷/企业画像
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_company_survey_whitelist.enable
---

可展示问卷活动的企业。

```ground:caliber
name: 问卷白名单企业
predicate: "cust_company_survey_whitelist.enable = 'Y'"
scope: cust_company_survey_whitelist
evidence: code
```
