---
type: caliber
title: CA升级授权书影像（A0049）
page_key: ca-upgrade-auth-media-a0049
domain: 文件/附件/媒体
status: draft
aliases: [A0049, CA升级授权书, CA 升级授权书影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
contract_version: "0.1"
belong: calibers
---

# CA升级授权书影像（A0049）

## 业务定位

`catgId = 'A0049'` 是 CA 升级授权书影像。它的关键特征是“双写”：同时写入运营中台与产融影像树。因此排查 A0049 影像缺失时，需要同时看两侧，而不能只看产融侧。

```ground:caliber
name: CA升级授权书影像
predicate: "MediaFile.catgId = 'A0049'"
scope: CA 升级授权书，同时写运营中台与产融影像树
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

与其他授权书类分类（[[calibers/auth-media-a0004]]、[[calibers/electronic-auth-media-a0050]]）的差异在于写入目标是一对多，而不是命名或幂等策略。

## 版本演进

- v0（本页）：口径来自 [代码] 证据。