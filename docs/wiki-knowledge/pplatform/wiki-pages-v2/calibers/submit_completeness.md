---
type: caliber
title: 一证四步上送完整性口径
page_key: submit_completeness
domain: CA证书认证
status: draft
aliases: [上送完整性, assertCompleteForSubmit 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

判定一行 CA 认证数据是否"材料齐备、可以上送签章中台"：notify_agreement_json 非空，且（enterprise_four_json 或 police_two_json 至少一项），且（intent_sms_json 或 intent_h_face_json 至少一项，CHANNEL_OPENAPI 来源除外），且 file_refs_json 非空。缺项即阻断上送。

## 需求背景

本口径的三处"至少一项"设计，对应真实业务上的可选路径：企业实名四要素/三要素共用 [[enterprise_four_elements|enterprise_four_json]]，意愿可走短信或 H5 刷脸，被授权人核验落 [[ca_certification_info]] 的 police_two_json。开放渠道豁免意愿校验的边界见 [[channel_openapi_source]]。执行侧规则见 [[submit_completeness_check]]。

## 版本演进

- v0：首次固化四项必要条件与一项豁免。

```ground:caliber
name: 一证四步上送完整性口径
predicate: "ca_certification_info.notify_agreement_json != null"
scope: 且（enterprise_four_json 或 police_two_json 至少一项）且（intent_sms_json 或 intent_h_face_json 至少一项，CHANNEL_OPENAPI 除外）且 file_refs_json 非空
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#assertCompleteForSubmit"
```

关联页面：[[ca_certification_info]]、[[submit_completeness_check]]、[[channel_openapi_source]]、[[notify_agreement]]、[[enterprise_four_elements]]、[[ca_upgrade_auth]]。