---
type: caliber
title: 已过期短链
page_key: expired_short_link
domain: 通知/验证码/短链
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
  - short_link.is_forever
  - short_link.expire_time
---

非永久且已过 expire_time。

```ground:caliber
name: 已过期短链
predicate: "short_link.is_forever = 'N' AND short_link.expire_time <= NOW()"
scope: short_link
evidence: code
```
