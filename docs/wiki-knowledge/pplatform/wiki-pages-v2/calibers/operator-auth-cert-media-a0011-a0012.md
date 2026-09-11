---
type: caliber
title: 操作人/授权类证件影像（A0011/A0012）
page_key: calibers/operator-auth-cert-media-a0011-a0012
domain: 文件/附件/媒体
status: draft
aliases: [A0011, A0012, 操作人证件影像, 授权类证件影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
  - code_path:CustMediaFacade.java:uploadMultiRole
contract_version: "0.1"
---

# 操作人/授权类证件影像（A0011/A0012）

## 业务定位

操作人/授权类证件影像使用 `catgId in ('A0011','A0012')`，并按被授权人证件类型细分（`A001101`/`102`/`103`/`104`/`105`、`A001201`/…）。这类影像按人隔离，因此查询时必须带 `userBusiKey`，详见 [[calibers/archived-media-busikey]]；在互通产品的多角色场景下还会按剩余角色重传（[[rules/multi-role-media-copy]]）。

```ground:caliber
name: 操作人/授权类证件影像
predicate: "MediaFile.catgId in ('A0011','A0012')"
scope: 按被授权人证件类型细分（A001101/102/103/104/105、A001201/…）
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

与 [[calibers/auth-media-a0004]] 一样，这两个分类共同出现在“按 `userBusiKey` 过滤”和“多角色复制”两条规则中。

## 版本演进

- v0（本页）：口径来自 [代码] 证据；后缀细分与证件类型的完整对应表未在本次分析中给出。