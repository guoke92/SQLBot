---
type: process
title: CA 上送状态机
page_key: ca_submit_status_flow
domain: CA证书认证
status: draft
aliases: [上送签章中台]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaCertificationInfoAppServiceImpl.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [ca_certification_info.submit_status]
---

作用于 [[ca_certification_info]] 的 `submit_status`（字典 [[ca_submit_status]]）。SUCCESS 后再调用 `submitToSignCenter` 会幂等短路，不重复上送。

```ground:process
name: CA 签章中台上送状态
field: ca_certification_info.submit_status
states:
  - value: PENDING
    label: 创建后未提交、或正在采集各 JSON 列
    source: code_enum
  - value: SUCCESS
    label: cbsSubmitBizData 成功并已回写
    source: code_enum
  - value: FAIL
    label: cbsSubmitBizData 失败 / 超时 / 业务校验未通过
    source: code_enum
transitions:
  - from: PENDING
    event: cbsSubmitBizData 成功 writeSubmitResult
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
  - from: PENDING
    event: cbsSubmitBizData 失败或 markFailed
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:writeSubmitResult"
```
