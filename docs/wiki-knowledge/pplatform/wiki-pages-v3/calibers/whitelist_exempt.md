---
type: caliber
title: 白名单豁免
page_key: whitelist_exempt
domain: CA证书收费
status: draft
aliases: [免缴, EXEMPT_WHITELIST]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFee"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - ca_fee_company.special_config_flag
  - ca_fee_company.special_annual_fee
---

特殊配置生效且应缴年费为 0，视为免缴，列在 [[ca_fee_company]]。`special_annual_fee > 0` 是减免不是豁免。来源名单在 [[ca_fee_project_config]] 的 `special_company_list`。

```ground:caliber
name: 白名单豁免
predicate: "ca_fee_company.special_config_flag = 'Y' AND ca_fee_company.special_annual_fee = 0"
scope: ca_fee_company
evidence: code
```
