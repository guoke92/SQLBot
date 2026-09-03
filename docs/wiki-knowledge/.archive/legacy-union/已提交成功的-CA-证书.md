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
title: 已提交成功的 CA 证书
page_key: 已提交成功的-CA-证书
domain: ca_certification
field_targets:
- ca_certification_info.submit_status
- ca_certification_info.enable
---
# 已提交成功的 CA 证书

submit_status=SUCCESS 且 enable=Y。

```ground:caliber
caliber: 已提交成功的 CA 证书
field_targets:
- ca_certification_info.submit_status
- ca_certification_info.enable
filters:
- .ca_certification.submit_status = 'SUCCESS'
- .ca_certification.enable = 'Y'
```

## 关联
- [[ca_certification_info]]
