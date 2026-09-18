---
type: concept
title: 变更认证方式
page_key: change_identify_style
belong: concepts
domain: cust
status: draft
aliases: [切换认证方式, 认证失败改方式, 企业认证升级]
maps_to: cust_company_info.identify_style
field_targets: [cust_company_info.identify_style]
sources: ['code_path:CustCompanyOperationApplication.java:119', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [simple_auth, self_auth]
adjudication: boundary
---

# 变更认证方式

document_claim:变更认证方式.md#18：自主注册认证失败且无法删除时，运营把 identify_style 改成简易/接口/保持现状。
document_claim:企业认证升级.md#15：简易升级为邀请，仍是改 identify_style，不是改 cust_build_type。
现网 CustCompanyOperationApplication.changeIdentifyStyle 只 update 该列。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__identify_style]]
- [[concepts/self_auth]]
- [[concepts/simple_auth]]
