---
type: concept
title: 总公司行标识（head_company_data）
page_key: head_company_data
domain: CA证书认证
status: draft
aliases: [headCompanyData=Y, 总公司行标识]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationHeadCompanySupport.java
  - code:CaCertificationConfirmApplication.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.head_company_data
field_targets:
  - ca_certification_info.head_company_data
  - ca_certification_info.cust_id
adjudication: boundary
also_confused_with:
  - ca_certification_info.cust_id
belong: concepts
field_targets: [ca_certification_info.head_company_data]
---

head_company_data 标记一行认证数据的主体归属：Y=总公司主体行（来源 head_company_info），N=本企业/分公司自身行，用字面量 'Y'/'N' 写入。

**边界（boundary）**：Y 行 cust_id 是总公司 id（cust_head_company_info.id），不是分公司 cust_company_info.id；N/Y 两行靠 cust_id+data_date+batch_no+head_company_data 共同定位。因此"cust_id 相同"绝不能作为合并两行的依据，反过来也不能因为 cust_id 不同就认为不是同一笔业务。

## 需求背景

口径见 [[head_company_row|总公司主体行口径]]；协议确认阶段只有 N 行会被上送（[[confirm_submit_own_row_only]]），而运营推送链路会并行上送两行（[[operation_platform_source]]）。

## 版本演进

- v0：首次固化字面量写入方式与 cust_id 语义差异。

关联页面：[[ca_certification_info]]、[[head_company_row]]、[[confirm_submit_own_row_only]]、[[incremental_idempotent_key]]。