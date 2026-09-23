---
type: concept
title: 企业统一社会信用代码
page_key: certification_no_term
belong: concepts
domain: ca_fee
status: draft
aliases: [统码, USCC, certification_no]
maps_to: cust_company_info.certification_no
field_targets: [cust_company_info.certification_no, ca_fee_company.certification_no,
  ca_fee_order.certification_no, ca_cfca_upgrade_report.certification_no,
  ca_fee_special_config.certification_no]
sources: ['field_semantics:certification_no_uscc', 'code_path:ca_fee/relations_dicts.yaml']
created: '2026-09-22'
updated: '2026-09-22'
contract_version: '0.1'
related: [cust_company_info, ca_fee_company, ca_fee_order]
also_confused_with: [tenant_uscc]
adjudication: boundary
semantic_kind: same_semantic
join_hint: high_overlap_ok
---

# 企业统一社会信用代码

企业/CA 宽表与订单、上报等附属表共用的**统码**语义。

- hub→附属：重合高则强连（已确认企业→订单/CFCA 上报等）。
- 附属↔附属：重合高也可以连，不强求；低则只认同一术语。
- 勿与人员/股东证件号同列名场景混淆（见同名异义束）。

## 页面链接

- [[tables/cust_company_info]]
- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[concepts/tenant_uscc]]
- [[concepts/channel_code_homonym_bundle]]
