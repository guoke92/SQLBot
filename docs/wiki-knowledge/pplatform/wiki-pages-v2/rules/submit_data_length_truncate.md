---
type: rule
title: 上送 data 字段长度裁剪
page_key: submit_data_length_truncate
domain: CA证书认证
status: draft
aliases: [truncateOversizedDataFieldsInSubmitPayload, 1000 字符裁剪]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: rules
---

上送前对 authPersonPoliceTwo / authEnterpriseThree / authEnterpriseFour / checkCode / h5Face 的 data 做 1000 字符限制，超长按 JSON 叶子节点从长到短剔除，失败则硬截断。

**影响**：避免签章中台因 data 超长拒收；代价是库内留痕与实际上送内容可能不一致——排查"中台收到的东西和库里不一样"时应先想到本规则。

## 需求背景

被裁剪的字段分别对应 [[enterprise_four_elements]]（authEnterpriseFour/authEnterpriseThree）与意愿留痕（h5Face/checkCode），上送原始报文另存于 sign_platform_result，可用于比对裁剪前后差异。

## 版本演进

- v0：首次固化 1000 字符阈值与"先剔叶、后硬截断"的降级顺序。

```ground:rule
name: 上送 data 字段长度裁剪
content: 上送前对 authPersonPoliceTwo/authEnterpriseThree/authEnterpriseFour/checkCode/h5Face 的 data 做 1000 字符限制，超长按 JSON 叶子节点从长到短剔除，失败则硬截断
impact: 避免签章中台因 data 超长拒收
field_targets:
  - ca_certification_info.police_two_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#truncateOversizedDataFieldsInSubmitPayload"
```

关联页面：[[ca_certification_info]]、[[enterprise_four_elements]]、[[submit_completeness_check]]。