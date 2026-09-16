---
type: caliber
title: 上送成功的认证行
page_key: ca_submit_success
domain: CA证书认证
status: draft
aliases: [submit_status=SUCCESS]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:ca_certification_info"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets: [ca_certification_info.submit_status]
---

列在 [[ca_certification_info]]。不等于企业 [[ca_registered_company]]。

```ground:caliber
name: 上送成功的认证行
predicate: "ca_certification_info.submit_status = 'SUCCESS'"
scope: ca_certification_info
evidence: db
```
