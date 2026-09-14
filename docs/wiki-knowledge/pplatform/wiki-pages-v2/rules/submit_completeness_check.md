---
type: rule
title: 上送前完整性校验
page_key: submit_completeness_check
domain: CA证书认证
status: draft
aliases: [assertCompleteForSubmit, CA_CERT_INFO_INCOMPLETE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: rules
---

上送前校验：notify_agreement_json 必填、实名 JSON 至少一项、意愿 JSON 至少一项（CHANNEL_OPENAPI 免）、file_refs_json 必填。

**影响**：缺项时抛 CA_CERT_INFO_INCOMPLETE 阻断上送，行停留在 [[ca_submit_status|PENDING]] 状态并被后续请求复用。

## 需求背景

校验条件与 [[submit_completeness|一证四步上送完整性口径]] 一一对应；开放渠道豁免的边界见 [[channel_openapi_source]]。若前端提示此错误，通常应先查 [[notify_agreement]] 与 [[ca_upgrade_auth]] 的落位而不是重试。

## 版本演进

- v0：首次固化四项校验与一项豁免。

```ground:rule
name: 上送前完整性校验
content: notify_agreement_json 必填、实名 JSON 至少一项、意愿 JSON 至少一项（CHANNEL_OPENAPI 免）、file_refs_json 必填
impact: 缺项时抛 CA_CERT_INFO_INCOMPLETE 阻断上送
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
  - ca_certification_info.file_refs_json
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#assertCompleteForSubmit"
```

关联页面：[[submit_completeness]]、[[ca_certification_info]]、[[channel_openapi_source]]、[[ca_submit_status]]。