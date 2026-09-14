---
type: process
title: 联系人实名结果（real_name_result）
page_key: real_name_result
domain: 经办人/联系人/管理员管理
status: draft
aliases: [实名结果, INIT, VERIFIED_SUCCESS, VERIFIED_FAILED]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.real_name_result", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
belong: processes
---

real_name_result 是实名认证结果字段，使用 INIT / VERIFIED_SUCCESS / VERIFIED_FAILED 一套独立码值，与 phone_realname_status、face_status 的认证码值并行存在。人脸认证回写与人工核验通过都会推进到 VERIFIED_SUCCESS（[[phone_realname_status]]、[[realname_status]]）。

## 需求背景
- 继承逻辑除了写 phone_realname_status，还会写 real_name_result=VERIFIED_SUCCESS 并继承证件号/类型/有效期（[[new_person_inherit_verified]]）。

## 版本演进
- 当前版本中 INIT 是初始态；VERIFIED_FAILED 目前仅有 DB 分布证据，未定位到写值代码路径。

```ground:process
name: 联系人实名结果
field: cust_person_info.real_name_result
states:
  - value: INIT
    label: 初始化/待认证
    source: db_dist
  - value: VERIFIED_SUCCESS
    label: 认证成功
    source: code_enum
  - value: VERIFIED_FAILED
    label: 认证失败
    source: db_dist
transitions:
  - from: INIT
    event: "人脸认证回写"
    to: VERIFIED_SUCCESS
    evidence: "code_path:CustPersonApplication.java:updateFaceStatus"
  - from: INIT
    event: "人工实名核验通过"
    to: VERIFIED_SUCCESS
    evidence: "code_path:CustPersonApplication.java:updateVerifyNameStatus"
  - from: INIT
    event: "认证不通过"
    to: VERIFIED_FAILED
    evidence: "db_dist:cust_person_info.real_name_result"
```

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[realname_status]]。