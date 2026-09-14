---
type: concept
title: 企业类型/企业角色
page_key: company_type
domain: 外部渠道与银行对接
status: draft
aliases:
  - companyType
  - custCompanyType
  - CompanyType
  - SPY
  - CE
  - CPT
  - OPE
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCompanyType
  - code:TianmaService.companyArchive
contract_version: "0.1"
maps_to: cust_company_info.cust_company_type
also_confused_with:
  - cust_person_info.company_type
  - cust_role_info.role_type
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.cust_company_type]
sources: ["enrich:wiki-admin"]
---

企业类型承担对外协议码与内部字典值的双向往返，是渠道建档中取值最容易混淆的维度。

## 需求背景
对外协议码（SPY/CE/CPT/OPE）与内部 dictKey（SUPPLIER/CORE/FINANCE/PLATFORM_OPERATOR_COMPANY）需经 getCompanyType 转换；天马请求 companyType 为空时按默认供应商处理（[[tianma_default_supplier]]）。主表以 JSON 数组存储，查询侧只能 like 模糊匹配（[[company_certification_tenant_match]]），因此不可用等值条件过滤角色。

## 版本演进
暂无版本演进记录。

相关：[[cust_company_info]]
