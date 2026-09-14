---
type: caliber
title: 授权书已授权
page_key: auth_agreement_authed_y
domain: 授权协议与电子授权
status: draft
aliases:
  - 已签署授权书
  - authed_status=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
belong: calibers
---

判断企业/管理员是否已签署授权书的口径。使用时注意：只有当记录 `enable=Y` 时，`authed_status=Y` 才代表当前有效授权——管理员变更会把原记录置 `enable=N` 并同时置 `authed_status=N`，见 [[manager_change_invalidate_agreement]] 与状态机 [[authed_status_state_flow]]。

```ground:caliber
name: 授权书已授权
predicate: "authorization_agreement.authed_status = 'Y'"
scope: "判断企业/管理员是否已签署授权书（enable=Y 时有效）"
evidence: "code:CustAuthAgreementDomainService.java:hasCompanySignedAuthAggrement + db"
```