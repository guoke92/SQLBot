---
type: table
title: MediaFile 影像文件模型
page_key: tables/media_file
domain: 文件/附件/媒体
status: draft
aliases: [MediaFile, 影像平台模型, 媒体文件, lls.media]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile
  - code_path:MediaEventSyncProvider.java
  - code_path:CustMediaFacade.java
  - code_path:ClientMediaSyncService.java
contract_version: "0.1"
---

# MediaFile 影像文件模型

## 业务定位

`MediaFile` 是影像平台（lls.media）的影像模型，`modelCode` 在建档场景固定为 `MA001`。它承载“影像本体在存储上的归属关系”：`busiKey`/`userBusiKey` 决定影像挂在谁的树上，`catgId` 决定影像属于哪类业务资料，`path`/`spath`/`destPath`/`storageType` 决定文件存在哪里，`specifyFileName`/`fileRename`/`fileName` 决定它对外叫什么。

与运营文件表 [[tables/project_file_info]] 的边界：`MediaFile` 是影像平台模型，参与上传、删除、复制、信息变更等事件；`project_file_info` 只是项目运营文件的元数据登记。术语映射见 [[concepts/media-image]]、[[concepts/busi-key]]、[[concepts/catg-id]]、[[concepts/specify-file-name]]。

影像的分类口径（`catgId` 取值语义）落在 [[calibers/auth-media-a0004]]、[[calibers/electronic-auth-media-a0050]]、[[calibers/ca-upgrade-auth-media-a0049]]、[[calibers/legal-person-cert-media-a0007-a0008]]、[[calibers/operator-auth-cert-media-a0011-a0012]]、[[calibers/project-config-media]]；归属主键口径见 [[calibers/archived-media-busikey]]。

```ground:fields
fields:
  - name: modelCode
    meaning: 影像模型编码，建档影像固定为 MA001（MeidaConstants.MODEL_CODE）
    evidence: code
  - name: catgId
    meaning: 影像分类ID（A0004=授权书，A0007/A0008=法人证件类，A0011/A0012=操作人/授权书类，A0049=CA升级授权书，A0050=电子签约版授权书；带后缀如 A000701/A001101 按证件类型细分）
    evidence: code
  - name: busiKey
    meaning: 影像归属业务主键：客户影像传产融企业id，项目/审批影像传项目或审批id
    evidence: code
  - name: userBusiKey
    meaning: 影像归属用户业务主键：联系人/操作人id，用于 A0004/A0011/A0012 等分类按人过滤
    evidence: code
  - name: specifyFileName
    meaning: 指定文件名（业务语义名，不带后缀），A0004 默认“授权书”
    evidence: code
  - name: fileRename
    meaning: 文件展示名/重命名后的名称
    evidence: code
  - name: fileName
    meaning: 原始文件名，A0004 缺省时置为“授权书.pdf”
    evidence: code
  - name: path
    meaning: 影像存储相对路径（COS 相对路径或 http 全路径），下载时据此生成 URL
    evidence: code
  - name: spath
    meaning: 影像存储路径（与 path 同源，用于展示/同步）
    evidence: code
  - name: destPath
    meaning: 上传目标存储路径（uploadCosPathMediaFile 入参）
    evidence: code
  - name: storageType
    meaning: 存储类型（COS 等），取自 MediaStorageType
    evidence: code
  - name: mediaCheckStatus
    meaning: 影像审核状态
    evidence: code
  - name: fileStatus
    meaning: 文件状态
    evidence: code
  - name: fileType
    meaning: 文件类型
    evidence: code
  - name: fileUrl
    meaning: 文件下载/浏览 URL（由 path 经 CosFileUtil.getDownloadUrl 生成）
    evidence: code
  - name: dataHash
    meaning: 文件 MD5/哈希，用于影像记录直接入库
    evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

从字段组合可读出的业务意图：`system` 侧的存储字段（`path`/`spath`/`destPath`/`storageType`）服务于“一次上传、多处同步”——对外同步时统一由 `path` 换取 `fileUrl`（见 [[rules/media-download-url]]）；命名三兄弟（`specifyFileName`/`fileRename`/`fileName`）服务于“业务名与物理名解耦”，其中 A0004 有强默认命名口径（见 [[rules/auth-media-default-file-name]]）。

## 版本演进

- v0（本页）：字段语义来自 [代码] 证据；`mediaCheckStatus`、`fileStatus`、`fileType` 的取值枚举未在本次语义分析中给出，属已知留白。
- 后续版本：待补充 `mediaCheckStatus` 等状态字段的取值集合与状态流转（如与审核流程的对应关系）。