---
type: rule
title: 建档影像仅在建档流程实时处理
page_key: rules/archived-media-isdo
domain: 文件/附件/媒体
status: draft
aliases: [isdo 判断, 建档影像实时处理, 变更影像延后处理]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:isdo
contract_version: "0.1"
---

# 建档影像仅在建档流程实时处理

## 业务定位

并不是所有客户影像回调都会立刻落库：`isdo()` 判断要求“影像对应企业存在于产融，且非变更流程（`CustSourceEnum.PLATFORM_PUSH` 或非变更）”时才实时处理；变更类影像则在变更审核通过后统一拉取。

这样做的意图是避免变更流程中的影像回调与变更流程自身产生冲突（例如变更未生效就先把影像挂上）。排查“影像为什么没立刻出现”时，应先确认该影像是否属于变更流程，而不是先怀疑同步链路。

```ground:rule
name: 建档影像仅在建档流程实时处理
content: isdo() 判断：影像对应企业存在于产融，且非变更流程（CustSourceEnum.PLATFORM_PUSH 或非变更）时才实时处理；变更影像审核通过后统一拉取。
impact: 变更类影像回调不实时落库，避免与变更流程冲突。
field_targets:
  - MediaFile.busiKey
evidence: "code_path:CustMediaFacade.java:isdo"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

前置的业务类型路由见 [[processes/media-busi-type-routing]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。