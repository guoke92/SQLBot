---
type: caliber
title: 需开通电子签章
page_key: need_register_ca
domain: 授权协议与电子授权
status: draft
aliases:
  - 需要开通电子签章
  - need_register_ca=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
belong: calibers
---

判断企业是否需要 CFCA 电子签章能力的口径，是「意愿」而非「结果」，必须与 [[cfca_registered]] 同时成立才视为已开通，见 [[electronic_seal_activation]]。简易认证场景下即使该字段为 Y 也会被强制校正为不开通，见 [[simple_identify_disable_ca]]。

```ground:caliber
name: 需开通电子签章
predicate: "cust_company_info.need_register_ca = 'Y'"
scope: "判断企业是否需要 CFCA 电子签章能力"
evidence: "code:CustAuthSignOrchestrationApplication.java:isCaRegistered"
```