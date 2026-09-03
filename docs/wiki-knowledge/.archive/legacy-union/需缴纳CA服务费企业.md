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
title: 需缴纳CA服务费企业
page_key: 需缴纳CA服务费企业
domain: cafee
field_targets:
- ca_fee_project_config.charge_enabled
- ca_fee_company.pay_status
- ca_fee_company.service_end
---
# 需缴纳CA服务费企业

项目 charge_enabled=Y、非白名单/非0元豁免、服务费未在期内的企业。

```ground:caliber
caliber: 需缴纳CA服务费企业
field_targets:
- ca_fee_project_config.charge_enabled
- ca_fee_company.pay_status
- ca_fee_company.service_end
filters:
- .project_config.charge_enabled = 'Y'
- .company.pay_status = 'UNPAID'
```

## 关联
- [[ca_fee_company]]
- [[ca_fee_project_config]]
