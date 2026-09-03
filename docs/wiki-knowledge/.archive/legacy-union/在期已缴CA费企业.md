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
title: 在期已缴CA费企业
page_key: 在期已缴CA费企业
domain: ca_fee
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.service_end
---
# 在期已缴CA费企业

企业台账pay_status=PAID且服务截止日不早于当前日期。

```ground:caliber
caliber: 在期已缴CA费企业
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.service_end
filters:
- .ca_fee_company.pay_status = 'PAID'
- .ca_fee_company.service_end gte 'CURRENT_DATE'
```

## 关联
- [[ca_fee_company]]
