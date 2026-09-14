---
type: rule
title: 新增经办人继承已认证信息
page_key: new_person_inherit_verified
domain: 经办人/联系人/管理员管理
status: draft
aliases: [实名继承, insertOrUpdatePerson]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#insertOrUpdatePerson"]
contract_version: "0.1"
belong: rules
---

同一 db_tenant_code 下若已存在 phone_realname_status ∈ {AUTOMATIC_AUTHENTICATION_PASSED, MANUAL_AUTHENTICATION_PASSED} 的记录，新增经办人直接置自动认证通过 + real_name_result=VERIFIED_SUCCESS，并继承证件号/证件类型/有效期（[[phone_realname_status]]、[[real_name_result]]）。

## 需求背景
- 该规则实现跨企业复用实名结果，减少重复认证；继承范围含证件信息，若证件有效期过期仍会沿用，需注意（[[realname_status]]）。

## 版本演进
- 当前版本继承判定按 db_tenant_code 维度，而非企业维度。

```ground:rule
name: 新增经办人继承已认证信息
content: "同 db_tenant_code 下若存在 phone_realname_status ∈ {AUTOMATIC_AUTHENTICATION_PASSED, MANUAL_AUTHENTICATION_PASSED} 的记录，则新经办人直接置自动认证通过 + real_name_result=VERIFIED_SUCCESS，并继承证件号/证件类型/有效期"
impact: 跨企业复用实名结果，减少重复认证
field_targets:
  - cust_person_info.phone_realname_status
  - cust_person_info.real_name_result
  - cust_person_info.certification_no
evidence: "code_path:CustPersonApplication.java#insertOrUpdatePerson"
```

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[real_name_result]]、[[realname_status]]。