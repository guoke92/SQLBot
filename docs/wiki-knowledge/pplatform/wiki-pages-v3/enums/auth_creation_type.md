---
type: enum
title: auth_creation_type
page_key: auth_creation_type
domain: 授权协议与电子授权
status: draft
aliases: [管理员变更授权书]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# auth_creation_type

`AuthAgreementCreationTypeEnum`，displayName 取第三参数。落库 dictKey 与枚举名不完全相同。

```ground:enum
enum: auth_creation_type
fields:
  - authorization_agreement.creation_type
values:
  "COMPANY_AUTH_AGGREMENT":
    label: "授权书变更"
  "CUST_BUILD_INIT":
    label: "企业发起认证"
  "AUTO":
    label: "迁移租户自动开通产品时"
  "COMPANY_MANAGER_CHANGE_CODE":
    label: "管理员变更"
```
