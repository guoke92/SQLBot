---
type: caliber
title: 可参与关联重建的企业
page_key: rel_rebuild_company
domain: 经办人/联系人/管理员管理
status: draft
aliases: [BUILD_SUCCESS, CUST_CHANGE, 重建企业口径]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyUserRelApplication.java#processSingleCompany"]
contract_version: "0.1"
belong: calibers
---

"可参与关联重建的企业"口径 = cust_company_info.cust_build_status='BUILD_SUCCESS'，用于 sys_cust_user_rel 重建（含 CUST_CHANGE 场景）。联系人侧同名字段不参与该判定（[[build_status]]、[[rel_rebuild_precondition]]）。

## 需求背景
- 重建的完整前置条件还包括企业 enable=Y、存在 OPENED 产品、管理员 user_id>0（[[sys_cust_user_rel]]、[[opened_product]]）。

## 版本演进
- 当前版本将 CUST_CHANGE 纳入可重建状态集合，服务企业变更场景。

```ground:caliber
name: 可参与关联重建的企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
scope: sys_cust_user_rel 重建（含 CUST_CHANGE）
evidence: "code:CustCompanyUserRelApplication.java#processSingleCompany"
```

相关页面：[[cust_company_info]]、[[sys_cust_user_rel]]、[[rel_rebuild_precondition]]、[[build_status]]。