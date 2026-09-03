---
type: enum
title: 认证方式
page_key: identify_style
domain: 企业建档
status: published
aliases: [认证方式, 平台邀请认证, 邀请认证, 网关邀请认证]
anchors: [cust_company_info.identify_style]
field_targets: [cust_company_info.identify_style]
sources: ["enums.yaml", "CustCompanyInfo.java"]
created: 2026-08-28
updated: 2026-08-29
related: [cust_company_info, cust-build-type]
contract_version: "0.1"
---

# 认证方式（identify_style）

企业完成身份**认证的渠道方式**。与[[cust-build-type|建档录入方式]]严格区分：
本字段回答"企业如何完成认证"，不回答"企业档案由哪个渠道创建"。
用户问"认证方式"且语境同时出现"录入/建档"时，应先澄清指向哪个字段。

```ground:enum
enum: identify_style
fields: [cust_company_info.identify_style]
values:
  INVITE: { label: 平台邀请认证 }
  INVITE_AGW: { label: 网关邀请认证 }
  SELF: { label: 自主认证 }
ambiguous: false
```

## 关联

- [[cust-build-type]]（易混淆，必须对照）
- [[cust_company_info]]
