---
type: caliber
title: 简易认证在建档中判定
page_key: is_simple_building
domain: 企业建档与认证
status: draft
aliases:
  - 简易建档流程中
  - isSimpleBuilding
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyUtilApplication.java:isSimpleBuilding
contract_version: "0.1"
belong: calibers
---

判断企业是否正处在简易认证的建档过程中：必须认证方式为简易，且未落到变更态与认证成功态。两个排除条件实际上是"未走到终态"的近似表达。

```ground:caliber
name: 简易认证在建档中判定
predicate: cust_company_info.identify_style = 'SIMPLE' AND cust_company_info.cust_build_status != 'CUST_CHANGE' AND cust_company_info.cust_build_status != 'BUILD_SUCCESS'
scope: 简易建档流程中
evidence: code_path:CustCompanyUtilApplication.java:isSimpleBuilding
```

## 需求背景

简易认证与邀请/自主认证走不同链路（见 [[rules/simple_auth_no_ca]]、[[rules/finance_simple_direct_effect]]），下游需要据此区分企业是否还在简易建档中，从而决定是否允许触发相关动作。

## 版本演进

v0 初稿：口径固化自 `isSimpleBuilding`。用 `!=` 排除两个状态而非枚举在途状态，是否遗漏 `BUILD_FAIL` 等取值需复核。

关联：[[concepts/identify_style]]、[[processes/cust_build_status_state_machine]]。