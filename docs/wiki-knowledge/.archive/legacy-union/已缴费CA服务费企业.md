---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: caliber
title: 已缴费CA服务费企业
page_key: 已缴费CA服务费企业
domain: cafee
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.enable
---
# 已缴费CA服务费企业

ca_fee_company.pay_status=PAID 且 enable=Y 的企业。

```ground:caliber
caliber: 已缴费CA服务费企业
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.enable
filters:
- .company.pay_status = 'PAID'
- .company.enable = 'Y'
```

## 关联
- [[ca_fee_company]]
