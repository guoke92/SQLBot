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
type: pattern
title: 服务费台账统计（总数/已缴/未缴/缴费率/本月实缴）
page_key: ledger-statistics
domain: CA认证与服务费
anchors:
- ca_fee_company
- ca_fee_order
---
# 服务费台账统计（总数/已缴/未缴/缴费率/本月实缴）

问法：服务费台账统计（总数/已缴/未缴/缴费率/本月实缴）

```ground:pattern
pattern: ledger-statistics
question: 服务费台账统计（总数/已缴/未缴/缴费率/本月实缴）
sql: "SELECT COUNT(*) AS total,\n       SUM(CASE WHEN pay_status = 'PAID' THEN 1 ELSE\
  \ 0 END) AS paid\nFROM ca_fee_company WHERE enable = 'Y'; SELECT IFNULL(SUM(pay_amount),\
  \ 0) FROM ca_fee_order WHERE order_status = 'PAID' AND enable = 'Y'\n  AND pay_time\
  \ BETWEEN ? AND ?;"
verification: PENDING_VALIDATION
```

## 关联
- [[ca_fee_company]]
- [[ca_fee_order]]
