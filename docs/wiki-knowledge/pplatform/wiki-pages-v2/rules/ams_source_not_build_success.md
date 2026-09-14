---
type: rule
title: AMS 来源不置建档成功
page_key: ams_source_not_build_success
domain: 经办人/联系人/管理员管理
status: draft
aliases: [AMS, source≠AMS, 建档成功写入条件]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#insertOrUpdatePerson"]
contract_version: "0.1"
belong: rules
---

新增经办人仅当 source ≠ AMS 时才写 setCustBuildStatus(BUILD_SUCCESS)；AMS 来源交由运营中台流程驱动，不在此处置为已建档（[[source]]、[[cust_build_status]]）。

## 需求背景
- 该规则用于防止外部同步数据被误标为已建档，进而误触发关联重建（[[rel_rebuild_precondition]]）。

## 版本演进
- 当前版本以 AMS 为唯一排除值；longteng 等其他来源不在排除范围内。

```ground:rule
name: AMS 来源不置建档成功
content: "新增经办人仅当 source ≠ AMS 时才 setCustBuildStatus(BUILD_SUCCESS)；AMS 来源交由运营中台流程驱动"
impact: 防止外部同步数据被误标为已建档
field_targets:
  - cust_person_info.source
  - cust_person_info.cust_build_status
evidence: "code_path:CustPersonApplication.java#insertOrUpdatePerson"
```

相关页面：[[cust_person_info]]、[[source]]、[[cust_build_status]]、[[rel_rebuild_precondition]]。