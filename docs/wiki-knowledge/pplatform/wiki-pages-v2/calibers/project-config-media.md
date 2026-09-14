---
type: caliber
title: 项目配置影像
page_key: project-config-media
domain: 文件/附件/媒体
status: draft
aliases: [项目配置影像, PROJECT_CONFIG, 项目上线审批影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.busiKey
  - code:MediaFile.catgId
contract_version: "0.1"
belong: calibers
---

# 项目配置影像

## 业务定位

项目配置影像是项目上线审批影像树中的一类：`busiKey = projectApprovalId` 且 `catgId = ProjectApprovalMediaCatgEnum.PROJECT_CONFIG`。该目录采用“同项目重复推送先清空该目录再写入”的策略，即写入是替换而非追加。

注意它与项目运营文件表 [[tables/project_file_info]] 不是一回事：前者在影像平台上、以审批 id 为归属；后者是运营文件的元数据登记。

```ground:caliber
name: 项目配置影像
predicate: "MediaFile.busiKey = projectApprovalId 且 catgId = ProjectApprovalMediaCatgEnum.PROJECT_CONFIG"
scope: 项目上线审批影像树，同项目重复推送先清空该目录再写入
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

“先清空再写入”与 [[calibers/electronic-auth-media-a0050]] 的“仅新增不删除”形成对照，两者是可被误用的兄弟口径。

## 版本演进

- v0（本页）：口径来自 [代码] 证据。