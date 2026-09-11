---
type: rule
title: 规则引擎优先级
page_key: rules/rule_engine_priority
domain: CA证书收费
status: draft
aliases: [evaluate 判定顺序, 缴费判定优先级]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeRuleEngineService.java:evaluate
contract_version: "0.1"
---

# 规则引擎优先级

## 业务定位

评估企业是否需要缴费的**判定顺序**为：

1. 项目未开启收费 → 放行；
2. 白名单豁免 → 放行；
3. 延期支付 → 放行；
4. 服务期内已缴费 → 放行；
5. 应缴金额为 0 → 放行；
6. 其余 → 需缴费（`UNPAID`/`EXPIRED`）。

顺序即优先级：**前序条件命中即短路**，不再进入后续判断。因此"金额为 0"这一条排在豁免之后，仅对未被前四类豁免覆盖的企业生效。结果产出 `feeStatus` 与 `needPay`，业务侧据此决定是否进入[[rules/intercept_scene_rule|拦截场景规则]]。

相关口径：[[calibers/charge_enabled_project]]、[[calibers/whitelist_exempt]]、[[calibers/in_service_period]]、[[calibers/paid_company]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定 feeStatus 和 needPay。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 规则引擎优先级
content: 评估企业是否需要缴费的优先级：项目未开启收费 → 白名单豁免 → 延期支付 → 服务期内已缴费 → 应缴金额为0 → 需缴费（UNPAID/EXPIRED）。
impact: 决定 feeStatus 和 needPay。
field_targets: [ca_fee_order, ca_fee_company]
evidence: "code_path:CaFeeRuleEngineService.java:evaluate"
```