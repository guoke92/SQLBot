---
type: rule
title: 企业管理员变更即作废原授权书
page_key: manager_change_invalidate_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 管理员变更作废授权
  - 授权主体切换规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
belong: rules
---

管理员换人时“先作废、后重建”：先把原管理员在该企业下的全部授权记录置 `enable=N`、`authed_status=N`（remark 记录 to|新管理员|原因），再为新管理员按企业各角色创建/更新 `authed_status=Y` 的授权记录。这是 [[authed_status_state_flow]] 中 Y→N 迁移的唯一来源，也解释了 [[auth_agreement_authed_n]] 记录偏多的现象。

```ground:rule
name: 企业管理员变更即作废原授权书
content: "管理员换人时先把原管理员在该企业下的全部授权记录 enable=N、authed_status=N（remark 记录 to|新管理员|原因），再为新管理员按企业各角色创建/更新 authed_status=Y 的授权记录"
impact: "保证授权主体与当前管理员一致"
field_targets:
  - authorization_agreement.enable
  - authorization_agreement.authed_status
  - authorization_agreement.cust_manager_id
  - authorization_agreement.creation_type
evidence: "code:CustAuthAgreementDomainService.java:changeCompanyAuthorizationAgreement + disabledAllAuthorizationAgreement"
```