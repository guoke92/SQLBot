---
type: enum
title: face_status
page_key: face_status
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

# face_status

[[cust_person_info]] 的 `face_status`。

```ground:enum
enum: face_status
fields: [cust_person_info.face_status]
values:
  "AUTOMATIC_AUTHENTICATION_FAILED":
    label: "自动认证不通过"
  "AUTOMATIC_AUTHENTICATION_PASSED":
    label: "自动认证通过"
  "MANUAL_AUTHENTICATION_PASSED":
    label: "人工认证通过"
  "TO_BE_VERIFIED":
    label: "待核查"
```
