---
type: caliber
title: 有效接入渠道
page_key: valid_access_channel
domain: 准入接入与接入密钥
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_access_secret.enable
---

OpenAPI / 准入校验使用的有效渠道。

```ground:caliber
name: 有效接入渠道
predicate: "cust_access_secret.enable = 'Y'"
scope: cust_access_secret
evidence: code
```
