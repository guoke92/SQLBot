---
type: caliber
title: 待客户确认可重新认证
page_key: reauthentication_allowed
domain: 企业建档与认证
status: draft
aliases:
  - 允许重新认证
  - reAuthentication
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyOperationApplication.java:reAuthentication
contract_version: "0.1"
belong: calibers
---

"重新认证"动作的准入口径：只有当前处于待客户认证（`CUST_CONFIRM_AWAIT`）的企业，才允许被重置回 `INIT` 重走一遍认证流程。它是 [[processes/cust_build_status_state_machine]] 中 `CUST_CONFIRM_AWAIT → INIT` 这条回边的守卫条件。

```ground:caliber
name: 待客户确认可重新认证
predicate: cust_company_info.cust_build_status = 'CUST_CONFIRM_AWAIT'
scope: 仅该状态允许 reAuthentication
evidence: code_path:CustCompanyOperationApplication.java:reAuthentication
```

## 需求背景

客户长时间未完成确认时，运营需要能主动把流程打回起点重新发起，而不必新建一条企业记录；限制在单一前置状态是为了避免打断已在运营中台审核中的流程。

## 版本演进

v0 初稿：口径固化自 `reAuthentication` 的校验。是否为唯一入口（存在其他重置路径）待复核。

关联：[[concepts/cust_confirm_await]]、[[calibers/judge_have_applying_record]]。