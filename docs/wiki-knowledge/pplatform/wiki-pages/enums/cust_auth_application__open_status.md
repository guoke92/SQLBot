---
type: enum
title: open_status
page_key: cust_auth_application__open_status
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

（权威枚举页：3 值，绑定方式 setter-evidence，主承载 cust_auth_application.open_status；db 实测分布。）

```ground:enum
enum: cust_auth_application__open_status
fields: [cust_auth_application.open_status, cust_interworking_product.open_status]
values:
  NOT_OPENED:
    label: 未开通
  OPENING:
    label: 开通中：带客户确认 forams
  OPENED:
    label: 已开通
```
