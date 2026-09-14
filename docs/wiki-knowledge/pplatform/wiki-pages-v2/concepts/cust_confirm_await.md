---
type: concept
title: 待客户认证
page_key: cust_confirm_await
domain: 企业建档与认证
status: draft
aliases:
  - CUST_CONFIRM_AWAIT
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:submitCust
  - code_path:CustCompanyOperationApplication.java:reAuthentication
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
field_targets:
  - cust_company_info.cust_build_status
  - cust_build_status.CUST_CONFIRM_AWAIT
  - cust_build_status.AWAIT_CUST_CONFIRM
adjudication: boundary
also_confused_with:
  - cust_build_status.AWAIT_CUST_CONFIRM
belong: concepts
field_targets: [cust_company_info.cust_build_status]
sources: ["enrich:wiki-admin"]
---

"待客户认证"指流程已发起但球在企业一侧：邀请认证的客户录入提交、自主认证的重提交、内管发起建档都会落到该状态，等待客户向运营中台提交后才进入审核中。它是 [[calibers/reauthentication_allowed]] 的唯一准入态。

## 边界与歧义

与 `AWAIT_CUST_CONFIRM` 的边界：两值字面近似但语义不同——`CUST_CONFIRM_AWAIT` 是邀请/自主认证的"待客户确认"；`AWAIT_CUST_CONFIRM` 由简易认证提交写入（`submitForSimpleAuth`），走的是另一条无需运营中台审批的链路，见 [[processes/cust_build_status_state_machine]]。

## 需求背景

需求文档中"待提交"态在本字段落地为该值；"已驳回→待提交（修改后重新提交）"即从 `BUILD_FAIL` 回到本状态。

## 版本演进

v0 初稿：取值以 DB 分布为准。两值是否应合并或改名，待产品与研发确认。

关联：[[concepts/cust_building]]、[[rules/self_invite_need_audit]]、[[calibers/reauthentication_allowed]]。

相关：[[cust_company_info]]
