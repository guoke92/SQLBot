---
type: caliber
title: 已认证授权书
page_key: authed_agreement
domain: 授权协议与电子授权
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
  - authorization_agreement.authed_status
---

授权书认证状态为 Y。

```ground:caliber
name: 已认证授权书
predicate: "authorization_agreement.authed_status = 'Y'"
scope: authorization_agreement
evidence: code
```
