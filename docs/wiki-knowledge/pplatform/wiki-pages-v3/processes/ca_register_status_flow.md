---
type: process
title: 企业 CA 开通状态机
page_key: ca_register_status_flow
domain: CA证书认证
status: draft
aliases: [ca_register_status]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaActivationApplication.java", "code:CaCertificationPreCheckApplication.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [cust_company_info.ca_register_status]
---

作用于 [[cust_company_info]] 的 `ca_register_status`（字典 [[open_status]]）。注册成功回写 Y；一证四步预检发现证书失效或中台企业名不一致时回写 N。

`CaOpenCaApplication.isOpenCa` 在 `caEval.isInvalid()` 时**仅内存**视为未开通，不落库。

```ground:process
name: 企业 CA 注册状态
field: cust_company_info.ca_register_status
states:
  - value: N
    label: 未开通
    source: code_enum
  - value: P
    label: 开通中
    source: code_enum
  - value: Y
    label: 已开通
    source: code_enum
transitions:
  - from: N
    event: openCa / cbsCompanyRegister 注册成功
    to: Y
    evidence: "code_path:CaActivationApplication.java:activateByOpCompanyId"
  - from: P
    event: 注册成功回写
    to: Y
    evidence: "code_path:CaCertificationConfirmApplication.java:confirm"
  - from: Y
    event: pre4Step 预检证书失效或企业名不一致
    to: N
    evidence: "code_path:CaCertificationPreCheckApplication.java:resetCaRegisterStatusToN"
```
