---
type: caliber
title: CA认证行幂等创建
page_key: caliber/ca_row_idempotent_key
domain: CA证书认证
status: draft
aliases: [createOrGetByKey 口径, CA认证行幂等键]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"]
contract_version: "0.1"
---

口径含义：创建或获取 CA 认证行时，以（cust_id, data_date, head_company_data, submit_status='PENDING'）作为幂等键；若已存在 PENDING 行则复用，否则新建一行。

该口径的作用域只在 PENDING 态有效——已进入 SUCCESS 或 FAIL 的行不参与复用（状态语义见 [[processes/ca_certification_submit_status]]），因此同一企业同一天可能既有历史 SUCCESS 行又有新的 PENDING 行。head_company_data 进入幂等键，是分公司双行场景能够成立的前提（[[rules/branch_dual_row]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。键的四个组成字段与复用/新建分支均来自代码路径证据；对应的业务规则见 [[rules/ca_row_idempotent]]，其中还包含 batch_no 的生成约定。

## 版本演进

暂无文档化的版本演进证据。

```ground:caliber
name: CA认证行幂等创建
predicate: "ca_certification_info.cust_id = ? 且 ca_certification_info.data_date = ? 且 ca_certification_info.head_company_data = ? 且 ca_certification_info.submit_status = 'PENDING'"
scope: 创建或获取CA认证行时，若存在PENDING行则复用，否则新建
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"
```

相关页面：[[tables/ca_certification_info]]、[[rules/ca_row_idempotent]]、[[concepts/head_company_data]]。