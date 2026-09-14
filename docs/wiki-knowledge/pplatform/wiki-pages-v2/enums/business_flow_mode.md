---
type: enum
title: business_flow_mode
page_key: business_flow_mode
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




# business_flow_mode

（权威枚举页：4 值，绑定方式 db-profile，主承载 tenant_project_approval_business_info.business_flow_mode；db 实测分布。）

```ground:enum
enum: business_flow_mode
fields: [tenant_project_approval_business_info.business_flow_mode]
values:
  "CONFIRM_RIGHT_AFTER":
    label: "CONFIRM_RIGHT_AFTER"
  "CONFIRM_RIGHT_FIRST":
    label: "CONFIRM_RIGHT_FIRST"
  "先确权":
    label: "先确权"
  "后确权":
    label: "后确权"
```
