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
title: CA认证成功企业/个人
page_key: CA认证成功企业-个人
domain: certification
field_targets:
- ca_certification_info.submit_status
---
# CA认证成功企业/个人

CA 认证结果为 SUCCESS 的记录。

```ground:caliber
caliber: CA认证成功企业/个人
field_targets:
- ca_certification_info.submit_status
filters:
- .ca_cert.submit_status = 'SUCCESS'
```

## 关联
- [[ca_certification_info]]
