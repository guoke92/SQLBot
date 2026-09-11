---
type: caliber
title: 建档影像企业主键口径
page_key: calibers/archived-media-busikey
domain: 文件/附件/媒体
status: draft
aliases: [影像归属主键口径, busiKey 口径, 客户影像归属]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.busiKey
  - code:MediaFile.userBusiKey
contract_version: "0.1"
---

# 建档影像企业主键口径

## 业务定位

客户影像以产融企业 id 作为 `busiKey`（即 `cust_company_info.id`），这是“这棵树属于哪家企业”的锚点；对于 `A0004`/`A0011`/`A0012` 这类按人隔离的分类，还需要 `userBusiKey`（联系人 id）二次过滤，才能得到“某企业某人的授权书/证件影像”。

混用这两个键会造成“企业级影像被当成人员影像”或漏取影像，二者边界见 [[concepts/busi-key]]。

```ground:caliber
name: 建档影像企业主键口径
predicate: "MediaFile.busiKey = cust_company_info.id"
scope: 客户影像以产融企业id为 busiKey，A0004/A0011/A0012 另按 userBusiKey（联系人id）过滤
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

项目/审批影像的 `busiKey` 则传项目或审批 id，与客户影像口径不同（对比 [[calibers/project-config-media]]）。

## 版本演进

- v0（本页）：口径来自 [代码] 证据。