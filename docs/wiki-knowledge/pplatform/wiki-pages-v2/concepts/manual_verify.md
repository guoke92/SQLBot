---
type: concept
title: "人工审核"
page_key: "concepts/manual_verify"
domain: "customer-onboarding"
status: draft
aliases:
  - "人工核查"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:saveManual"
  - "code_path:FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
maps_to: "AutoVerifyController.saveManual + cust_certification_info.manual_verify_status=MANUAL_AUTHENTICATION_PASSED"
field_targets:
  - "cust_certification_info.manual_verify_status"
adjudication: "boundary"
also_confused_with:
  - "运营中台工作流审批人审核"
boundary: "人工核查作用于单条认证影像/实名的核查结论；运营中台工作流审核作用于企业建档/变更流程结论，前者不改变 cust_build_status。"
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实) 本页版本演进包含需求文档主张，尚未在代码中得到证实。

「人工核查」指由人工对单条认证影像或实名结果给出核查结论，写入 [[tables/cust_certification_info]] 的 `manual_verify_status`。它与运营中台的**工作流审批人**是两类角色：前者不改变 [[tables/cust_company_info]] 的 `cust_build_status`，后者才是准入/变更结论的来源，见 [[processes/workflow_check_status_machine]]。

## 边界

`boundary`：人工核查作用于单条认证影像/实名的核查结论；运营中台工作流审核作用于企业建档/变更流程结论，前者不改变 `cust_build_status`。

自动通道见 [[concepts/auto_verify]]；核查状态机见 [[processes/certification_verify_machine]]。

## 需求背景

需求文档把人工审核描述为准入流程中的一个队列环节；代码中可见的只有人工结论提交入口，准入结论仍由工作流链路驱动。

## 版本演进

- (document_claim，未证实) 需求文档称「需人工审核时进入人工审核队列，由审核人员审核」。代码证据：`code_path:AutoVerifyController.java:saveManual`——有人工审核提交接口，但未见队列数据结构与消费逻辑。该主张**未证实**。
- 人工核查结论的枚举取值与自动核查共用同一枚举族，见 [[processes/certification_verify_machine]]。

相关：[[cust_certification_info]]
