---
type: enum
title: ca_data_source
page_key: ca_data_source
domain: CA证书认证
status: draft
aliases: [CA数据来源]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaDataSourceEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# ca_data_source

[[ca_certification_info]] 的 `data_source`。`CaDataSourceEnum` 无 displayName，label 取类 Javadoc 对三个常量的说明。

```ground:enum
enum: ca_data_source
fields: [ca_certification_info.data_source]
values:
  "OPERATION_PLATFORM":
    label: "运营中台 notifyActivateCa 链路落库"
  "FBP_PORTAL":
    label: "产融门户一证四步落库"
  "CHANNEL_OPENAPI":
    label: "渠道 OpenAPI 入站建档落库"
```
