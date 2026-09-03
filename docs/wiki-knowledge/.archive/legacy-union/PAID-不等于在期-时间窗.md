---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: PAID 不等于在期（时间窗）
page_key: PAID-不等于在期-时间窗
domain: CA认证与服务费
field_targets:
- ca_fee_company.service_end
- ca_fee_company.pay_status
---
# PAID 不等于在期（时间窗）

到期任务把 service_end<today 的 PAID 翻回 UNPAID，但任务按日调度存在时间窗； 严格口径用 service_end >= today（服务期内）而非 pay_status=PAID。

```ground:rule
rule: paid-not-inperiod-window
field_targets:
- ca_fee_company.service_end
- ca_fee_company.pay_status
impact: query_constraint
content: 到期任务把 service_end<today 的 PAID 翻回 UNPAID，但任务按日调度存在时间窗； 严格口径用 service_end
  >= today（服务期内）而非 pay_status=PAID。
scope: 精确的"在保企业"统计
```

## 关联
- [[ca_fee_company]]
