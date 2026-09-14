---
type: caliber
title: 电子签约版授权书影像（A0050）
page_key: electronic-auth-media-a0050
domain: 文件/附件/媒体
status: draft
aliases: [A0050, 电子签约版授权书, 电子授权书影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
  - code_path:CustMediaFacade.java:uploadElectronicAuthMediaFile
contract_version: "0.1"
belong: calibers
---

# 电子签约版授权书影像（A0050）

## 业务定位

`catgId = 'A0050'` 表示电子签约版授权书影像。它与纸质/常规授权书（[[calibers/auth-media-a0004]]）在写入语义上是刻意隔离的：A0050 增量保存、仅新增不删除，禁止写入 A0004、禁止调用 `deleteFileByCatgId`。因此按流程号（`appNo`）追加历史版本是预期行为，不会覆盖既有电子授权书。

```ground:caliber
name: 电子签约版授权书影像
predicate: "MediaFile.catgId = 'A0050'"
scope: 增量保存，仅新增不删除，禁止写入 A0004、禁止调用 deleteFileByCatgId
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

幂等控制细节见 [[rules/electronic-auth-media-idempotent]]：以 `busiKey`/`userBusiKey`/`specifyFileName` 作为命中键。

## 版本演进

- v0（本页）：口径与隔离约束来自 [代码] 证据。