---
type: rule
title: 企业状态同步口径规则
page_key: company_status_sync
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业冻结/注销联动
  - custStatusSync/userStatusSync
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustCompanyInfoApplication.java:custStatusSync
  - code:CustCompanyInfoApplication.java:userStatusSync
contract_version: "0.1"
belong: rules
---

企业状态变更映射到平台侧状态，并联动该企业下逐联系人（用户）状态同步。

## 需求背景

映射关系：FREEZE→`CustStatusEnum.FREEZE`、UNFREEZE→`EFFECT`、DISABLE→`WRITEOFF`；企业状态经 `clientCustStatusSyncService.call`，随后对每个联系人调用 `clientUserStatusSyncService.call`。这与建档状态机 [[cust_build_status]] 的审核通过与拒绝迁移是两条不同的状态维度，前者是经营状态、后者是建档进度，切勿混用。

## 版本演进

- 企业级与用户级两次调用为串行结构，意味着用户同步失败会直接影响该企业的整体同步结果。

```ground:rule
name: 企业状态同步口径
content: FREEZE→CustStatusEnum.FREEZE；UNFREEZE→EFFECT；DISABLE→WRITEOFF，同时 clientCustStatusSyncService.call 与逐联系人 clientUserStatusSyncService.call
impact: 企业状态变更联动用户冻结/解冻
field_targets: []
evidence: "code:CustCompanyInfoApplication.java:custStatusSync/userStatusSync"
```