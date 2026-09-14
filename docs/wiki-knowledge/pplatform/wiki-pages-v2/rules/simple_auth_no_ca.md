---
type: rule
title: 简易认证不支持开通电子签章规则
page_key: simple_auth_no_ca
domain: 平台事件监听与同步
status: draft
aliases:
  - enforceMustNotOpenCa
  - 简易认证 CA 校正
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
belong: rules
---

简易认证路径提交时，即使入参 `need_register_ca=Y`，也会被强制校正为不开通并落库。

## 需求背景

由 `CustCompanyCaPolicy.enforceMustNotOpenCa` 执行校正，字段落点为 [[cust_company_info]].`need_register_ca` 与 `ca_register_status`。业务意图是阻断简易认证走电子签章开通流程。该分支与建档状态机的 `AWAIT_CUST_CONFIRM` 状态配套，见 [[cust_build_status]]。

## 版本演进

- 校正发生在提交时而非登记时，失败重试路径（[[compensation_fail_type]]）是否会再次校正需结合重放上下文判断。

```ground:rule
name: 简易认证不支持开通电子签章
content: 简易认证提交时若 needRegisterCa=Y，强制校正为不开通并落库（CustCompanyCaPolicy.enforceMustNotOpenCa）
impact: 阻断简易认证走 CA 开通
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
evidence: "code:CustCompanyInfoApplication.java:submitForSimpleAuth"
```