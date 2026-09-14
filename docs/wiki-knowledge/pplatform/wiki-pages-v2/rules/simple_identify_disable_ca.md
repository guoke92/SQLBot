---
type: rule
title: 简易认证强制关闭电子签章
page_key: simple_identify_disable_ca
domain: 授权协议与电子授权
status: draft
aliases:
  - SIMPLE 不开 CA
  - 简易认证签章约束
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyCaPolicy.java
  - db:cust_company_info
contract_version: "0.1"
belong: rules
---

简易认证（`identify_style=SIMPLE`）链路不支持开通电子签章：提交时若 [[need_register_ca]] 为 Y，会被策略强制校正为不开通并落库。这直接影响 [[offline_eauth_sign_trigger]] 的第 ⑥ 个与门——简易认证企业不会走电子授权书签署。

```ground:rule
name: 简易认证强制关闭电子签章
content: "简易认证提交时如 need_register_ca=Y 则通过 CustCompanyCaPolicy.enforceMustNotOpenCa 强制校正为不开通并落库"
impact: "简易建档不支持开通电子签章"
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.identify_style
evidence: "code:CustCompanyCaPolicy.java:enforceMustNotOpenCa"
```