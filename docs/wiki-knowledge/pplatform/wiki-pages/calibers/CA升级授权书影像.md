---
type: caliber
title: CA升级授权书影像
page_key: CA升级授权书影像
domain: 文件媒体与附件
status: published
aliases: []
oid: 1
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---
本页记录口径「CA升级授权书影像」，用于限定客户 CA 升级场景中的授权书影像。

## 需求背景
代码证据显示 `MediaFile.catgId = 'A0049'` 标识 CA 升级授权书影像。该口径支持上传运营中台与产融影像树双端流程。

## 版本演进
v0.1 固化当前代码证据。后续可补充双端上传的详细状态机。

```ground:caliber
name: CA升级授权书影像
predicate: "MediaFile.catgId = 'A0049'"
scope: 客户CA升级授权书影像
evidence: code
```