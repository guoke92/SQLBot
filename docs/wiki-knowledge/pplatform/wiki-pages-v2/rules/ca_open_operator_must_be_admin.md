---
type: rule
title: CA 开通操作人必须是企业管理员
page_key: ca_open_operator_must_be_admin
domain: CA证书认证
status: draft
aliases: [CA_CERT_NOT_ADMIN, 管理员校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
contract_version: "0.1"
belong: rules
---

pre4Step 校验当前登录用户手机号命中 cust_person_info（user_type=admin、enable=Y、company_type=登录角色、ref_cust_company_info=企业 code），否则抛 CA_CERT_NOT_ADMIN。

**影响**：非管理员无法进入一证四步。取数条件见 [[authorized_person]]。

## 需求背景

该规则是办理链路的准入闸门之一，与 [[company_in_change_forbid_ca]]、[[non_build_success_no_ca]] 共同构成预检（pre4Step）的三大阻断条件。

## 版本演进

- v0：首次固化校验字段组合与错误码。

```ground:rule
name: CA 开通操作人必须是企业管理员
content: pre4Step 校验当前登录用户手机号命中 cust_person_info（user_type=admin、enable=Y、company_type=登录角色、ref_cust_company_info=企业 code），否则抛 CA_CERT_NOT_ADMIN
impact: 非管理员无法进入一证四步
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
evidence: "code_path:CaCertificationPreCheckApplication.java#assertCurrentUserIsAdmin"
```

关联页面：[[authorized_person]]、[[company_in_change_forbid_ca]]、[[non_build_success_no_ca]]。