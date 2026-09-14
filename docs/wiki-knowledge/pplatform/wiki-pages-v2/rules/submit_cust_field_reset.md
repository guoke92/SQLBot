---
type: rule
title: 提交建档时的字段重置（check_status 置 null、audit_back_flag 置 'N'）
page_key: submit_cust_field_reset
domain: 平台内部服务对接
status: draft
aliases:
  - 提交建档字段重置
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.check_status]
  - semantic:field_semantics[cust_company_info.audit_back_flag]
contract_version: "0.1"
belong: rules
---

提交建档时把 check_status 置为 null；非自主录入的提交路径把 audit_back_flag 置为 'N'。

## 需求背景

这两步是进入审核前的状态清理，配合建档状态机（[[processes/cust_build_status_machine]]）的提交分支生效。判定分支取决于认证方式（[[concepts/identify_style_bridge]]）。

## 版本演进

v0：首次成页。

```ground:rule
name: 提交建档时的字段重置
field: cust_company_info.check_status / cust_company_info.audit_back_flag
condition: "提交建档；非自主录入提交"
effect: "check_status 置 null；audit_back_flag 置 'N'"
evidence: code
```