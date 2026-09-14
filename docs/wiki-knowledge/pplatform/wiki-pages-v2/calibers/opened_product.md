---
type: caliber
title: 已开通产品
page_key: opened_product
domain: 经办人/联系人/管理员管理
status: draft
aliases: [OPENED, open_status, 产品开通口径]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyUserRelApplication.java#processSingleCompany", "code:CustCompanyQueryApplication.java#queryOpenedProductsByCompanies"]
contract_version: "0.1"
belong: calibers
---

"已开通产品"口径 = cust_auth_application.open_status='OPENED'，用于关联重建前置校验与产品开通状态展示（展示侧另含 OPENING）。它是"联系人已开通产品"的真实查询口径，[[cust_person_info]] 的 auth_application 字段不是（[[cust_auth_application]]、[[sys_cust_user_rel]]）。

## 需求背景
- 重建要求企业至少存在一个 OPENED 产品，否则不写入关联关系（[[rel_rebuild_precondition]]）。

## 版本演进
- 当前版本展示侧口径包含 OPENED 与 OPENING 两种状态，重建侧只认 OPENED。

```ground:caliber
name: 已开通产品
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: 关联重建、产品开通状态展示（另含 OPENING）
evidence: "code:CustCompanyUserRelApplication.java#processSingleCompany + CustCompanyQueryApplication.java#queryOpenedProductsByCompanies"
```

相关页面：[[cust_auth_application]]、[[sys_cust_user_rel]]、[[rel_rebuild_precondition]]。