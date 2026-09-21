---
type: process
title: CA服务费企业缴费状态
page_key: ca_fee_company__pay_status
belong: processes
domain: ca_fee
status: draft
anchors: [ca_fee_company.pay_status]
field_targets: [ca_fee_company.pay_status]
sources: ['code_path:cafee/CaFeeOrderService.java:450', 'code_path:CaFeeRenewalService.java:173']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_company]
---

# CA服务费企业缴费状态

钉 ca_fee_company.pay_status。缴费成功写 PAID；服务到期任务写回 UNPAID。
这是宽表两态，不是规则引擎的 PAID/UNPAID/EXPIRED/EXEMPT。


```ground:process
process: CA服务费企业缴费状态
field: ca_fee_company.pay_status
entry: POST /cust-web/caFee
stages:
- stage: 已缴费
  transitions:
  - from: UNPAID
    event: syncCompanyAfterPaid
    to: PAID
    evidence: code_path:cafee/CaFeeOrderService.java:450
- stage: 到期
  transitions:
  - from: PAID
    event: markServiceExpired
    to: UNPAID
    evidence: code_path:CaFeeRenewalService.java:173
```

## 页面链接

- [[tables/ca_fee_company]]
- [[dicts/ca_fee_company__pay_status]]
