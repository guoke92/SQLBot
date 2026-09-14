---
type: rule
title: CA 上送完整性校验
page_key: ca_submit_completeness_check
domain: 微信生态/小程序/扫脸
status: draft
aliases: [上送完整性校验, 完整性校验]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: rules
---

# CA 上送完整性校验

submitToSignCenter 前的完整性校验规则：notify_agreement_json 非空；enterprise_four_json 或 police_two_json 至少一项非空；以及意愿认证相关约束（`data_source=CHANNEL_OPENAPI` 时豁免「至少一项意愿认证」，见 [[ca_certification_info]] 的 data_source）。

## 需求背景

签章中台要求报文具备协议告知与至少一类身份核验证据，否则拒绝受理。

## 版本演进

v0.1 记录校验前置条件；完整校验清单在语义分析中此处被截断，待补充。

```ground:rule
name: CA 上送完整性校验
content: "submitToSignCenter 前校验：notify_agreement_json 非空；enterprise_four_json 或 police_two_json 至少一项非空；intent…（原文在语义分析中截断，待补全）。"
impact: "保障中台报文具备协议告知与至少一类身份核验证据；CHANNEL_OPENAPI 数据源豁免意愿认证完整性校验。"
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.data_source
evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
```

相关：[[ca_certification_info]]、[[ca_submit_state_machine]]、[[submit_data_length_limit]]、[[ca_idempotent_row]]。