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
title: CA认证状态取值
page_key: CA认证状态取值
domain: certification
field_targets:
- ca_certification_info.submit_status
---
# CA认证状态取值

ca_certification_info.submit_status 只允许 PENDING/SUCCESS/FAIL，结果以中台回调为准。

```ground:rule
rule: ca-cert-status-valid
field_targets:
- ca_certification_info.submit_status
impact: query_constraint
content: ca_certification_info.submit_status 只允许 PENDING/SUCCESS/FAIL，结果以中台回调为准。
scope: CA 认证状态查询
```

## 关联
- [[ca_certification_info]]
