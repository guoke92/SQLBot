---
type: rule
title: 授权书默认文件名
page_key: rules/auth-media-default-file-name
domain: 文件/附件/媒体
status: draft
aliases: [A0004 默认文件名, 授权书.pdf, 授权书默认名]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:upload
contract_version: "0.1"
---

# 授权书默认文件名

## 业务定位

当 `catgId = A0004`（[[calibers/auth-media-a0004]]）时，系统对命名做强兜底：`fileName` 缺省置为「授权书.pdf」，`specifyFileName` 缺省置为「授权书」。

因此 A0004 授权书影像的名称在该场景下不具区分度，按名称做筛选或对账会退化为“全选”。区分应回到 `busiKey`/`userBusiKey`（[[calibers/archived-media-busikey]]）与分类本身。

```ground:rule
name: 授权书默认文件名
content: catgId=A0004 时，fileName 缺省置为「授权书.pdf」，specifyFileName 缺省置为「授权书」。
impact: A0004 授权书影像有强默认命名口径。
field_targets:
  - MediaFile.fileName
  - MediaFile.specifyFileName
evidence: "code_path:CustMediaFacade.java:upload"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

命名三字段的边界见 [[concepts/specify-file-name]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。