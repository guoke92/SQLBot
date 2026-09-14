---
type: caliber
title: 变更类签署仅限企业自行变更且变更项命中
page_key: change-scope-self-alter-items
domain: 授权协议与电子授权
status: draft
aliases:
  - CHANGE 分支准入
  - 变更项白名单
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_change_record
  - db:cust_change_cfg
contract_version: "0.1"
belong: calibers
---

`processType=CHANGE` 分支要求变更方式为企业自行变更（`alter_mode='SELF_ALTER'`），且 `alter_type_id` 反查 [[tables/cust_change_cfg|item_code]] 命中 `UN0016`/`UN0012`/`UN0013`/`UN0008`/`UN0015` 之一。平台代变更（`PLAT_ALTER`）与未命中的变更项不触发签署，见 [[calibers/offline-electronic-auth-trigger]]。

## 需求背景
只有企业自行发起的、且涉及授权要件的变更项才需要重新出具电子授权书；平台代变更与不涉及授权的变更项重复签署无业务意义。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 变更类签署仅限企业自行变更且变更项命中
predicate: "cust_change_record.alter_mode = 'SELF_ALTER' AND cust_change_cfg.item_code ∈ {'UN0016','UN0012','UN0013','UN0008','UN0015'}"
scope: "processType=CHANGE 分支"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#isAllowedChangeScenario"
```