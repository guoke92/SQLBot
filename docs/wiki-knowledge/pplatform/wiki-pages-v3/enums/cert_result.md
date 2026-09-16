---
type: enum
title: cert_result
page_key: cert_result
domain: 经办人/联系人/管理员管理
status: draft
aliases: [自动认证通过]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# cert_result

`CustCertificationResultTypeEnum`，用于人脸/手机号实名分项。综合结论在 [[real_name_result]]。

```ground:enum
enum: cert_result
fields:
  - cust_person_info.face_status
  - cust_person_info.phone_realname_status
values:
  "TO_BE_VERIFIED":
    label: "待核查"
  "AUTOMATIC_AUTHENTICATION_PASSED":
    label: "自动认证通过"
  "AUTOMATIC_AUTHENTICATION_FAILED":
    label: "自动认证不通过"
  "MANUAL_AUTHENTICATION_PASSED":
    label: "人工认证通过"
  "MANUAL_AUTHENTICATION__FAILED":
    label: "人工认证不通过"
  "NO_RECORD":
    label: "库无记录"
```
