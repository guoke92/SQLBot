---
type: rule
title: 简易认证禁止开通电子签章
page_key: simple_auth_forbid_ca
domain: CA证书认证
status: draft
aliases: [enforceMustNotOpenCa, 简易认证不开通 CA]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyCaPolicy.java
  - db:cust_company_info
contract_version: "0.1"
belong: rules
---

简易认证提交时若 need_register_ca='Y'，调用 CustCompanyCaPolicy.enforceMustNotOpenCa 校正并落库 need_register_ca / ca_register_status / need_register_bs / bs_register_status。

**影响**：简易认证企业强制不开通 CA。这条规则解释了为什么存在 need_register_ca='Y' 但 ca_register_status 长期为 N 的企业，也是 [[legacy_package_companies|存量打包企业口径]] 明确排除 identify_style='SIMPLE' 的原因（两份口径互相印证）。

## 需求背景

校正同时覆盖 CFCA 与 BS 两个渠道字段，说明"简易认证不得开通电子签章"是渠道无关的策略，边界参见 [[ca_certificate]]。

## 版本演进

- v0：首次沉淀该策略字段范围（evidence 与 field_targets 在语义分析输入中被截断，本页据 content 中列出的列名推导，待下一版补全逐字证据）。

```ground:rule
name: 简易认证禁止开通电子签章
content: 简易认证提交时若 need_register_ca='Y'，调用 CustCompanyCaPolicy.enforceMustNotOpenCa 校正并落库 need_register_ca/ca_register_status/need_register_bs/bs_register_status
impact: 简易认证企业强制不开通 CA
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_bs
  - cust_company_info.bs_register_status
evidence: "code_path:CustCompanyCaPolicy.java#enforceMustNotOpenCa"
```

关联页面：[[cust_company_info]]、[[legacy_package_companies]]、[[need_register_ca_judgement]]、[[ca_certificate]]。