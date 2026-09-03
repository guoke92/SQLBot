---
type: process
title: 变更记录状态机
page_key: change_record_status
domain: 企业变更与运营变更
status: published
aliases: ["变更记录状态", "status"]
oid: 1

sources: ["db_dist", "CustSyncEventProvider.processCustEvent", "enrich:wiki-admin"]
contract_version: "0.1"
coverage_note: 变更记录
scope:
  databases: [lowcode_pplatform]
---

变更记录状态机定义 `cust_change_record.status` 的所有可能取值，是变更流程推进与完成的核心依据。状态包括初始、审核中、已通过、已驳回、退回客户等，其中存在非标准值 `returnCust-*` 被识别为脏数据。

## 需求背景

审核通过后变更记录状态变为已生效（`CUST_CHECK_PASS`），驳回变为已驳回（`CUST_CHECK_REJECT`）。该状态变化由 `CustSyncEventProvider.processCustEvent` 调用 `custSyncEventProcessor.doEvent` 处理通过/拒绝回调，数据库分布存在这两个终态值。

```ground:state_machine
name: "变更记录状态机"
field: "cust_change_record.status"
states:
  - value: "1"
    label: "待提交/初始"
    source: "db_dist"
  - value: "CUST_CHECK_CHECKING"
    label: "审核中"
    source: "db_dist"
  - value: "CUST_CHECK_PASS"
    label: "已通过"
    source: "db_dist"
  - value: "CUST_CHECK_REJECT"
    label: "已驳回"
    source: "db_dist"
  - value: "CUST_CHECK_BACKTOCUSTOM"
    label: "退回客户"
    source: "db_dist"
  - value: "returnCust-*"
    label: "非标准退回客户值（脏数据）"
    source: "db_dist"
```

```ground:claim
claim: "审核通过后变更记录状态变为已生效，驳回变为已驳回"
evidence: "code_path:CustSyncEventProvider.processCustEvent + reqdoc:claim-2"
```

## 版本演进

> (document_claim，未证实) 企业信息变更流程：企业提交变更申请，选择变更项，填写信息，上传证明，创建变更记录（待提交），提交审核。代码中未完整展示创建与状态设置。