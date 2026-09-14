---
type: caliber
title: CFCA 已开通
page_key: cfca_registered
domain: 授权协议与电子授权
status: draft
aliases:
  - CA 已开通
  - ca_register_status=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
belong: calibers
---

电子授权书在线签署的前置校验口径：必须同时满足 [[need_register_ca]]（意愿）与本口径（结果）。它与 `bs_register_status`（上上签）是并列的两个签章通道，见 [[electronic_seal_activation]]。若审核通过时本口径未命中则跳过签署，待 CA 重开成功回调后补偿触发，见 [[ca_delayed_compensation_sign]]。

```ground:caliber
name: CFCA 已开通
predicate: "cust_company_info.ca_register_status = 'Y'"
scope: "电子授权书在线签署前置校验（需同时 need_register_ca='Y'）"
evidence: "code:CustAuthSignOrchestrationApplication.java:isCaRegistered"
```