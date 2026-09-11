---
type: concept
title: "建档状态"
page_key: "concepts/build_status"
domain: "customer-onboarding"
status: draft
aliases:
  - "认证状态"
  - "cust_build_status"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
contract_version: "0.1"
maps_to: "CustBuildStatusEnum"
field_targets:
  - "cust_company_info.cust_build_status"
adjudication: "boundary"
also_confused_with:
  - "客户状态 cust_status(CustStatusEnum)"
  - "审核状态 check_status(CheckStatus)"
boundary: "cust_build_status 描述认证/建档进度；cust_status 描述企业生效/变更/注销生命周期；check_status 描述单次工作流审核结论。三者取值域互不相同。"
---

「建档状态」（亦称认证状态）描述企业在准入流程中的进度：初始、待客户确认、审核中、成功、失败、变更中。取值域由 `CustBuildStatusEnum` 定义，流转见 [[processes/company_build_status_machine]]。

## 边界

`boundary`：`cust_build_status` 描述认证/建档进度；`cust_status` 描述企业生效/变更/注销生命周期；`check_status` 描述单次工作流审核结论。三者取值域互不相同。

因此「企业已生效」这类判断必须同时看建档状态与客户状态，口径见 [[calibers/effect_company]]；单次审核结论见 [[concepts/check_status]]。

## 需求背景

需求文档中的「企业状态」实指本字段，其「已通过」对应 `BUILD_SUCCESS`，与工作流审核的 `CUST_CHECK_PASS` 不等价（后者经流转后才会导致前者），详见 [[concepts/check_status]]。

## 版本演进

- 建档状态的写入证据目前主要来自旧处理器 `CustStatusCommitProcessor`，该类已废弃，见 [[rules/legacy_status_processor_deprecated]]；新链路下应回归验证。