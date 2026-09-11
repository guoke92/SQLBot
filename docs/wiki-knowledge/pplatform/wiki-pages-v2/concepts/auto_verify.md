---
type: concept
title: "自动审核"
page_key: "concepts/auto_verify"
domain: "customer-onboarding"
status: draft
aliases:
  - "自动化核查"
  - "自动核查"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:autoVerify"
  - "code_path:AutoVerifyController.java:saveManual"
  - "code_path:FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
maps_to: "AutoVerifyService.autoVerify(信息核查)/autoMediaVerify(影像核查)，以及 cust_certification_info.auto_verify_status"
field_targets:
  - "cust_certification_info.auto_verify_status"
adjudication: "boundary"
also_confused_with:
  - "CustWorkflowAuditCommitProcessor 的工作流审核通过/拒绝"
  - "cust_company_info.check_status=CUST_CHECK_PASS"
boundary: "『自动核查』是准入审核前的资料/身份核查环节（OCR、人脸、影像），产出 auto_verify_status；『审核通过』是运营中台工作流/自动审核后的准入结论，产出 check_status=CUST_CHECK_PASS 与 cust_build_status=BUILD_SUCCESS。二者是前后置关系，不是同一值。"
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实) 本页版本演进包含需求文档主张，尚未在代码中得到证实。

「自动审核」在业务口语中常被当作准入结论，但在代码里它对应的是准入前置的核查环节：对 OCR、人脸、影像等资料做自动化核查，结果写入 [[tables/cust_certification_info]] 的 `auto_verify_status`。它**不是** [[concepts/check_status]]，也不等于 [[concepts/admission]]。

## 边界

`boundary`：『自动核查』是准入审核前的资料/身份核查环节（OCR、人脸、影像），产出 `auto_verify_status`；『审核通过』是运营中台工作流/自动审核后的准入结论，产出 `check_status=CUST_CHECK_PASS` 与 `cust_build_status=BUILD_SUCCESS`。二者是前后置关系，不是同一值。

相关状态机见 [[processes/certification_verify_machine]]，分支口径见 [[calibers/auto_verify_type_branch]]；与之相对的人工环节见 [[concepts/manual_verify]]。

## 需求背景

需求文档把自动审核描述为准入的自动通过条件；代码中可见的只是核查触发与核查结果落库，准入结论仍由工作流链路写入 [[tables/cust_company_info]]。

## 版本演进

- (document_claim，未证实) 需求文档称「企业准入流程中『自动审核通过』后自动通过准入并更新企业状态为已通过」。代码证据：`code_path:AutoVerifyController.java:autoVerify`——仅触发 `autoVerify`/`autoMediaVerify`，未见于本链路写 `cust_status`/`cust_build_status` 为已通过。该主张**未证实**。
- (document_claim，未证实) 需求文档称「自动审核规则：企业征信评分>=60、法人无不良信用记录、经营状态正常、行业不在黑名单」。代码证据：未在提供的 service/mapper 链路中出现征信评分/黑名单判定实现。该主张**未证实**，且不应写入任何统计口径。
- 自动核查的类型分支（信息核查 / 影像核查）已落地，见 [[calibers/auto_verify_type_branch]]。

相关：[[cust_certification_info]]
