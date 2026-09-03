---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: CA 提交幂等键
page_key: CA-提交幂等键
domain: ca_certification
field_targets:
- ca_certification_info.submit_status
---
# CA 提交幂等键

提交幂等键为 (cust_id, data_date, head_company_data)；submit_status=PENDING 表示未提交。

```ground:rule
rule: ca-cert-idempotent-key
field_targets:
- ca_certification_info.submit_status
impact: query_constraint
content: 提交幂等键为 (cust_id, data_date, head_company_data)；submit_status=PENDING 表示未提交。
scope: 提交中、提交失败重试
```

## 关联
- [[ca_certification_info]]
