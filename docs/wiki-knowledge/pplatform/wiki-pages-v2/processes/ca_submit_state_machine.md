---
type: process
title: CA 一证四步上送状态机
page_key: process/ca_submit_state_machine
domain: 微信生态/小程序/扫脸
status: draft
aliases: [上送状态机, submit_status 状态机]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 一证四步上送状态机

描述 [[ca_certification_info]] 上送签章中台的状态流转：落库初始 PENDING，成功后 SUCCESS，失败 FAIL；SUCCESS 行具备幂等短路的保护语义。

## 需求背景

上送涉及外部中台，需要可重试且可人工干预。通过 PENDING 初始态 + SUCCESS 幂等短路 + markFailed 人工补录，保证重复调用不产生歧义、已成功结果不被覆盖。

## 版本演进

v0.1 记录三种状态与六条迁移路径。

```ground:process
state_machine: CA 一证四步上送状态机
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
  - from: "(新建)"
    event: createOrGetByKey 建行
    to: PENDING
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey
  - from: PENDING
    event: submitToSignCenter 中台返回 DBaaS code∈{0,200} 且 biz.status=SAVED
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
  - from: PENDING
    event: submitToSignCenter 抛异常 / DBaaS code 不成功 / biz.status≠SAVED
    to: FAIL
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
  - from: FAIL
    event: markFailed 人工补录强制置失败
    to: FAIL
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#markFailed
  - from: SUCCESS
    event: submitToSignCenter 重复调用（幂等短路）
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
  - from: SUCCESS
    event: markFailed（被拒绝，抛 CA_CERT_SUBMIT_ALREADY_SUCCESS）
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#markFailed
```

相关：[[ca_certification_info]]、[[ca_idempotent_row]]、[[latest_success_submit]]、[[h5_face_persist_soft_fail]]。