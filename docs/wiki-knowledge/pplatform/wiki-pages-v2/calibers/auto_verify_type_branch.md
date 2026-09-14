---
type: caliber
title: "自动核查类型分支"
page_key: auto_verify_type_branch
domain: "customer-onboarding"
status: draft
aliases:
  - "checkType=INFO 分支"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:autoVerify"
contract_version: "0.1"
belong: calibers
---

本口径决定自动核查走哪条实现：命中 `CustAutoCheckTypeEnum.INFO` 走信息核查，否则走影像核查。它解释了统计「自动核查通过率」时为何必须按 `checkType` 分类，否则两类核查口径会被混算。相关状态机见 [[processes/certification_verify_machine]]，术语见 [[concepts/auto_verify]]。

## 需求背景

需求文档把「自动审核」作为单一环节描述，但代码中存在两条核查实现，取数与耗时特征不同；对账与统计时需要按本口径拆分。

## 版本演进

- 当前为二分支结构（INFO / 非 INFO）；若后续新增核查类型，本口径的 `else` 分支会静默吞掉新类型，需要同步维护。

```ground:caliber
name: "自动核查类型分支"
predicate: "FlowAutoMediaVerifyReqDTO.checkType = 'INFO'"
scope: "AutoVerifyController.autoVerify：命中 CustAutoCheckTypeEnum.INFO 走 autoVerifyService.autoVerify(appNo)，否则走 autoMediaVerify(appNo)"
evidence: "code_path:AutoVerifyController.java:autoVerify"
```

相关：[[processes/certification_verify_machine]]、[[tables/cust_certification_info]]、[[concepts/auto_verify]]。