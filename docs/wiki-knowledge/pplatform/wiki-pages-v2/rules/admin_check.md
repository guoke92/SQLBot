---
type: rule
title: 管理员校验规则
page_key: rule/admin_check
domain: CA证书认证
status: draft
aliases: [assertCurrentUserIsAdmin, CA_CERT_NOT_ADMIN]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationPreCheckApplication.java:assertCurrentUserIsAdmin"]
contract_version: "0.1"
---

规则要求：当前登录用户必须是企业管理员，需同时满足 cust_person_info.user_type=admin、enable=Y、ref_cust_company_info=当前企业 code、company_type=当前登录企业类型、phone=当前登录手机号。任一不满足即抛出 CA_CERT_NOT_ADMIN 异常，无法开通 CA。

五个条件构成一次「人-企业-手机号」三重一致性确认：既校验操作者角色，也校验其归属企业与企业类型，并用手机号与登录态对齐，避免借用他人账号代开证书。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。五项条件、比对方向与异常码均来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。该规则与变更态拦截同属前置检查阶段（[[rules/block_ca_on_change_status]]）。

```ground:rule
name: 管理员校验规则
content: 当前登录用户必须是企业管理员：cust_person_info.user_type=admin且enable=Y且ref_cust_company_info=当前企业code且company_type=当前登录企业类型且phone=当前登录手机号。
impact: 非管理员抛出CA_CERT_NOT_ADMIN异常，无法开通CA
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.ref_cust_company_info
  - cust_person_info.company_type
  - cust_person_info.phone
evidence: "code_path:CaCertificationPreCheckApplication.java:assertCurrentUserIsAdmin"
```

相关页面：[[rules/block_ca_on_change_status]]、[[concepts/ca]]。