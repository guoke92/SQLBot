---
type: concept
title: 审批中/审核中
page_key: cust_building
domain: 企业建档与认证
status: draft
aliases:
  - CUST_BUILDING
  - BUILDING
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:messageNotify
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
field_targets:
  - cust_company_info.cust_build_status
  - cust_build_status.CUST_BUILDING
  - cust_build_status.BUILDING
adjudication: boundary
also_confused_with:
  - cust_build_status.BUILDING
belong: concepts
field_targets: [cust_company_info.cust_build_status]
sources: ["enrich:wiki-admin"]
---

"审核中/审批中"指流程已提交运营中台、等待审批的状态，是认证成功前的最后一个中间态：客户提交后由 `CUST_CONFIRM_AWAIT` 进入，运营中台退回则回退，通过则进入 [[concepts/build_success]]。

## 边界与歧义

与 `BUILDING` 的边界：`CUST_BUILDING` 是提交运营中台后的真实审核态（DB 2909 条）；`BUILDING` 在枚举中意为"建档中"，DB 仅 2 条，主流程基本不使用。两者不可等同。

## 需求背景

需求文档中的"审核中"对应本概念；变更流程中的企业也可能以 `cust_build_status = 'CUST_CHANGE'` 等方式并行表达，需与 [[concepts/cust_confirm_await]] 区分。

## 版本演进

v0 初稿：以 DB 分布为准确认主用值；`BUILDING` 的存量数据归属待清理确认。

关联：[[processes/cust_build_status_state_machine]]、[[calibers/judge_have_applying_record]]。

相关：[[cust_company_info]]
