---
type: concept
title: 企业实名四要素
page_key: enterprise_four_elements
domain: CA证书认证
status: draft
aliases: [ENTERPRISE_FOUR, 企业三要素 ENTERPRISE_THREE, 企业实名核验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.enterprise_four_json
field_targets:
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.police_two_json
belong: concepts
field_targets: [ca_certification_info.enterprise_four_json]
---

企业实名四要素（ENTERPRISE_FOUR）指企业侧的名称/证件等要素核验，其请求与响应留痕落在 enterprise_four_json。

**边界（boundary）**：四要素与三要素（ENTERPRISE_THREE）在 updateRealNameByMethod 中同样落到 enterprise_four_json（靠 verifyMethod 区分），个人侧公安二要素（POLICE_TWO）落 police_two_json。因此"一列一方法"的直觉是错的：看到 enterprise_four_json 有值不代表走的是四要素核验，需回看 verifyMethod。

## 需求背景

上送时两类实名 JSON 满足"至少一项"即可通过 [[submit_completeness|一证四步上送完整性口径]]；两者都会被 [[submit_data_length_truncate]] 的 1000 字符限制裁剪。

## 版本演进

- v0：首次记录四要素与三要素共列（靠 verifyMethod 区分）这一事实。

关联页面：[[ca_certification_info]]、[[submit_completeness]]、[[submit_data_length_truncate]]、[[authorized_person]]。