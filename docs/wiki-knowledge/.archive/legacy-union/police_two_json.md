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
type: enum
title: CA实名核验方式
page_key: police_two_json
domain: certification
aliases:
- 实名方式
- 公安二要素
- 企业三要素
anchors:
- police_two_json
---
# CA实名核验方式

实名认证按核验方式落不同 JSON 列；POLICE_TWO 落 police_two_json，ENTERPRISE_THREE/ENTERPRISE_FOUR 落 enterprise_four_json。

```ground:enum
enum: police_two_json
fields:
- ca_certification_info.police_two_json
- ca_certification_info.enterprise_four_json
values:
  POLICE_TWO:
    label: 公安二要素
  ENTERPRISE_THREE:
    label: 企业三要素
  ENTERPRISE_FOUR:
    label: 企业四要素
```

## 关联
- [[ca_certification_info|ca_certification_info]]
