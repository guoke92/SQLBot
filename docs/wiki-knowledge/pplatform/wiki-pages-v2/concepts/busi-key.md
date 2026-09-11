---
type: concept
title: busiKey 业务主键
page_key: concepts/busi-key
domain: 文件/附件/媒体
status: draft
aliases: [busiKey, 业务主键, 影像业务主键]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.busiKey
maps_to: "MediaFile.busiKey"
field_targets: [MediaFile.busiKey]
also_confused_with: [userBusiKey]
adjudication: boundary
boundary: "busiKey 一般为产融企业id/项目id；userBusiKey 为联系人id，用于特定分类按人隔离。"
contract_version: "0.1"
---

# busiKey 业务主键

## 业务定位

`busiKey` 是影像归属的业务主键，决定影像挂在产融的哪棵树上：客户影像传产融企业 id，项目/审批影像传项目或审批 id（客户侧口径见 [[calibers/archived-media-busikey]]，项目侧见 [[calibers/project-config-media]]）。

它与 `userBusiKey` 的边界是本域最易出错之处：`busiKey` 回答“属于哪个主体（企业/项目）”，`userBusiKey` 回答“属于哪个人（联系人/操作人）”。只有 `A0004`/`A0011`/`A0012` 等按人隔离的分类才需要 `userBusiKey` 参与过滤；写成“任何分类都要带 userBusiKey”即为越界。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：边界来自 [代码] 证据。