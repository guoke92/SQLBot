---
type: rule
title: CA认证行创建幂等规则
page_key: ca_row_idempotent
domain: CA证书认证
status: draft
aliases: [createOrGetByKey 规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"]
contract_version: "0.1"
belong: rules
---

规则要求：以（custId, dataDate, headCompanyData, submitStatus=PENDING）为幂等键创建 [[tables/ca_certification_info]] 行，已存在 PENDING 行则复用，否则新建，并生成唯一 batchNo。影响是避免同一企业同一天同一总公司标记下重复创建 CA 认证行。

复用的边界只在 PENDING 态：一旦行进入 SUCCESS 或 FAIL，新的提交会落到另一行（状态语义见 [[processes/ca_certification_submit_status]]）。batchNo 的格式约束为 INC_yyyyMMddHHmmssSSS_6位hex，是这条规则的可观测产出。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。幂等键、复用条件与 batchNo 生成均由代码路径证据支撑；对应的查询口径见 [[calibers/ca_row_idempotent_key]]。

## 版本演进

暂无文档化的版本演进证据。

```ground:rule
name: CA认证行创建幂等规则
content: 以(custId, dataDate, headCompanyData, submitStatus=PENDING)为幂等键，已存在PENDING则复用，否则新建，并生成唯一batchNo。
impact: 避免同一企业同一天同一总公司标记下重复创建CA认证行
field_targets:
  - ca_certification_info.cust_id
  - ca_certification_info.data_date
  - ca_certification_info.head_company_data
  - ca_certification_info.submit_status
  - ca_certification_info.batch_no
evidence: "code_path:CaCertificationInfoAppServiceImpl.java:createOrGetByKey"
```

相关页面：[[calibers/ca_row_idempotent_key]]、[[concepts/head_company_data]]、[[rules/branch_dual_row]]。