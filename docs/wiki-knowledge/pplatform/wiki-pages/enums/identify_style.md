---
type: enum
title: identify_style
page_key: identify_style
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

# identify_style

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 cust_company_info.identify_style；db 实测分布。）

```ground:enum
enum: identify_style
fields: [cust_change_cfg.identify_style, cust_company_info.identify_style]
values:
  INVITE:
    label: 邀请认证
  INVITE_AGW:
    label: 邀请认证-内管录入
  SIMPLE:
    label: 简易认证
  SELF:
    label: 自主认证
```

## 表述差异

- INVITE: 权威「邀请认证」；另有表述 ['邀请认证-客户录入']
