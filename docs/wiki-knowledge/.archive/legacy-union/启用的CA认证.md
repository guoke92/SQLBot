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
title: 启用的CA认证
page_key: 启用的CA认证
domain: cafee
field_targets:
- ca_certification_info.enable
---
# 启用的CA认证

enable=Y 的记录。

```ground:caliber
caliber: 启用的CA认证
field_targets:
- ca_certification_info.enable
filters:
- .ca_certification_info.enable = 'Y'
```

## 关联
- [[ca_certification_info]]
