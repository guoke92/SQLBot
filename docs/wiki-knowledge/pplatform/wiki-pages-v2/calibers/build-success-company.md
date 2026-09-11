---
type: caliber
title: 建档成功企业
page_key: calibers/build-success-company
domain: 平台事件监听与同步
status: draft
aliases:
  - BUILD_SUCCESS 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
---

建档成功企业口径：`cust_company_info.cust_build_status = 'BUILD_SUCCESS'` 的企业，在存量判定中直接跳过推送/变更。

## 需求背景
存量企业已经完成过推送与审核，事件回调到达时无需再次推送；用建档终态做幂等短路，可避免重复同步与重复回调。终态的写入路径见 [[processes/cust-company-build-status]] 的 `updateCustBuildStatus` 迁移。

## 版本演进
- v0 契约：口径取自代码层增量/存量判定逻辑，无 DB 实测。

```ground:caliber
name: 建档成功企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
scope: 存量企业直接跳过推送/变更判定
evidence: code
related_pages:
  - tables/cust_company_info
  - processes/cust-company-build-status
```