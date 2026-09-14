---
type: caliber
title: 企业生效
page_key: company_effect
domain: 客户中心
status: draft
aliases:
  - listEffectCompany
  - 生效企业
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
contract_version: "0.1"
belong: calibers
---

企业生效口径用于筛选已认证成功、业务状态生效且数据有效的企业。关联 [[cust_company_info]]、状态机 [[company_build_status]] 与术语 [[build]]。

```ground:caliber
name: 企业生效
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1'
scope: listEffectCompany / listEffectCompanyByTenantAndType
evidence: code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。