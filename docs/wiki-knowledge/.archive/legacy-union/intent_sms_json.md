---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: CA意愿认证方式
page_key: intent_sms_json
domain: certification
aliases:
- 意愿方式
- 短信意愿
- H5人脸意愿
anchors:
- intent_sms_json
---
# CA意愿认证方式

意愿认证按认证类型落不同 JSON 列；SMS_CODE 落 intent_sms_json，H5_FACE 落 intent_h_face_json。

```ground:enum
enum: intent_sms_json
fields:
- ca_certification_info.intent_sms_json
- ca_certification_info.intent_h_face_json
values:
  SMS_CODE:
    label: 短信验证码意愿
  H5_FACE:
    label: H5人脸意愿
```

## 关联
- [[ca_certification_info|ca_certification_info]]
