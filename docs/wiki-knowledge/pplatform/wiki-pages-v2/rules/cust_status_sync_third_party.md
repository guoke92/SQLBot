---
type: rule
title: 状态同步第三方
page_key: cust_status_sync_third_party
domain: 企业建档与认证
status: draft
aliases:
  - 客户状态同步
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:custStatusSync
contract_version: "0.1"
belong: rules
---

企业生命周期状态变更（冻结→`FREEZE`、解冻→`EFFECT`、注销→`WRITEOFF`）通过 `clientCustStatusSyncService` 同步到业务系统；用户状态的同步则直接透传 `operateType`。

```ground:rule
name: 状态同步第三方
content: 客户状态变更(冻结→FREEZE、解冻→EFFECT、注销→WRITEOFF)通过 clientCustStatusSyncService 同步业务系统；用户状态同步 operateType 直传
impact: 跨系统状态一致性
field_targets:
  - cust_company_info.cust_status
evidence: code_path:CustCompanyInfoApplication.java:custStatusSync
```

## 需求背景

冻结与注销会影响下游系统的业务资格，因此状态迁移必须同步出去；同步点与 [[processes/cust_status_state_machine]] 的迁移同源，见 [[concepts/freeze]]、[[concepts/writeoff]]。

## 版本演进

v0 初稿：规则以 `custStatusSync` 的调用路径固化。同步失败的重试/补偿策略未在给定证据中体现。

关联：[[processes/cust_status_state_machine]]、[[concepts/writeoff]]。