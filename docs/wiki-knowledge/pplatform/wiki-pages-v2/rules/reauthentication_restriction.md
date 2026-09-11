---
type: rule
title: 重新认证限制
page_key: reauthentication_restriction
domain: 企业建档与认证
status: draft
aliases:
  - 重新认证前置条件
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyOperationApplication.java:reAuthentication
contract_version: "0.1"
---

仅当认证状态为 `CUST_CONFIRM_AWAIT`（待客户确认，见 [[pending_customer_confirm]]）时，才允许将其重置为 `INIT` 以重新认证；状态不符时会抛出异常。这条规则限定了认证状态机（[[enterprise_auth_status_machine]]）中 `CUST_CONFIRM_AWAIT → INIT` 这条回退边的可执行前提。

```ground:rule
name: 重新认证限制
content: 仅当认证状态为 CUST_CONFIRM_AWAIT 时，允许重置为 INIT 重新认证。
impact: 状态不符时抛异常。
field_targets:
  - cust_build_status
evidence: "code_path:CustCompanyOperationApplication.java:reAuthentication"
```

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据代码证据建立规则页。