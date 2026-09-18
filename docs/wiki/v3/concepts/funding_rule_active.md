---
type: concept
title: 生效中的资方规则
page_key: funding_rule_active
belong: concepts
domain: funding_rule
status: draft
aliases: [资金方规则, 资方准入]
maps_to: funding_rule_info.rule_status
field_targets: [funding_rule_info.rule_status]
sources: ['code_path:FundingPartyRuleProviderImpl.java:95', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [funding_rule_info]
also_confused_with: [funding_exception_hint, no_voucher_rule_element]
adjudication: boundary
---

# 生效中的资方规则

运行时只取 rule_status=ACTIVE 的规则头，再按 rule_info_id 取明细。不是异常建议表，也不是需求「无凭证」要素（本仓无对应赋值）。

## 页面链接

- [[tables/funding_rule_info]]
- [[dicts/funding_rule_info__rule_status]]
- [[processes/funding_rule_info__rule_status]]
- [[concepts/funding_exception_hint]]
- [[concepts/no_voucher_rule_element]]
