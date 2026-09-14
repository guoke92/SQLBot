---
type: caliber
title: 开放渠道来源口径（免意愿校验）
page_key: channel_openapi_source
domain: CA证书认证
status: draft
aliases: [CHANNEL_OPENAPI, 开放渠道来源]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

圈定开放渠道 OpenAPI 落库的 CA 认证行，并标记它与门户来源在**校验强度**上的差异：assertCompleteForSubmit 对本来源跳过 intent_sms_json / intent_h_face_json 的必填校验。这意味着渠道侧自行保证意愿，库里可能缺席意愿留痕列，做完整性看板时不能把"意愿列为空"一律判为脏数据。

## 需求背景

上送完整性的其余要求（协议告知 JSON 必填、实名 JSON 至少一项、file_refs_json 非空）对本来源仍然生效，见 [[submit_completeness_check]]。

## 版本演进

- v0：首次固化谓词、豁免范围与分布值。

```ground:caliber
name: 开放渠道来源口径（免意愿校验）
predicate: "ca_certification_info.data_source = 'CHANNEL_OPENAPI'"
scope: assertCompleteForSubmit 对本来源跳过 intent_sms_json/intent_h_face_json 必填校验
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#assertCompleteForSubmit + db_dist:CHANNEL_OPENAPI=49"
```

关联页面：[[ca_certification_info]]、[[submit_completeness]]、[[submit_completeness_check]]、[[fbp_portal_source]]。