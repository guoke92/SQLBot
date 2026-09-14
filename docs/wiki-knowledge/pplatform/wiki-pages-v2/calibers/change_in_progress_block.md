---
type: caliber
title: 变更在途阻断
page_key: change_in_progress_block
domain: 客户中心
status: draft
aliases:
  - ADMIN_CHANGE 阻断
  - 变更中阻断
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:adminChangeSaveOrUpdate
contract_version: "0.1"
belong: calibers
---

变更在途阻断口径用于在发起新变更前判断企业是否正处变更流程，避免并发变更。关联 [[cust_company_info]]、[[change_in_progress_block]] 与状态机 [[company_build_status]]（CUST_CHANGE 态）。

```ground:caliber
name: 变更在途阻断
predicate: cust_company_info.cust_status = 'CHANGE'
scope: adminChangeSaveOrUpdate 发起新变更前阻断
evidence: code_path:CustPersonApplication.java:adminChangeSaveOrUpdate
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。