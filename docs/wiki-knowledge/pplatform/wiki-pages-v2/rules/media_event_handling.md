---
type: rule
title: 影像事件处理
page_key: media_event_handling
domain: 文件/附件/媒体
status: draft
aliases: [MediaEventSyncProvider 事件处理]
oid: 1
scope:
  databases: [unknown]
sources: ["code:MediaEventSyncProvider.java:onEvent"]
contract_version: "0.1"
belong: rules
---
MediaEventSyncProvider 只处理 CUST 类型事件的 UPLOAD/DELETE/INFO_CHANGE（见 [[MediaEventType]]），ASSET 类型仅打日志，从而区分客户影像与资产影像的同步。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 MediaEventSyncProvider.onEvent 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 影像事件处理
content: MediaEventSyncProvider 处理 CUST 类型的 UPLOAD/DELETE/INFO_CHANGE；ASSET 类型仅日志。
impact: 区分客户影像与资产影像同步
field_targets: [PlatClientMediaEvent.busiType, PlatClientMediaEvent.eventType]
evidence: MediaEventSyncProvider.java:onEvent
```

关联：[[MediaEventType]]、[[media_file]]、[[build_media_sync_condition]]。