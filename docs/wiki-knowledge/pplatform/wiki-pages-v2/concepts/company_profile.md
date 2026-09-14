---
type: concept
title: 企业画像 / Profile
page_key: company_profile
domain: 客户管理
status: draft
aliases: [profile-web, 性能测试接口]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code_path:ProfileController.java:getAppId
  - code_path:GptLearnService.java:checkPosterStatus
  - db:cust_company_info
contract_version: "0.1"
maps_to: cust_company_info.id
field_targets:
  - cust_company_info.id
adjudication: boundary
also_confused_with:
  - gpt_learn_poster_log.company_id
belong: concepts
field_targets: [cust_company_info.id]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实) 需求/系统文档层（客户管理平台业务规则文档、运营配置管理业务规则文档）通篇未出现 GP学习引流、问卷星活动、企业画像（Profile）的任何业务规则或流程表述，无法形成双源锚点。

主题名与实际实现不符：`ProfileController` 的 @Api 标注为「性能测试接口」，路径 `/profile-web/`，仅提供四个能力——取企业简要信息、按 `dbTenantCode` 取租户、分页用户、取 token。代码链路中不存在画像标签、画像表或画像计算实现。

## 需求背景

该主题下的接口是企业信息（[[tables/cust_company_info]]）的调试/测试入口，不应被当作「客户画像」能力引用；与之相邻的企业维度数据读取方还有 GP学习引流（按 `cust_company_info.cust_company_type` 与 `db_tenant_code` 过滤，见 [[rules/gpt_learn_finance_only]]、[[rules/poster_allowed_tenant]]）。

## 版本演进

- 当前观测：仅四个测试能力，无画像相关表与实现。
- 文档侧无对应业务规则表述（见页首 document_claim，未证实）。

相关：[[cust_company_info]]
