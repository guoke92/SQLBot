---
type: caliber
title: 授权书影像（A0004）
page_key: auth-media-a0004
domain: 文件/附件/媒体
status: draft
aliases: [A0004, 授权书影像, catgId=A0004]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
  - code_path:CustMediaFacade.java:upload
contract_version: "0.1"
belong: calibers
---

# 授权书影像（A0004）

## 业务定位

企业授权书影像是客户建档场景中最核心的一类影像：`catgId = 'A0004'`，挂在企业 + 管理员/操作人维度，默认文件名“授权书”/“授权书.pdf”。它也是少数带有“强默认命名”的分类（见 [[rules/auth-media-default-file-name]]），并会参与多角色复制（见 [[rules/multi-role-media-copy]]）。

统计与筛选这类影像时，应使用本页谓词而不是按名称模糊匹配；名称在缺省场景下会被系统改写成“授权书”，不具备区分度。

```ground:caliber
name: 授权书影像
predicate: "MediaFile.catgId = 'A0004'"
scope: 企业授权书影像，默认文件名“授权书”/“授权书.pdf”，挂在企业+管理员/操作人维度
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

维度说明：`busiKey`（产融企业id）定位企业，`userBusiKey`（联系人id）在该分类下用于按人过滤，口径参见 [[calibers/archived-media-busikey]]。

## 版本演进

- v0（本页）：口径来自 [代码] 证据。