---
type: rule
title: 简易认证不支持开通CA
page_key: simple-auth-no-ca
belong: rules
domain: 企业建档与准入
status: published
aliases: [简易认证CA限制]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.ca_register_status, cust_company_info.need_register_ca]
scope:
  databases: [lowcode_pplatform]
---

# 简易认证不支持开通CA

本规则规定简易认证提交时，若 `need_register_ca='Y'` 则强制改为 `'N'` 并落库，避免简易认证走 CA 开通流程。

## 需求背景

简易认证是低门槛认证方式，不应触发 CA 开通。该规则在代码提交入口强制执行，保障流程简化。

## 版本演进

证据来自代码路径 `CustCompanyInfoApplication.submitForSimpleAuth`。

```ground:rule
name: 简易认证不支持开通CA
content: 简易认证提交时，若 need_register_ca='Y' 则强制改为 'N' 并落库
impact: 避免简易认证走CA开通流程
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
evidence: "code_path:CustCompanyInfoApplication.submitForSimpleAuth"
```

相关表：[[cust_company_info]]