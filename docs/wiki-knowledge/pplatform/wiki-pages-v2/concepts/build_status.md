---
type: concept
title: 建档状态
page_key: build_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [cust_build_status, custBuildStatus]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.cust_build_status", "db:cust_company_info.cust_build_status", "code:CustCompanyUserRelApplication.java#processSingleCompany"]
contract_version: "0.1"
maps_to: cust_person_info.cust_build_status
field_targets:
  - cust_person_info.cust_build_status
  - cust_company_info.cust_build_status
adjudication: boundary
also_confused_with:
  - cust_company_info.cust_build_status
boundary: "同名同码值，企业表与联系人表各存一份；重建 sys_cust_user_rel 时判定用企业侧，联系人侧仅表示该联系人自身建档进度。"
belong: concepts
field_targets: [cust_person_info.cust_build_status]
---

"建档状态"在 [[cust_company_info]] 与 [[cust_person_info]] 中各存一份，码值相同但语义主体不同：企业侧决定企业能否进入审核/重建流程，联系人侧表示该联系人自身建档进度（[[cust_build_status]]、[[rel_rebuild_company]]）。

## 需求背景
- 重建 sys_cust_user_rel 的判定取企业侧值，取错一侧会导致关联关系不写入或误写入（[[rel_rebuild_precondition]]）。
- AMS 来源的新增经办人不写建档成功，避免与运营中台流程冲突（[[ams_source_not_build_success]]）。

## 版本演进
- 当前版本联系人侧建档状态仅供展示与自身进度判断，未参与重建判定。

相关页面：[[cust_company_info]]、[[cust_person_info]]、[[cust_build_status]]、[[rel_rebuild_company]]。