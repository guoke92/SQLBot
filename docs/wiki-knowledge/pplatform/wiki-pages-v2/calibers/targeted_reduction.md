---
type: caliber
title: 定向减免
page_key: targeted_reduction
domain: CA证书收费
status: draft
aliases: [特殊年费大于0, 定向减免企业]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
belong: calibers
---

# 定向减免

## 业务定位

以[[tables/ca_fee_company]]的 `special_config_flag='Y'` 且 `special_annual_fee > 0` 判定：企业存在生效中的特殊配置快照，且特殊年费不为 0——即**仍需缴费但金额被定向调整**（通常低于项目标准价）。

该值在[[rules/annual_fee_pricing_rule|年费定价规则]]中享有**最高优先级**：特殊年费 → 已锁定年费 → 项目角色价。因此命中本口径的企业，其订单 `annual_fee` 不会再回落到 `locked_annual_fee` 或项目价。

与[[calibers/whitelist_exempt]]的区别仅在于 `special_annual_fee` 是否为 0，请勿混用。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 定向减免
predicate: "ca_fee_company.special_config_flag = 'Y' AND ca_fee_company.special_annual_fee > 0"
scope: ca_fee_company
evidence: code
```