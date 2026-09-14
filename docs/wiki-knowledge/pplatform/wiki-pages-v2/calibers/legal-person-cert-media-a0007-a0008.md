---
type: caliber
title: 法人证件影像（A0007/A0008）
page_key: legal-person-cert-media-a0007-a0008
domain: 文件/附件/媒体
status: draft
aliases: [A0007, A0008, 法人证件影像, 法人证件类]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
contract_version: "0.1"
belong: calibers
---

# 法人证件影像（A0007/A0008）

## 业务定位

法人证件类影像使用 `catgId in ('A0007','A0008')` 这一组分类，并按企业法人证件类型再细分（`A000701`/`702`/`703`/`704`/`705` 等带后缀取值）。因此“法人证件是否齐全”的判断必须按后缀细分后逐类核对，不能只按前缀统计。

```ground:caliber
name: 法人证件影像
predicate: "MediaFile.catgId in ('A0007','A0008')"
scope: 按企业法人证件类型细分（A000701/702/703/704/705 等）
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

后缀细分与 [[concepts/catg-id]] 中“catgId 是分类维度”的说明一致：`catgId` 自身即可承载两级语义，不需要借助 `fileType`。

## 版本演进

- v0（本页）：口径来自 [代码] 证据；具体后缀与证件类型的完整对应表未在本次分析中给出。