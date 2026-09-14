---
type: rule
title: 建档影像同步条件
page_key: build_media_sync_condition
domain: 文件/附件/媒体
status: draft
aliases: [影像同步条件]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:isdo/doDel/doUpload"]
contract_version: "0.1"
belong: rules
---
运营中台回调影像事件时，仅当企业存在且非变更流程（或来源非 PLATFORM_PUSH）才处理；变更影像在审核通过后统一拉取，避免变更过程中实时同步导致数据不一致。来源判定口径见 [[platform_push_source]]，状态流转见 [[cust_build_status]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 isdo/doDel/doUpload 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 建档影像同步条件
content: 运营中台回调影像事件时，仅当企业存在且非变更流程（或来源非 PLATFORM_PUSH）才处理；变更影像在审核通过后统一拉取。
impact: 避免变更流程中实时同步影像导致数据不一致
field_targets: [cust_company_info.cust_source, cust_change_record.oper_cust_id]
evidence: CustMediaFacade.java:isdo/doDel/doUpload
```

关联：[[cust_company_info]]、[[cust_change_record]]、[[platform_push_source]]、[[cust_build_status]]。