---
type: caliber
title: 白名单豁免
page_key: calibers/whitelist_exempt
domain: CA证书收费
status: draft
aliases: [EXEMPT_WHITELIST, 特殊配置且年费为0]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 白名单豁免

## 业务定位

以[[tables/ca_fee_company]]的 `special_config_flag='Y'` 且 `special_annual_fee=0` 判定：企业存在生效中的特殊配置快照，且特殊配置后应缴年费为 0。命中即视为**免缴**，在[[rules/multi_project_exemption_rule|多项目豁免规则]]与[[rules/rule_engine_priority|规则引擎优先级]]中按 `EXEMPT_WHITELIST` 放行。

与[[calibers/targeted_reduction]]的差别仅在 `special_annual_fee` 是否为 0：为 0 是豁免，大于 0 是减免，二者共用 `special_config_flag='Y'` 这一前置。特殊配置来源见[[tables/ca_fee_project_config]]的 `special_company_list`。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 白名单豁免
predicate: "ca_fee_company.special_config_flag = 'Y' AND ca_fee_company.special_annual_fee = 0"
scope: ca_fee_company
evidence: code
```