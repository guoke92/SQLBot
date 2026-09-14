---
type: process
title: 影像同步事件路由（客户影像）
page_key: client-media-event-routing
domain: 文件/附件/媒体
status: draft
aliases: [客户影像事件路由, ClientMediaEvent.eventType 路由, 影像事件分发]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:ClientMediaEvent
  - code_path:MediaEventSyncProvider.java:onCustEvent
contract_version: "0.1"
belong: processes
---

# 影像同步事件路由（客户影像）

## 业务定位

客户影像在产融与运营中台之间以事件方式同步。事件类型字段 `ClientMediaEvent.eventType` 决定这次回调会让产融影像树发生什么动作：上传、删除、复制还是信息变更。路由入口在 `MediaEventSyncProvider.onCustEvent`，随后分派到 `CustMediaFacade` 的对应方法。

关键语义：`UPLOAD`/`DELETE`/`INFO_CHANGE` 都会真正改动产融影像并向下游同步；`COPY` 只记日志、不落库——因此“复制”在客户影像链路上不可依赖。

```ground:states
field: ClientMediaEvent.eventType
states:
  - value: UPLOAD
    label: 影像上传
    source: code_enum
  - value: DELETE
    label: 影像删除
    source: code_enum
  - value: COPY
    label: 影像复制
    source: code_enum
  - value: INFO_CHANGE
    label: 影像信息变更（改分类/重命名）
    source: code_enum
```

```ground:transitions
transitions:
  - from: 任意
    event: UPLOAD
    to: 落产融影像树并向下游客户端同步
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent -> CustMediaFacade.doUpload/upload"
  - from: 任意
    event: DELETE
    to: 删除产融影像并同步删除事件
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent -> CustMediaFacade.doDel/del"
  - from: 任意
    event: INFO_CHANGE
    to: 按 src/dest 判定改分类或重命名并同步
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent -> CustMediaFacade.change"
  - from: 任意
    event: COPY
    to: 仅记录日志，不做落库处理
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

`INFO_CHANGE` 由 `src`/`dest` 对比推导到底是“改分类”还是“重命名”，说明该事件是一个复合语义事件，落到 [[tables/media_file]] 上会分别命中 `catgId` 与命名三字段（见 [[concepts/catg-id]]、[[concepts/specify-file-name]]）。

## 版本演进

- v0（本页）：事件取值与去向来自 [代码] 证据；`COPY` 不落库属当前实现事实，是否为长期设计意图未在本次分析中给出结论。