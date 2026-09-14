---
type: rule
title: CFCA 未开通时的延迟补偿签署
page_key: ca_delayed_compensation_sign
domain: 授权协议与电子授权
status: draft
aliases:
  - CA 回调补偿签署
  - 延迟补签规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: rules
---

解决“审核通过时 CA 还没开好”的时序问题：审核通过时若 [[cfca_registered]] 不成立则本轮跳过；待 CA 重开成功回调（`CaActivateResult.activateSuccess=true`）后再链式触发一次签署，此时即便本地状态仍非 Y 也继续尝试，由签章层做二次校验。与 [[offline_eauth_sign_trigger]] 配合，保证不永久漏签。

```ground:rule
name: CFCA 未开通时的延迟补偿签署
content: "审核通过时若本地 ca_register_status≠Y 则跳过签署；待 CA 重开成功回调（CaActivateResult.activateSuccess=true）后再链式触发一次签署，此时即使本地状态仍非 Y 也继续尝试（由签章层二次校验）"
impact: "保证 CA 开通后授权书能补签，避免永久漏签"
field_targets:
  - cust_company_info.ca_register_status
evidence: "code:CustAuthSignOrchestrationApplication.java:tryOfflineElectronicAuthSignAfterCaSuccess"
```