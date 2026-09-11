---
type: caliber
title: 企业建档成功口径
page_key: calibers/company-build-success
domain: 企业集团关系
status: draft
aliases: [建档成功, BUILD_SUCCESS]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java:checkCustGroup
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
contract_version: "0.1"
---

企业建档成功指企业主数据已完成认证建档，判定条件为 `cust_company_info.cust_build_status = 'BUILD_SUCCESS'`，是发送集团待办、CA 开通、集团类操作的前置条件。

## 需求背景

未建档完成的企业不具备签署与业务承接能力，若提前发送待办或允许操作会产生无效流程与脏状态，因此把建档成功作为一系列动作的统一闸门，见 [[rules/notice-only-build-success]] 与 [[rules/effective-member-no-op]]。

## 版本演进

v0 契约按现状固化。该口径同时被协议签署侧（CustGroupLicenseApplication.checkCustGroup）与关系新增/导入侧（CustGroupRelApplication）引用，是跨模块共享口径。

## 口径锚点

```ground:caliber
name: 企业建档成功
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
scope: 发送集团待办、CA 开通、集团操作的前置条件
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup / CustGroupRelApplication.java:addExistSubCustGroupRel
```