---
type: process
title: 联系人实名认证状态（phone_realname_status）
page_key: phone_realname_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [手机号实名认证状态, 实名认证状态, face_status]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.phone_realname_status", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
belong: processes
---

phone_realname_status 表示手机号维度的实名认证进度，与 face_status 共用同一套码值。前端在 AUTO/MANUAL_AUTHENTICATION_PASSED 时不再弹认证框，因此该字段直接影响交互；它与 real_name_result 是两套码值，不可互换（[[real_name_result]]、[[realname_status]]）。

## 需求背景
- 同租户下已有认证通过记录时，新增经办人直接继承认证通过，减少重复认证成本（[[new_person_inherit_verified]]）。
- 免认证白名单只覆盖特定租户与角色（[[skip_realname_auth_whitelist]]）。

## 版本演进
- 当前版本的新增默认值为 TO_BE_VERIFIED；人工核验通过由 updateVerifyNameStatus 写入 MANUAL_AUTHENTICATION_PASSED；不通过状态当前仅见 DB 分布。

```ground:process
name: 联系人实名认证状态
field: cust_person_info.phone_realname_status
states:
  - value: TO_BE_VERIFIED
    label: 待核查
    source: db_dist
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: code_enum
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: code_enum
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动认证不通过
    source: db_dist
transitions:
  - from: ""
    event: "新增经办人默认待核查"
    to: TO_BE_VERIFIED
    evidence: "code_path:CustPersonApplication.java:insertOrUpdatePerson(setPhoneRealnameStatus(TO_BE_VERIFIED))"
  - from: TO_BE_VERIFIED
    event: "同租户下已存在认证通过记录，新增时继承"
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: "code_path:CustPersonApplication.java:insertOrUpdatePerson"
  - from: TO_BE_VERIFIED
    event: "人工实名核验通过"
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: "code_path:CustPersonApplication.java:updateVerifyNameStatus"
  - from: AUTOMATIC_AUTHENTICATION_PASSED
    event: "运营/风控侧回写不通过"
    to: AUTOMATIC_AUTHENTICATION_FAILED
    evidence: "db_dist:cust_person_info.phone_realname_status"
```

相关页面：[[cust_person_info]]、[[real_name_result]]、[[realname_status]]、[[new_person_inherit_verified]]。