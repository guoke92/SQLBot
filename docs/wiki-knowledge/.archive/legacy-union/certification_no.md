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
type: enum
title: CA费企业台账
page_key: certification_no
domain: ca_fee
aliases:
- CA缴费企业
- 企业缴费状态
anchors:
- certification_no
---
# CA费企业台账

按统一社会信用代码维护企业维度的CA服务费状态与当前服务周期快照。

```ground:enum
enum: certification_no
fields:
- ca_fee_company.certification_no
- ca_fee_company.pay_status
values:
  PAID:
    label: 已缴费
  UNPAID:
    label: 未缴费
```

## 关联
- [[ca_fee_company|ca_fee_company]]
