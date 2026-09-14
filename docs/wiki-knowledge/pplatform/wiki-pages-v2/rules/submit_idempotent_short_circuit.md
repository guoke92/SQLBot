---
type: rule
title: 上送幂等短路
page_key: submit_idempotent_short_circuit
domain: CA证书认证
status: draft
aliases: [CA_CERT_SUBMIT_ALREADY_SUCCESS, 重复上送短路]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: rules
---

submit_status=SUCCESS 的行再次 submitToSignCenter 直接返回成功，不重复调用 cbsSubmitBizData。

**影响**：协议确认页可重复点击，不会造成中台重复受理；同时也意味着材料在上送成功后再修改，不会自动重推，需要新建行（受 [[incremental_idempotent_row]] 约束）。

## 需求背景

本规则是 [[submit_success|上送完成口径]] 得以安全复用 SUCCESS 行的前提，也是 [[ca_submit_status]] 状态机中 SUCCESS 自指的迁移来源。

## 版本演进

- v0：首次固化短路行为与返回码语义（CA_CERT_SUBMIT_ALREADY_SUCCESS）。

```ground:rule
name: 上送幂等短路
content: submit_status=SUCCESS 的行再次 submitToSignCenter 直接返回成功，不重复调用 cbsSubmitBizData
impact: 协议确认页可重复点击
field_targets:
  - ca_certification_info.submit_status
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter"
```

关联页面：[[ca_submit_status]]、[[submit_success]]、[[incremental_idempotent_row]]。