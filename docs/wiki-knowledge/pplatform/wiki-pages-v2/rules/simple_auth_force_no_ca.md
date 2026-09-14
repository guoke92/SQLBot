---
type: rule
title: 简易认证强制不开通CA
page_key: simple_auth_force_no_ca
domain: CA证书认证
status: draft
aliases: [submitForSimpleAuth 校正规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CustCompanyInfoApplication.java:submitForSimpleAuth"]
contract_version: "0.1"
belong: rules
---

规则要求：简易认证提交时，若 cust_company_info.need_register_ca=Y，强制校正为 N 并落库，同时校正 ca_register_status、need_register_bs、bs_register_status。影响是简易建档不支持开通电子签章。

这是一条「上游强制收敛」规则：调用方即使传入了开通意图，也会在落库时被改写，因此简易企业不会进入一证四步（[[concepts/one_cert_four_steps]]），也不会产生 [[tables/ca_certification_info]] 的认证行。它同时校正 BS 侧的注册标识，说明 CA 与 BS 的开通开关在简易场景下被一并关闭。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。校正字段清单与强制方向来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。本规则与存量打包口径中的 identify_style != 'SIMPLE' 条件互相印证（[[calibers/legacy_package_company_scope]]）。

```ground:rule
name: 简易认证强制不开通CA
content: 简易认证提交时，若need_register_ca=Y，强制校正为N并落库，同时校正ca_register_status、need_register_bs、bs_register_status。
impact: 简易建档不支持开通电子签章
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_bs
  - cust_company_info.bs_register_status
evidence: "code_path:CustCompanyInfoApplication.java:submitForSimpleAuth"
```

相关页面：[[calibers/legacy_package_company_scope]]、[[rules/ca_invalidate_writeback]]、[[concepts/one_cert_four_steps]]。