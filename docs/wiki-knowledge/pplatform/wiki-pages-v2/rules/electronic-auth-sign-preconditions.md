---
type: rule
title: 电子授权书签署编排前置条件（全满足才签署）
page_key: rule.electronic_auth_sign_preconditions
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署准入规则
  - evaluateIneligibilityReason
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

该规则把分散的准入口径聚合为一次求值：审核通过、线下授权模式、租户开关开启、企业类型在白名单、流程类型命中（建档的邀请/自主录入，或企业自行变更且变更项命中）、且 CFCA 已开通。任一不满足仅记日志跳过，不阻断 `CustSyncEventProcessor` 主流程；CA 未开通时等待重开 CA 成功后链式触发。

引用的口径页：[[calibers/offline-electronic-auth-trigger]]、[[calibers/allowed-company-types]]、[[calibers/build-scope-identify-styles]]、[[calibers/change-scope-self-alter-items]]；幂等与并发见 [[rules/sign-idempotency-and-lock]]。

## 需求背景
电子签署是增强路径，必须在任何前置条件缺失时安全跳过，并允许在 CA 开通等异步条件补齐后重新求值，因此被设计为「条件集合 + 不阻断主流程」的规则。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的规则；本次分析未提供 document_claim（未证实主张）。

```ground:rule
name: 电子授权书签署编排前置条件（全满足才签署）
content: "checkStatus=CUST_CHECK_PASS；企业用户 authModel=off_auth；租户 generate_electronic_auth_flag=Y；企业类型 ∈{SUPPLIER,CORE,FINANCE,PROJECT_COMPANY}；流程为建档（identifyStyle ∈{INVITE,SELF}）或企业自行变更（alterMode=SELF_ALTER 且变更项命中 UN0016/UN0012/UN0013/UN0008/UN0015）；need_register_ca=Y 且 ca_register_status=Y。任一不满足仅记日志跳过。"
impact: "不阻断 CustSyncEventProcessor 主流程；CA 未开通时等待重开 CA 成功后链式触发"
field_targets:
  - cust_company_info.check_status
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.identify_style
  - cust_change_record.alter_mode
  - cust_change_cfg.item_code
  - tenant_setting_config.generate_electronic_auth_flag
evidence: "code_path:CustAuthSignOrchestrationApplication.java#evaluateIneligibilityReason"
```