---
type: rule
title: data字段超长截断规则
page_key: rule/data_field_truncate
domain: CA证书认证
status: draft
aliases: [truncateOversizedDataFieldsInSubmitPayload 规则, data 超长截断]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:truncateOversizedDataFieldsInSubmitPayload"]
contract_version: "0.1"
---

规则要求：上送签章中台时，authRealNameJson 与 intentJson 下的 data 字段若超过 1000 字符，按叶子节点从长到短删除直至不超长；非 JSON 则硬截断。影响是避免签章中台因 data 超长拒绝，保证上送成功。

截断发生在报文打包阶段，作用于四类核验 JSON 所对应的 data 内容，属于「为了保证送达而牺牲部分字段完整度」的妥协：截断后的报文体不会被回写到 [[tables/ca_certification_info]] 的原始 JSON 字段中，原始留痕仍以列值为准；签章中台的请求与响应原文另存于 sign_platform_result。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。1000 字符阈值、叶子节点删除顺序与非 JSON 硬截断三个要点均来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。本规则是 [[rules/submit_sign_center_completeness]] 的补充：完整性校验保证字段存在，截断规则保证字段可被接收。

```ground:rule
name: data字段超长截断规则
content: 上送签章中台时，authRealNameJson和intentJson下的data字段若超过1000字符，按叶子节点从长到短删除直至不超长；非JSON则硬截断。
impact: 避免签章中台因data超长拒绝，保证上送成功
field_targets:
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:truncateOversizedDataFieldsInSubmitPayload"
```

相关页面：[[rules/submit_sign_center_completeness]]、[[tables/ca_certification_info]]、[[concepts/one_cert_four_steps]]。