---
type: caliber
title: "变更记录回查等待"
page_key: "calibers/change_record_polling"
domain: "customer-onboarding"
status: draft
aliases:
  - "变更记录轮询口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:getChangeRecord"
contract_version: "0.1"
---

回调到达时变更记录可能尚未落库，因此按运营中台客户 id 回查，并限定轮询次数与间隔，超时即按未取到处理。该口径决定了「回调成功但记录未更新」这一现象的边界条件。相关表见 [[tables/cust_change_record]]，状态机见 [[processes/change_record_check_machine]]。

## 需求背景

需求文档要求变更审核结果可靠回传，回查等待是为处理中台与本域写入时序差而设的工程约束。

## 版本演进

- 当前为固定次数+固定间隔的同步轮询；轮询上限一旦变化，「回调丢失」类问题的排查结论会随之改变。

```ground:caliber
name: "变更记录回查等待"
predicate: "cust_change_record.oper_cust_id = 运营中台客户id"
scope: "getChangeRecord 最多轮询15次、每次间隔1s"
evidence: "code_path:CustStatusCommitProcessor.java:getChangeRecord"
```

相关：[[tables/cust_change_record]]、[[processes/change_record_check_machine]]、[[calibers/callback_msg_idempotent]]。