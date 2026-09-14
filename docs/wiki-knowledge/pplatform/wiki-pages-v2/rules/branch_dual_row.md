---
type: rule
title: 分公司双行处理规则
page_key: branch_dual_row
domain: CA证书认证
status: draft
aliases: [persistActivateData 双行规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaActivationApplication.java:persistActivateData"]
contract_version: "0.1"
belong: rules
---

规则要求：分公司场景下，CaActivationApplication 会创建两行 [[tables/ca_certification_info]]——headCompanyData=N（本企业）与 headCompanyData=Y（总公司），并分别提交签章中台；openCa 注册时自动双笔注册。影响是支持分公司代总公司完成 CA 认证。

双行意味着同一 cust_id、同一 data_date 下可以并存两条认证行，因此行标识 head_company_data 必须进入幂等键，否则两行会互相覆盖（[[calibers/ca_row_idempotent_key]]、[[rules/ca_row_idempotent]]）。两行各自独立走提交状态机（[[processes/ca_certification_submit_status]]），状态可能不一致，下游按企业取「最新成功上报数据」时需要明确是取哪一行（[[calibers/latest_success_report]]）。术语层面 headCompanyData 与 headCompany 的分工见 [[concepts/head_company_data]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。双行创建与分别上送的行为来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。

```ground:rule
name: 分公司双行处理规则
content: 分公司场景下，CaActivationApplication 会创建两行ca_certification_info：headCompanyData=N（本企业）和headCompanyData=Y（总公司），并分别提交签章中台；openCa注册时自动双笔注册。
impact: 支持分公司代总公司完成CA认证
field_targets:
  - ca_certification_info.head_company_data
  - ca_certification_info.cust_id
evidence: "code_path:CaActivationApplication.java:persistActivateData"
```

相关页面：[[calibers/ca_row_idempotent_key]]、[[rules/ca_row_idempotent]]、[[concepts/head_company_data]]、[[processes/ca_certification_submit_status]]。