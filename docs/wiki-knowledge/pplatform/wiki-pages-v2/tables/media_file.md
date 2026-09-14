---
type: table
title: 客户影像文件表
page_key: media_file
domain: 文件/附件/媒体
status: draft
aliases: [media_file, 影像表, 影像树]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:PlatFormMediaApplication.java:listCustMediaFile/lookupCustMedia", "code:CustMediaFacade.java:uploadElectronicAuthMediaFile", "code:ProjectMediaFacade.java:streamApprovalMediaZip"]
contract_version: "0.1"
belong: tables
---

media_file 是「影像」（[[media]]）的底层存储表，由 IMediaOperaProvider 维护、经 MediaFacade/CustMediaFacade 访问，按分类编码 catgId（[[catg_id]]）与业务键 busiKey（[[busi_key]]）/userBusiKey 组织。影像分类口径见 [[media_catg_a0004]]、[[media_catg_a0049]]、[[media_catg_a0050]]；上传与查询受 [[cust_media_precheck]]、[[catg_operator_filter]]、[[electronic_auth_incremental_upload]]、[[dual_side_media_upload]]、[[project_config_overwrite_upload]]、[[project_approval_zip_download]] 等规则约束。

## 需求背景
本期语义分析未提供需求文档主张；本页业务定位来自术语桥与规则证据（MediaFacade、CustMediaFacade、ProjectMediaFacade、PlatFormMediaApplication）。

## 版本演进
v0 初版：本表未获得字段级语义证据，故不产出 ground:table 锚点块；已涉及的字段引用（catg_id、busi_key、user_busi_key、path、specify_file_name）仅出现在规则锚点中，待补充库表证据后补齐（见 REVIEW）。

关联：[[media]]、[[attachment_info]]、[[project_file_info]]、[[catg_id]]、[[busi_key]]、[[media_event_handling]]。

```ground:table
table: media_file
fields:
  - name: modelCode
    desc: 影像模型编码，建档影像固定为 MA001（MeidaConstants.MODEL_CODE）
  - name: catgId
    desc: 影像分类ID（A0004=授权书，A0007/A0008=法人证件类，A0011/A0012=操作人/授权书类，A0049=CA升级授权书，A0050=电子签约版授权书；带后缀如 A000701/A001101 按证件类型细分）
  - name: busiKey
    desc: 影像归属业务主键：客户影像传产融企业id，项目/审批影像传项目或审批id
  - name: userBusiKey
    desc: 影像归属用户业务主键：联系人/操作人id，用于 A0004/A0011/A0012 等分类按人过滤
  - name: specifyFileName
    desc: 指定文件名（业务语义名，不带后缀），A0004 默认“授权书”
  - name: fileRename
    desc: 文件展示名/重命名后的名称
  - name: fileName
    desc: 原始文件名，A0004 缺省时置为“授权书.pdf”
  - name: path
    desc: 影像存储相对路径（COS 相对路径或 http 全路径），下载时据此生成 URL
  - name: spath
    desc: 影像存储路径（与 path 同源，用于展示/同步）
  - name: destPath
    desc: 上传目标存储路径（uploadCosPathMediaFile 入参）
  - name: storageType
    desc: 存储类型（COS 等），取自 MediaStorageType
  - name: mediaCheckStatus
    desc: 影像审核状态
  - name: fileStatus
    desc: 文件状态
  - name: fileType
    desc: 文件类型
  - name: fileUrl
    desc: 文件下载/浏览 URL（由 path 经 CosFileUtil.getDownloadUrl 生成）
  - name: dataHash
    desc: 文件 MD5/哈希，用于影像记录直接入库
```
