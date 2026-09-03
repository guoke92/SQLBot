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
title: 未缴CA费企业
page_key: 未缴CA费企业
domain: ca_fee
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.enable
---
# 未缴CA费企业

企业台账pay_status=UNPAID且启用。

```ground:caliber
caliber: 未缴CA费企业
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.enable
filters:
- .ca_fee_company.pay_status = 'UNPAID'
- .ca_fee_company.enable = 'Y'
```

## 关联
- [[ca_fee_company]]
