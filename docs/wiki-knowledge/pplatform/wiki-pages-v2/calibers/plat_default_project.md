---
type: caliber
title: 运营方默认项目
page_key: plat_default_project
domain: 客户中心
status: draft
aliases:
  - setPlatClientCustProject
  - 运营方项目
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:ClientCustCommitValidatorSyncService.java:setPlatClientCustProject
contract_version: "0.1"
belong: calibers
---

运营方默认项目口径用于在同步建档时识别运营方企业，从而走默认项目逻辑。关联 [[cust_company_info]]。

```ground:caliber
name: 运营方默认项目
predicate: "cust_company_info.cust_company_type = '[\"PLATFORM_OPERATOR_COMPANY\"]'"
scope: setPlatClientCustProject 运营方走默认项目
evidence: code_path:ClientCustCommitValidatorSyncService.java:setPlatClientCustProject
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。