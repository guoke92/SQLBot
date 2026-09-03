---
type: enum
title: auto_verify_status
page_key: auto_verify_status
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

# auto_verify_status

（权威枚举页：6 值，绑定方式 setter-evidence，主承载 cust_certification_info.auto_verify_status；db 实测分布。）

```ground:enum
enum: auto_verify_status
fields: [cust_certification_info.auto_verify_status, cust_person_info.face_status, cust_person_info.phone_realname_status]
values:
  TO_BE_VERIFIED:
    label: 待核查
  AUTOMATIC_AUTHENTICATION_PASSED:
    label: 自动认证通过
  AUTOMATIC_AUTHENTICATION_FAILED:
    label: 自动认证不通过
  MANUAL_AUTHENTICATION_PASSED:
    label: 人工认证通过
  MANUAL_AUTHENTICATION__FAILED:
    label: 人工认证不通过
  NO_RECORD:
    label: 库无记录
```
