---
type: caliber
title: 在途流程
page_key: in-transit-process
belong: calibers
domain: 企业建档与准入
status: published
aliases: [在途申请, 未完成流程]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.data_type]
scope:
  databases: [lowcode_pplatform]
---

# 在途流程

本口径识别存在未完成的申请/记录数据的企业，判定 `data_type = '0'` 且 `cust_build_status` 非终态（BUILD_SUCCESS、BUILD_FAIL）。用于变更流程互斥判断，防止并发变更。

## 需求背景

在途流程是 [[change-process-mutex]] 规则的基础口径。代码 `ApplyCompanyInfoApplication.judgeHaveApplyingRecord` 查询 `data_type=CustDataTypeConstant.DATA_TYPE_APPLY` 且非终态。

## 版本演进

口径证据来自代码 `ApplyCompanyInfoApplication.judgeHaveApplyingRecord`。

```ground:caliber
name: 在途流程
predicate: "cust_company_info.data_type = '0' AND cust_build_status NOT IN ('BUILD_SUCCESS','BUILD_FAIL')"
scope: 存在未完成的申请/记录数据
evidence: "code:ApplyCompanyInfoApplication.judgeHaveApplyingRecord 查询 data_type=CustDataTypeConstant.DATA_TYPE_APPLY 且非终态"
```

相关表：[[cust_company_info]]；相关规则：[[change-process-mutex]]