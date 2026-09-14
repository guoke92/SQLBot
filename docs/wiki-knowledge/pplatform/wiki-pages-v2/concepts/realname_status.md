---
type: concept
title: 实名认证状态
page_key: realname_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [phone_realname_status, face_status, realname_status]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.phone_realname_status", "db:cust_person_info.real_name_result", "code_path:CustPersonApplication.java:updateVerifyNameStatus"]
contract_version: "0.1"
maps_to: cust_person_info.phone_realname_status
field_targets:
  - cust_person_info.phone_realname_status
  - cust_person_info.face_status
  - cust_person_info.real_name_result
adjudication: boundary
also_confused_with:
  - cust_person_info.real_name_result
  - cust_person_info.face_status
  - cust_person_info.realname_status
boundary: "phone_realname_status 与 face_status 共用同一套认证结果码值（TO_BE_VERIFIED/AUTO_PASSED/MANUAL_PASSED/AUTO_FAILED），real_name_result 是另一套 INIT/VERIFIED_* 码值；DB 中 realname_status 与 phone_realname_status 并存但分布差异极大，需区分使用。"
belong: concepts
field_targets: [cust_person_info.phone_realname_status]
---

"实名认证状态"在代码与需求文档里指代多个字段，必须按字段区分：phone_realname_status（手机号维度）与 face_status（人脸维度）共用同一套认证码值；real_name_result 使用 INIT/VERIFIED_* 另一套码值（[[phone_realname_status]]、[[real_name_result]]）。

## 需求背景
- 前端弹框判断依赖认证通过状态，因此字段选错会直接表现为"认证框重复弹出/不弹出"。
- 新增经办人继承逻辑会同时写 phone_realname_status 与 real_name_result（[[new_person_inherit_verified]]）。

## 版本演进
- DB 中 realname_status 与 phone_realname_status 并存且分布差异极大，realname_status 未纳入本次字段语义清单，使用前需另行核实。

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[real_name_result]]、[[new_person_inherit_verified]]。