---
type: rule
title: "简易认证不支持开通电子签章"
page_key: simple_auth_no_ca_rule
belong: rules
domain: "授权协议与电子授权"
status: published
aliases: ["简易认证禁止电子签章", "简易认证无CA"]
oid: 1

sources: ["code:CustCompanyInfoApplication.submitForSimpleAuth", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.bs_register_status, cust_company_info.ca_register_status, cust_company_info.need_register_ca]
coverage_note: "简易认证流程"
scope:
  databases: [lowcode_pplatform]
---

该规则限制简易认证客户开通电子签章：提交简易认证时，若客户企业信息中请求开通电子签章，系统强制校正为关闭，并同步更新 CFCA/上上签开通状态。

## 需求背景

简易认证建档不再支持开通电子签章，这是业务上的明确限制。该规则防止简易认证路径意外开通签章能力，与 [[企业已开通电子签章口径]] 的判定前提相悖。

## 版本演进

暂无。

```ground:rule
name: 简易认证不支持开通电子签章
content: "简易认证提交时，若 cust_company_info.need_register_ca='Y'，则强制校正为 'N'，同时更新 ca_register_status/bs_register_status 字段，落库保存"
impact: "限制简易认证客户开通电子签章"
field_targets:
  - "cust_company_info.need_register_ca"
  - "cust_company_info.ca_register_status"
  - "cust_company_info.bs_register_status"
evidence: "code_path:CustCompanyInfoApplication.submitForSimpleAuth + reqdoc:简易认证建档不再支持开通电子签章"
```

相关：[[cust_company_info]]
