---
type: enum
title: open_status
page_key: tenant_interworking_product__open_status
belong: enums
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# open_status

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 tenant_interworking_product.open_status；db 实测分布。）

```ground:enum
enum: tenant_interworking_product__open_status
fields: [tenant_interworking_product.open_status, tenant_product.open_status]
values:
  Y:
    label: 已开通
  P:
    label: 开通中
  N:
    label: 未开通
```
