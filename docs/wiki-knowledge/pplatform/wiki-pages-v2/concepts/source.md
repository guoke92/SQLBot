---
type: concept
title: 来源
page_key: source
domain: 经办人/联系人/管理员管理
status: draft
aliases: [source, AMS, longteng]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.source", "code_path:CustPersonApplication.java:insertOrUpdatePerson"]
contract_version: "0.1"
maps_to: cust_person_info.source
field_targets:
  - cust_person_info.source
adjudication: boundary
also_confused_with:
  - cust_person_info.user_type
boundary: "source 表示数据来路（AMS=运营中台同步，longteng=龙腾），不是联系人身份；代码对比用 .name()/字面量，DB 中 AMS=417、longteng=69。"
belong: concepts
field_targets: [cust_person_info.source]
---

"来源"表示联系人数据的来路（AMS=运营中台同步，longteng=龙腾），不是联系人身份。代码中的比较既有 .name() 也有字面量写法，排查时需注意大小写与枚举一致性（[[cust_person_info]]、[[contact_person]]）。

## 需求背景
- 来源决定新增时是否直接置建档成功：AMS 来源不置，其余来源直接置 BUILD_SUCCESS（[[ams_source_not_build_success]]）。

## 版本演进
- DB 中 AMS=417、longteng=69；longteng 在代码枚举中未声明，属需要回填的取值点。

相关页面：[[cust_person_info]]、[[contact_person]]、[[ams_source_not_build_success]]、[[cust_build_status]]。