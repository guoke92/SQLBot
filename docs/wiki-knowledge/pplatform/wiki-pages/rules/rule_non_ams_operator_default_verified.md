---
type: rule
title: 非AMS来源新增经办人默认认证通过
page_key: rule_non_ams_operator_default_verified
belong: rules
domain: customer
status: published
aliases: []
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.cust_build_status, cust_person_info.source]
scope:
  databases: [lowcode_pplatform]
---

该规则规定非AMS来源新增经办人时，建档状态自动设为 `BUILD_SUCCESS`，无需后续实名认证。

## 需求背景

`insertOrUpdatePerson` 中若 `source != AMS`，设置 `cust_build_status=BUILD_SUCCESS`。这意味着只有AMS来源新增经办人才需要后续实名认证，其他来源默认通过。

## 版本演进

规则来自代码路径 `CustPersonApplication.insertOrUpdatePerson`，与联系人实名认证状态机联动。

```ground:rule
name: 非AMS来源新增经办人默认认证通过
content: "insertOrUpdatePerson中若source != AMS，设置cust_build_status=BUILD_SUCCESS"
impact: 只有AMS来源新增经办人才需要后续实名认证，其他来源默认通过
field_targets:
  - "cust_person_info.cust_build_status"
  - "cust_person_info.source"
evidence: "code_path:CustPersonApplication.insertOrUpdatePerson"
```

相关：[[cust_person_info]]
