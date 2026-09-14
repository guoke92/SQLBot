---
type: caliber
title: 授权书未授权
page_key: auth_agreement_authed_n
domain: 授权协议与电子授权
status: draft
aliases:
  - 未签署授权书
  - authed_status=N
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
belong: calibers
---

需补签授权书的判定口径，与 [[auth_agreement_authed_y]] 互补。DB 中该值占比更高（19547 条），部分来源是管理员变更导致的作废（`enable=N` 且 `authed_status=N`），须结合 `enable` 与 `cust_source` 判断是否真的需要补签，见 [[migratory_supplement_exemption]]、[[auth_agreement_supplement_flag]]。

```ground:caliber
name: 授权书未授权
predicate: "authorization_agreement.authed_status = 'N'"
scope: "需补签授权书的判定口径"
evidence: "code + db"
```