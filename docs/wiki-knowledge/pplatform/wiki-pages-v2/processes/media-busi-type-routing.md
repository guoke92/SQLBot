---
type: process
title: 影像业务类型
page_key: media-busi-type-routing
domain: 文件/附件/媒体
status: draft
aliases: [ClientMediaEvent.busiType 路由, 影像业务类型分发, 客户影像与资产影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:ClientMediaEvent
  - code_path:MediaEventSyncProvider.java:onEvent
contract_version: "0.1"
belong: processes
---

# 影像业务类型

## 业务定位

影像回调进入系统后，先按 `ClientMediaEvent.busiType` 判断这是“客户/建档影像”还是“资产影像”，再决定是否进入落库链路。`CUST` 进入客户影像处理分支，`ASSET` 只记日志不落库，其他取值直接抛 `GenericException`（不支持的事件类型）。

这条路由决定了大量客户侧影像能力（授权书、法人证件、操作人证件等口径）只在 `CUST` 分支生效，相关分类口径见 [[calibers/auth-media-a0004]] 与 [[calibers/legal-person-cert-media-a0007-a0008]]。

```ground:states
field: ClientMediaEvent.busiType
states:
  - value: CUST
    label: 客户/建档影像
    source: code_enum
  - value: ASSET
    label: 资产影像
    source: code_enum
```

```ground:transitions
transitions:
  - from: CUST
    event: 收到事件回调
    to: 进入客户影像处理分支
    evidence: "code_path:MediaEventSyncProvider.java:onEvent"
  - from: ASSET
    event: 收到事件回调
    to: 仅记录日志，不落库
    evidence: "code_path:MediaEventSyncProvider.java:onAssetEvent"
  - from: 其他
    event: 收到事件回调
    to: 抛 GenericException 不支持的事件类型
    evidence: "code_path:MediaEventSyncProvider.java:onEvent default"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

`CUST` 分支内部还有“是否实时处理”的前置判断（见 [[rules/archived-media-isdo]]），因此“业务类型路由”只是第一跳，第二跳才是建档/变更流程判定。

## 版本演进

- v0（本页）：业务类型取值与分支去向来自 [代码] 证据；`ASSET` 仅记日志属当前实现事实。