---
type: concept
title: 游客流程数据
page_key: visitor_flow_data
belong: concepts
domain: cust
status: draft
aliases: [游客处理, 流程数据]
maps_to: cust_company_info__data_type.0
field_targets: [cust_company_info__data_type.0, cust_company_info.data_type]
sources: ['code_path:CustDataTypeConstant.java:14', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [effective_company_term]
adjudication: boundary
---

# 游客流程数据

document_claim:游客处理.md#23：游客企业与正式表隔离。现网 data_type=0 是流程数据（常量注释），1 才是主数据有效企业。
不要用有效企业口径去数游客。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__data_type]]
- [[concepts/effective_company_term]]
