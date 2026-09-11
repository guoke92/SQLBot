---
type: concept
title: "准入"
page_key: "concepts/admission"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业准入"
  - "建档"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
  - "code_path:CustAuthValidatorProcessor.java:validate"
contract_version: "0.1"
maps_to: "企业建档/认证全流程（cust_build_status 从 INIT 到 BUILD_SUCCESS）"
field_targets:
  - "cust_company_info.cust_build_status"
adjudication: "boundary"
also_confused_with:
  - "产品开通 cust_auth_application.open_status"
boundary: "准入/建档指企业与联系人资格认证；产品开通（OPENING/OPENED/NOT_OPENED）指企业开通具体产品，属于建档成功后的独立流程。"
---

「准入」（亦称建档）指企业与联系人资格从提交到认证通过的全流程，终点是 [[tables/cust_company_info]] 的 `cust_build_status = BUILD_SUCCESS`；查询层面的有效性判定见 [[calibers/effect_company]]。

## 边界

`boundary`：准入/建档指企业与联系人资格认证；产品开通（OPENING/OPENED/NOT_OPENED）指企业开通具体产品，属于建档成功后的独立流程。

因此「准入通过」不能等同于「产品已开通」，也不等于单次审核结论 [[concepts/check_status]]。

## 需求背景

需求文档要求准入须经审核，驳回后可修改重提；本概念是这一要求的对象集合，流程见 [[processes/company_build_status_machine]]。

## 版本演进

- 准入链路的核查前置环节（自动/人工核查）与准入结论已明确解耦，见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]]。
- 需求文档中关于自动审核直接通过准入、征信评分规则的表述，在本链路中未获证实，见 [[concepts/auto_verify]]。