---
type: caliber
title: 多项目校验放行口径
page_key: multi_project_pass
belong: calibers
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 多项目校验放行口径

业务定位：在多收费项目场景下，只要任一项目满足免缴费条件，整体校验即放行。

## 需求背景

企业可能关联多个收费项目，每个项目独立评估是否需要缴费。为避免过度拦截，当至少一个项目无需缴费时，整体 `pass` 置为 true。

## 版本演进

当前为“任一通过即通过”的宽松策略，未来可能根据业务调整聚合逻辑。

```ground:caliber
name: 多项目校验放行口径
predicate: "任一收费项目 evaluate.needPay=false 或 pass=true 则整体 pass=true"
scope: 缴费校验 doCheckFeePayment
evidence: "code:CaFeePaymentCheckApplication.doCheckFeePayment"
```

[[rule_engine_exemption_chain]] · [[ca_fee_order]]