---
type: caliber
title: 未缴费企业
page_key: unpaid_company
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status]
scope:
  databases: [lowcode_pplatform]
---

未缴费企业口径用于从企业维度识别尚未完成 CA 服务费缴费的企业。

## 需求背景

在续费提醒、到期处理与规则评估中，需要明确“未缴费企业”的判定方式，作为状态流转和待办生成的基础。

## 版本演进

v0.1 草稿：基于数据库字段语义确定口径，后续可关联规则优先级链与到期处理结果进行验证。

```ground:caliber
name: 未缴费企业
predicate: "ca_fee_company.pay_status = 'UNPAID'"
scope: 企业维度
evidence: db
```

相关：[[ca_fee_company]]、[[ca_fee_company_pay_status]]、[[fee_rule_priority_chain]]、[[service_expiry_processing]]