---
type: caliber
title: 线下电子授权书签署触发条件
page_key: offline-electronic-auth-trigger
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子签署触发条件
  - 签署编排准入门槛
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
  - db:tenant_setting_config
contract_version: "0.1"
belong: calibers
---

这是签署编排的准入门槛：审核通过（`check_status='CUST_CHECK_PASS'`）、企业用户授权模式为线下（`auth_model='off_auth'`）、租户开关开启（[[tables/tenant_setting_config|generate_electronic_auth_flag]]='Y'）、且企业已具备 CFCA 电子签章能力（`need_register_ca='Y'` 且 `ca_register_status='Y'`）时必须全满足。企业类型与流程类型还分别有额外口径：[[calibers/allowed-company-types]]、[[calibers/build-scope-identify-styles]]、[[calibers/change-scope-self-alter-items]]。

聚合后的完整规则见 [[rules/electronic-auth-sign-preconditions]]；不满足时仅记日志跳过，不阻断主流程。

## 需求背景
电子授权书签署属于「可选的增强路径」，必须能安全地在前置条件不满足时静默跳过；同时 CA 未开通的企业需等待重开 CA 成功后链式触发签署，因此判定被设计为可重复求值的条件集合而非一次性开关。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 线下电子授权书签署触发条件
predicate: "cust_company_info.check_status = 'CUST_CHECK_PASS' AND <企业用户>.auth_model = 'off_auth' AND tenant_setting_config.generate_electronic_auth_flag = 'Y' AND cust_company_info.need_register_ca = 'Y' AND cust_company_info.ca_register_status = 'Y'"
scope: "审核回调 afterCommit 编排；不满足仅记日志跳过，不阻断主流程"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#evaluateIneligibilityReason"
```