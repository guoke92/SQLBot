---
type: rule
title: 变更记录取 status=CUST_CHECK_PASS 的最新有效记录
page_key: cust_change_record_latest_effective
domain: 平台内部服务对接
status: draft
aliases:
  - 变更记录取值规则
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_change_record.cust_id / status / oper_cust_info / oper_channel / create_time]
contract_version: "0.1"
belong: rules
---

读取客户变更记录时，以 status 为 CUST_CHECK_PASS 作为有效判据，并取最新的那条记录。

## 需求背景

该记录承载变更态下的运营中台企业 id（见 [[rules/change_status_token_source]]、[[concepts/platform_cust_id_bridge]]），取值错误会直接导致换 token 失败。

## 版本演进

v0：首次成页。

```ground:rule
name: 变更记录取 status=CUST_CHECK_PASS 的最新有效记录
field: cust_change_record.status
condition: "status = CUST_CHECK_PASS"
effect: "作为取值最新有效记录"
evidence: code
```