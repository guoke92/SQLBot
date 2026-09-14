---
type: rule
title: 提交签章中台完整性校验
page_key: submit_sign_center_completeness
domain: CA证书认证
status: draft
aliases: [assertCompleteForSubmit 规则, CA_CERT_INFO_INCOMPLETE]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:assertCompleteForSubmit"]
contract_version: "0.1"
belong: rules
---

规则要求：上送签章中台前，[[tables/ca_certification_info]] 行必须满足——notify_agreement_json 非空；至少一项实名 JSON（enterprise_four_json 或 police_two_json）；至少一项意愿 JSON（intent_sms_json 或 intent_h_face_json），除非 data_source=CHANNEL_OPENAPI；file_refs_json 非空。不满足时抛出 CA_CERT_INFO_INCOMPLETE 异常，阻止上送。

这是一条准入型规则，位于 [[processes/ca_certification_submit_status]] 的 PENDING 出口之前：校验不通过的行会保持 PENDING 或转入 FAIL，而不会进入 SUCCESS。意愿认证的豁免只针对渠道 API 来源，其余两个来源（FBP_PORTAL、OPERATION_PLATFORM）仍需意愿留痕，见 [[concepts/data_source]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。五项校验条件、豁免条件与异常码均来自代码路径证据；四类核验 JSON 的业务含义见 [[concepts/one_cert_four_steps]]。

## 版本演进

暂无文档化的版本演进证据。与该规则相邻的上送处理是 data 字段超长截断（[[rules/data_field_truncate]]）：前者决定「能不能送」，后者决定「报文能不能被接收」。

```ground:rule
name: 提交签章中台完整性校验
content: 上送签章中台前必须满足：notify_agreement_json非空；至少一项实名JSON（enterprise_four_json或police_two_json）；至少一项意愿JSON（intent_sms_json或intent_h_face_json），除非data_source=CHANNEL_OPENAPI；file_refs_json非空。
impact: 不满足则抛出CA_CERT_INFO_INCOMPLETE异常，阻止上送
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
  - ca_certification_info.file_refs_json
  - ca_certification_info.data_source
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:assertCompleteForSubmit"
```

相关页面：[[processes/ca_certification_submit_status]]、[[concepts/one_cert_four_steps]]、[[rules/data_field_truncate]]。