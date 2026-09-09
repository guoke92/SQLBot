---
type: enum
title: platform_operator
page_key: platform_operator
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

# platform_operator

（权威枚举页：2 值，绑定方式 exact-name，主承载 tenant_setting_config.platform_operator；db 实测分布，基线外 4 值。）

```ground:enum
enum: platform_operator
fields: [tenant_setting_config.platform_operator, tenant_setting_config_share.platform_operator]
values:
  TENANT:
    label: 租户自身
  PLATFORM:
    label: 联易融
  "[\"platform\",\"tenant\"]":
    label: "[\"platform\",\"tenant\"]"
    note: db 分布存在但代码枚举未声明（REVIEW）
  "[\"platform\"]":
    label: "[\"platform\"]"
    note: db 分布存在但代码枚举未声明（REVIEW）
  "[\"tenant\",\"platform\"]":
    label: "[\"tenant\",\"platform\"]"
    note: db 分布存在但代码枚举未声明（REVIEW）
  "[\"tenant\"]":
    label: "[\"tenant\"]"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
