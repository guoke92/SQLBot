---
type: caliber
title: CA开通阻断
page_key: ca_open_block
domain: 客户中心
status: draft
aliases:
  - isOpenCa 阻断
  - 建档变更中阻断
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:isOpenCa
contract_version: "0.1"
belong: calibers
---

CA开通阻断口径用于在 isOpenCa 判断时，若企业处于建档变更流程则返回处理中提示、阻断开通。关联 [[cust_company_info]]、术语 [[e_signature]] 与状态机 [[company_build_status]]。

```ground:caliber
name: CA开通阻断
predicate: cust_company_info.cust_build_status = 'CUST_CHANGE'
scope: isOpenCa 返回变更流程处理中阻断提示
evidence: code_path:CustCompanyIfoEnchanceService.java:isOpenCa
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。