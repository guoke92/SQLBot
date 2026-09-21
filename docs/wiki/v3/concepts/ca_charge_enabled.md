---
type: concept
title: 项目是否开启 CA 收费
page_key: ca_charge_enabled
belong: concepts
domain: ca_fee
status: draft
aliases: [CA收费开关]
maps_to: ca_fee_project_config.charge_enabled
field_targets: [ca_fee_project_config.charge_enabled]
sources: ['code_path:CaFeeRuleEngineService.java:98', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/ca证书收费.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_project_config]
also_confused_with: [ca_fee_paid]
adjudication: boundary
---

# 项目是否开启 CA 收费

未开收费时规则引擎直接 EXEMPT，不是「未缴费」。Y/N 本身不编字典页。

## 页面链接

- [[tables/ca_fee_project_config]]
- [[dicts/ca_fee_project_config__charge_enabled]]
- [[concepts/ca_fee_paid]]
