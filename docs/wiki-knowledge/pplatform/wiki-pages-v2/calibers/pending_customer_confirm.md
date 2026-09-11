---
type: caliber
title: 待客户确认
page_key: pending_customer_confirm
domain: 企业建档与认证
status: draft
aliases:
  - CUST_CONFIRM_AWAIT 判断
oid: 1
scope:
  databases: []
sources:
  - code:CustBuildStatusConstant.CUST_CONFIRM_AWAIT
contract_version: "0.1"
---

“待客户确认”是认证状态 `cust_build_status = 'CUST_CONFIRM_AWAIT'` 的记录集合（见 [[auth_status]]、[[enterprise_auth_status_machine]]）。处于该状态的企业已由平台或客户发起建档，等待客户侧确认或提交审核。

该状态是重新认证的唯一允许入口（见 [[reauthentication_restriction]]），同时也是运营退回后回落的目标状态；简易认证流程在该状态下可直接确认至认证成功。

```ground:caliber
name: 待客户确认
predicate: cust_company_info.cust_build_status = 'CUST_CONFIRM_AWAIT'
scope: 认证流程状态
evidence: "code_path:CustBuildStatusConstant.CUST_CONFIRM_AWAIT"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立口径页。