---
type: enum
title: phone_realname_status
page_key: phone_realname_status
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCertificationResultTypeEnum.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# phone_realname_status

[[cust_person_info]] 的 `phone_realname_status`。

```ground:enum
enum: phone_realname_status
fields: [cust_person_info.phone_realname_status]
values:
  "AUTOMATIC_AUTHENTICATION_FAILED":
    label: "自动认证不通过"
  "AUTOMATIC_AUTHENTICATION_PASSED":
    label: "自动认证通过"
  "MANUAL_AUTHENTICATION_PASSED":
    label: "人工认证通过"
  "MANUAL_AUTHENTICATION__FAILED":
    label: "人工认证不通过"
  "NO_RECORD":
    label: "库无记录"
  "TO_BE_VERIFIED":
    label: "待核查"
```
