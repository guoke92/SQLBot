---
type: rule
title: 简易建档强制不开通电子签章，head_company 为空置 'Y'
page_key: simple_auth_ca_forbidden
domain: 平台内部服务对接
status: draft
aliases:
  - 简易认证签章政策
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.need_register_ca]
  - semantic:field_semantics[cust_company_info.head_company]
contract_version: "0.1"
belong: rules
---

简易建档路径下，need_register_ca 政策上强制为不开通；head_company 为空时（简易认证）置为 'Y'。

## 需求背景

这条政策决定简易认证企业不会走 CA 开通流程，因而对外签章状态口径（[[calibers/ca_register_status_output]]）在这类企业上恒为未开通。简易认证的状态流转见 [[processes/cust_build_status_machine]]。

## 版本演进

v0：首次成页。

```ground:rule
name: 简易建档强制不开通电子签章，head_company 为空置 'Y'
field: cust_company_info.need_register_ca / cust_company_info.head_company
condition: "简易建档；head_company 为空（简易认证）"
effect: "need_register_ca 强制不开通；head_company 置 'Y'"
evidence: code
```