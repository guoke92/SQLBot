---
type: concept
title: 一证四步
page_key: concept/one_cert_four_steps
domain: CA证书认证
status: draft
aliases: [CFCA一证四步]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: 企业四要素/三要素核验 + 公安二要素核验 + 意愿认证（短信/H5刷脸） + 协议签署与上送签章中台
adjudication: synonym
also_confused_with: [实名认证]
field_targets:
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
  - ca_certification_info.notify_agreement_json
---

「一证四步」是 CFCA CA 开通的完整流程，四个步骤在 [[tables/ca_certification_info]] 上各有留痕字段：企业四要素/三要素核验（enterprise_four_json，verifyMethod=ENTERPRISE_FOUR 或 ENTERPRISE_THREE）、公安二要素核验（police_two_json，verifyMethod=POLICE_TWO）、意愿认证（intent_sms_json，authType=SMS_CODE；intent_h_face_json，authType=H5_FACE）、协议签署与上送签章中台（notify_agreement_json 留痕协议签署，file_refs_json 提供附件引用）。

## 边界与辨析

「一证四步」与「实名认证」是包含关系而非同义关系：实名认证仅指其中的核验环节（企业要素核验与公安二要素核验），不覆盖意愿认证、协议签署与上送。因此当需求文档提到「完成实名认证」时，不能直接推定为「完成一证四步」。

上送签章中台是否要求意愿认证留痕与数据来源有关：data_source=CHANNEL_OPENAPI 时可豁免意愿 JSON，见 [[rules/submit_sign_center_completeness]] 与 [[concepts/data_source]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。流程步骤与字段的对应关系来自代码中 verifyMethod 与 authType 的枚举取值。

## 版本演进

暂无文档化的版本演进证据。存量数据打包任务同样按一证四步口径筛选企业，见 [[calibers/legacy_package_company_scope]]。

相关页面：[[tables/ca_certification_info]]、[[rules/submit_sign_center_completeness]]、[[concepts/ca]]。