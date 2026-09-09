---
type: concept
title: busiKey
page_key: busiKey
belong: concepts
domain: 文件媒体与附件
status: published
aliases: [业务键]
oid: 1
sources: [db, code]
contract_version: "0.1"
maps_to: MediaFile.busiKey
adjudication: boundary
also_confused_with: [userBusiKey]
scope:
  databases: [lowcode_pplatform]
---
本页界定 `busiKey` 边界。`busiKey` 通常为企业 ID，与 [[影像]] 的企业维度锚点对应。

## 需求背景
`busiKey` 与 `userBusiKey` 易混：`busiKey` 通常为企业 ID，`userBusiKey` 通常为联系人 ID。在特定 `catgId` 查询下，如 A0004、A0011、A0012，必须用当前联系人 ID 匹配 `userBusiKey`，而非将其与企业级 `busiKey` 混淆。

## 版本演进
v0.1 固化边界。后续可在字段级契约中增加企业/联系人维度校验规则。