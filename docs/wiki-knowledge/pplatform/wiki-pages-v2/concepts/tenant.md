---
type: concept
title: 租户
page_key: tenant
domain: 外部渠道与银行对接
status: draft
aliases:
  - dbTenantCode
  - db_tenant_code
  - appTenantCode
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:MetaDataThreadLocalConfig
contract_version: "0.1"
maps_to: cust_company_info.db_tenant_code
also_confused_with:
  - cust_company_info.app_tenant_code
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.db_tenant_code]
---

「租户」在本主题中指数据租户（dbTenantCode），决定落库归属；它与逻辑租户 appTenantCode 不是同一概念。

## 需求背景
入站渠道建档先置 ThreadLocal 为 `all` 做跨租户检索（[[inbound_all_tenant_context]]），随后必须用渠道秘钥反查真实租户再落库，否则数据会落到错误租户；该反查依据见 [[cust_access_secret]]，落库字段见 [[cust_company_info]]。

## 版本演进
暂无版本演进记录。