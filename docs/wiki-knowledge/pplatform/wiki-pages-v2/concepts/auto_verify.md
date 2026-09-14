---
type: concept
title: 自动审核
page_key: auto_verify
domain: 客户中心
status: draft
aliases:
  - 自动核查
  - autoVerify
  - autoMediaVerify
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:isFaceVerifyPassed
  - code_path:CustPersonApplication.java:getFaceVerifyQueryVideoDTO
contract_version: "0.1"
maps_to: cust_certification_info.auto_verify_status
also_confused_with:
  - cust_certification_info.manual_verify_status
  - cust_person_info.face_status
adjudication: boundary
belong: concepts
field_targets: [cust_certification_info.auto_verify_status]
---

「自动审核」在客户中心语境下指系统侧自动核查，别名包括自动核查、autoVerify、autoMediaVerify，落库到 [[cust_certification_info]] 的 auto_verify_status 与 auto_verify_data。它与人工核查（manual_verify_status）是并行结果列，也不同于联系人的人脸状态（cust_person_info.face_status）。流转见 [[certification_verify_result]]，判定口径见 [[face_verify_passed]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。