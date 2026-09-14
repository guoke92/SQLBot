---
type: process
title: CA 签章中台上送状态（ca_certification_info.submit_status）
page_key: ca_submit_status
domain: CA证书认证
status: draft
aliases: [submit_status, 上送状态, 签章中台上送状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - code:CaCertificationIntentSmsApplication.java
  - db:ca_certification_info
contract_version: "0.1"
belong: processes
---

这是本系统到签章中台「一次上送」的状态位，落库为枚举 .name()：PENDING / SUCCESS / FAIL。它只描述一次上送动作的结果，不代表证书生命周期——证书侧的状态是另一套外部态，见 [[sign_center_cert_status]] 与 [[cert_status]]。

状态机有三个关键性质：第一，PENDING 同时是 [[incremental_idempotent_key|增量落库幂等键]] 的一部分，因此"还在 PENDING"的行会被复用而不是新建行；第二，SUCCESS 是终态，再次调用 submitToSignCenter 会短路返回成功（见 [[submit_idempotent_short_circuit]]），协议确认页因此可重复点击；第三，SUCCESS 之后即使再发生意愿落库动作，状态也不回退。

## 需求背景

状态迁移由 writeSubmitResult 统一写入：中台返回 DBaaS code in {0,200} 且业务体 biz.status=SAVED 记为 SUCCESS，其余异常或非 SAVED 记为 FAIL。FAIL 行可被 markFailed 再次置失败（补偿/人工），但不回到 PENDING。AMS 复用数据时按 [[submit_success|上送完成口径]] 取最新一条 SUCCESS 行重新组装上报。

## 版本演进

- v0：首次固化为三态。历史数据中 op_type 的 UPDATE 分支未使用、batch_no 退出幂等键，均与上送状态复用行逻辑（见 [[incremental_idempotent_row]]）相关。

```ground:process
name: CA 签章中台上送状态
field: ca_certification_info.submit_status
states:
  - value: PENDING
    label: 待上送
    source: code_enum
  - value: SUCCESS
    label: 上送成功
    source: code_enum
  - value: FAIL
    label: 上送失败
    source: code_enum
transitions:
  - from: PENDING
    event: "cbsSubmitBizData 返回 DBaaS code in {0,200} 且 biz.status=SAVED"
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter/writeSubmitResult"
  - from: PENDING
    event: "cbsSubmitBizData 抛异常或业务体非 SAVED"
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter/writeSubmitResult"
  - from: PENDING
    event: "markFailed 人工/补偿置失败"
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#markFailed"
  - from: SUCCESS
    event: "再次 submitToSignCenter（幂等短路，不重复上送）"
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter（CA_CERT_SUBMIT_ALREADY_SUCCESS）"
  - from: SUCCESS
    event: "短信意愿再次落库（拒绝）"
    to: SUCCESS
    evidence: "code_path:CaCertificationIntentSmsApplication.java#persistIntentSmsAfterVerify"
```

关联页面：[[ca_certification_info]]、[[submit_success]]、[[incremental_idempotent_key]]、[[submit_idempotent_short_circuit]]、[[submit_completeness_check]]、[[cert_status]]。