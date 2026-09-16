---
type: rule
title: 开放渠道上送免意愿校验
page_key: openapi_skip_intent
domain: CA证书认证
status: draft
aliases: [CHANNEL_OPENAPI 免意愿]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaCertificationInfoAppServiceImpl.java:assertCompleteForSubmit"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - ca_certification_info.data_source
  - ca_certification_info.intent_sms_json
---

`data_source='CHANNEL_OPENAPI'` 时，`assertCompleteForSubmit` 跳过 `intent_sms_json` / `intent_h_face_json` 必填。门户与运营中台来源仍要意愿留痕。

```ground:rule
name: 开放渠道上送免意愿校验
content: CHANNEL_OPENAPI 来源提交签章中台时不校验短信/刷脸意愿 JSON。
impact: 按来源统计「缺意愿仍上送」的行时，开放渠道不应算缺失。
field_targets: [ca_certification_info.data_source]
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:assertCompleteForSubmit"
```
