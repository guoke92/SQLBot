---
type: concept
title: 统一社会信用代码
page_key: social_unified_code
domain: 外部渠道与银行对接
status: draft
aliases:
  - socialUnifiedCode
  - certificationNo
  - certification_no
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.query
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_company_info.certification_no
also_confused_with:
  - cust_company_info.invoicing_taxpayer_no
adjudication: synonym
belong: concepts
field_targets: [cust_company_info.certification_no]
sources: ["enrich:wiki-admin"]
---

对外协议中的 socialUnifiedCode 与落库列 certification_no 为同一概念，是企业查重与定位的主匹配键。

## 需求背景
渠道建档/查询/变更均以该字段定位企业，结合租户构成三元匹配（[[company_certification_tenant_match]]）；与开票纳税人识别号 invoicing_taxpayer_no 不可混用。

## 版本演进
暂无版本演进记录。

相关：[[cust_company_info]]
