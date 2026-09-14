---
type: caliber
title: 客户主表启用过滤
page_key: company_enable_filter
domain: 外部渠道与银行对接
status: draft
aliases:
  - 企业启用口径
  - cust_company_info.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.query
  - code:CustAccessApplication.batchQuery
  - code:CustAccessApplication.changeCompanyInfo
contract_version: "0.1"
belong: calibers
---

企业查询/变更/批量查询统一附加启用过滤，保证停用企业不会被渠道侧检索或变更。

## 需求背景
对渠道而言「查不到」与「查不到但存在停用件」的语义不同，统一过滤避免了渠道侧对无效企业发起变更；变更链路中该过滤与 [[company_certification_tenant_match]] 叠加使用。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 客户主表启用过滤
predicate: "cust_company_info.enable = 'Y'"
scope: 企业查询/变更/批量查询均排除停用企业
evidence: "code:CustAccessApplication.query / batchQuery / changeCompanyInfo"
```