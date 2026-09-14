---
type: concept
title: 企业业务编码桥（code ↔ ref_cust_company_info）
page_key: company_business_code
domain: 数据权限与组织
status: draft
aliases: [企业业务编码, ref_cust_company_info, cust_company_info.code]
oid: 1
scope:
  databases: [base]
sources: [code, "enrich:wiki-admin"]
contract_version: "0.1"
maps_to:
  - cust_company_info.code
  - cust_person_info.ref_cust_company_info
  - cust_role_info.ref_cust_company_info
field_targets:
  - table: cust_company_info
    field: code
    meaning: 企业业务编码（对外引用键，子表以 ref_cust_company_info 指向它，而非 id）
    evidence: code
  - table: cust_role_info
    field: ref_cust_company_info
    meaning: 关联企业业务编码
    evidence: code
  - table: cust_company_info
    field: certification_no
    meaning: 统一社会信用代码（同租户内企业唯一键之一）
    evidence: code
adjudication: 企业侧对外引用一律走 cust_company_info.code（业务编码）；certification_no 是同租户内唯一键之一但不是关系外键，ref_cust_company_info 指向的是 code 而非 id。
also_confused_with: [cust_company_info.id, certification_no]
belong: concepts
---

术语桥：企业业务编码 code 是 [[tables/cust_company_info]] 对外暴露的引用键，引用方式在子表中名为 ref_cust_company_info（[[tables/cust_person_info]]、[[tables/cust_role_info]] 都有该字段）。最容易踩的坑是误用主键 id 关联，语义分析已明确「子表以 ref_cust_company_info 指向它，而非 id」。

另一个易混字段是 certification_no（统一社会信用代码）：它是同租户内的企业唯一键之一，但承担的是去重/识别职责，不是关系外键。

相关：[[cust_company_info]]
