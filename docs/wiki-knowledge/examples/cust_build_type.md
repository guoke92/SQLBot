---
type: enum
title: 建档录入方式
page_key: cust_build_type
domain: 企业建档
status: published
aliases: [平台录入, PC端录入, 网关录入]
anchors: [cust_company_info.cust_build_type]
field_targets: [cust_company_info.cust_build_type]
sources: ["enums.yaml", "CustCompanyInfo.java"]
created: 2026-08-28
updated: 2026-08-29
related: [cust_company_info, identify-style]
contract_version: "0.1"
---

# 建档录入方式（cust_build_type）

企业建档的**录入渠道**。与[[identify-style|认证方式]]严格区分：本字段回答
"企业档案由哪个渠道创建"，认证方式回答"企业通过何种方式完成认证"——
两者筛出的企业集合差异显著，筛选口径不可混用。

常见问法："平台录入的企业"、"PC端建档"、"网关自动建档"均指本字段。

```ground:enum
enum: cust_build_type
fields: [cust_company_info.cust_build_type]
values:
  PC_BUILD: { label: 客户录入, note: 客户端PC端录入（源码 CustBuildTypeConstant） }
  AGW_BUILD: { label: 平台录入, note: 平台/网关渠道录入（源码 CustBuildTypeConstant） }
ambiguous: false
```

## 关联

- [[identify-style]]（易混淆，必须对照）
- [[平台录入]]（术语桥页）
- [[cust_company_info]]
