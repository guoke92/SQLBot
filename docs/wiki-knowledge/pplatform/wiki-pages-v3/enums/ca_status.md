---
type: enum
title: ca_status
page_key: ca_status
domain: CA证书收费
status: draft
aliases: [CA签章状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeCertStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# ca_status

[[ca_fee_company]] 的 `ca_status`：签章中台查询结果写入的证书快照（`CaFeeCertStatusEnum`）。`UNKNOWN` 的 displayName 与 `UNREGISTERED` 同为「未注册」；`API_NOTES` 另写 UNKNOWN 为「查询失败/未知」，以构造函数 displayName 为准。

库分布目前是 `NORMAL` / `CANCELLED` / `UNKNOWN`。`EXPIRED`、`UNREGISTERED` 在枚举中，本列快照里尚未见到。

```ground:enum
enum: ca_status
fields: [ca_fee_company.ca_status]
values:
  "NORMAL":
    label: "有效"
  "EXPIRED":
    label: "已过期"
  "CANCELLED":
    label: "已注销"
  "UNREGISTERED":
    label: "未注册"
  "UNKNOWN":
    label: "未注册"
```
