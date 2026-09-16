---
type: caliber
title: 已生效租户
page_key: active_tenant
domain: 租户配置/灰度/运营邮件
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
  - tenant_setting_config.enable
  - tenant_setting_config.status
---

`listActicveAll` 使用的已生效租户。

```ground:caliber
name: 已生效租户
predicate: "tenant_setting_config.enable = 'Y' AND tenant_setting_config.status = 'Y'"
scope: tenant_setting_config
evidence: code
```
