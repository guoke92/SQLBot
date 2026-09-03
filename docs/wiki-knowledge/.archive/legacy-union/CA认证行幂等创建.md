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
title: CA认证行幂等创建
page_key: CA认证行幂等创建
domain: certification
field_targets:
- ca_certification_info.cust_id
- ca_certification_info.data_date
- ca_certification_info.head_company_data
- ca_certification_info.submit_status
---
# CA认证行幂等创建

以 (custId, dataDate, headCompanyData, submitStatus=PENDING) 为幂等键，命中则返回已有行，不重复建行。

```ground:rule
rule: ca-idempotent-create
field_targets:
- ca_certification_info.cust_id
- ca_certification_info.data_date
- ca_certification_info.head_company_data
- ca_certification_info.submit_status
impact: query_constraint
content: 以 (custId, dataDate, headCompanyData, submitStatus=PENDING) 为幂等键，命中则返回已有行，不重复建行。
scope: 初始化或重试 CA 认证
```

## 关联
- [[ca_certification_info]]
