---
type: enum
title: asset_list_mode
page_key: asset_list_mode
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---




# asset_list_mode

（权威枚举页：2 值，绑定方式 db-profile，主承载 tenant_project_approval_business_info.asset_list_mode；db 实测分布。）

```ground:enum
enum: asset_list_mode
fields: [tenant_project_approval_business_info.asset_list_mode]
values:
  "SIMPLE_LIST":
    label: "SIMPLE_LIST"
  "STANDARD_LIST":
    label: "STANDARD_LIST"
```
