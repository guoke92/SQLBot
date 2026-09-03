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
type: caliber
title: CA认证待处理
page_key: CA认证待处理
domain: certification
field_targets:
- ca_certification_info.submit_status
---
# CA认证待处理

CA 认证已提交、未收到终态结果。

```ground:caliber
caliber: CA认证待处理
field_targets:
- ca_certification_info.submit_status
filters:
- .ca_cert.submit_status = 'PENDING'
```

## 关联
- [[ca_certification_info]]
