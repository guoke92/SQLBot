---FILE: tables/project_file_info.md ---
---
type: table
title: project_file_info 项目运营文件表
page_key: tables/project_file_info
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件表, 项目文件信息表, 运营文件]
oid: 1
scope:
  databases: [project_file_info]
sources:
  - db:project_file_info
  - code_path:ProjectFileController.java:saveOrUpdate
  - code_path:ProjectFileController.java:buildQueryWrapper
contract_version: "0.1"
---

# project_file_info 项目运营文件表

## 业务定位

`project_file_info` 是项目运营侧的文件元数据表：它只保存“文件在项目里的登记信息”（标题、描述、模块类型、归属项目），不保存影像本体，也不承载影像平台的上传/删除事件。业务上它以项目（`project_id` → `tenant_project`）为聚合根，按 `file_type` 划分到客户资料/审批/核对/核查/其他等模块，供项目运营人员登记与检索资料。

它最容易与影像平台模型 [[tables/media_file]] 混淆：两者都落在“文件”域，但 `project_file_info` 是运营文件登记表（`title`/`content`/`file_type`），[[tables/media_file]] 是影像平台模型（`catgId`/`busiKey`/`modelCode`），二者不同源。术语边界见 [[concepts/media-image]] 与 [[concepts/catg-id]]。

写入与读取语义分别由 [[rules/project-file-save-or-update]] 和 [[rules/project-file-page-query]] 约束。

```ground:fields
fields:
  - name: id
    meaning: 表主键，项目运营文件记录ID（ProjectFileController.saveOrUpdate 时报文 id 不能为空）
    evidence: db
  - name: title
    meaning: 文件标题，列表支持模糊查询
    evidence: db
  - name: content
    meaning: 文件描述/内容，列表支持模糊查询
    evidence: db
  - name: file_type
    meaning: 文件模块类型；实测值域 cust=客户资料、approve=审批、collate=核对/整理、check=核查、other=其他
    evidence: db
  - name: project_id
    meaning: 关联项目ID（指向 tenant_project 项目），分页查询的精确匹配条件
    evidence: db
  - name: enable
    meaning: 逻辑启用标识，默认 Y
    evidence: db
  - name: code
    meaning: 编码
    evidence: db
  - name: name
    meaning: 名称
    evidence: db
  - name: create_by
    meaning: 创建人id
    evidence: db
  - name: create_user
    meaning: 创建人名称
    evidence: db
  - name: update_by
    meaning: 更新人id
    evidence: db
  - name: update_user
    meaning: 更新人名称
    evidence: db
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据，需求侧口径待补充。）

从字段结构可读出的业务意图：`title`/`content` 承担“人读的检索入口”，因此列表检索把二者做成模糊条件；`project_id` 与 `file_type` 承担“机器定位入口”，因此是等值条件。`file_type` 的值域是运营文件自己的模块划分，与影像分类 [[concepts/catg-id]]、影像模型 `modelCode` 都不是同一套枚举，不可互相翻译。

## 版本演进

- v0（本页）：仅依据 [DB] 字段语义与代码侧读写规则（[[rules/project-file-save-or-update]]、[[rules/project-file-page-query]]）建立契约草稿。
- 字段级的中文注释存在较弱的通用字段（`code`/`name`/`enable`/审计字段）含义未细化，属已知留白。

---END FILE---

---FILE: tables/media_file.md ---
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

---END FILE---

---FILE: processes/client-media-event-routing.md ---
---
type: process
title: 影像同步事件路由（客户影像）
page_key: processes/client-media-event-routing
domain: 文件/附件/媒体
status: draft
aliases: [客户影像事件路由, ClientMediaEvent.eventType 路由, 影像事件分发]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:ClientMediaEvent
  - code_path:MediaEventSyncProvider.java:onCustEvent
contract_version: "0.1"
---

# 影像同步事件路由（客户影像）

## 业务定位

客户影像在产融与运营中台之间以事件方式同步。事件类型字段 `ClientMediaEvent.eventType` 决定这次回调会让产融影像树发生什么动作：上传、删除、复制还是信息变更。路由入口在 `MediaEventSyncProvider.onCustEvent`，随后分派到 `CustMediaFacade` 的对应方法。

关键语义：`UPLOAD`/`DELETE`/`INFO_CHANGE` 都会真正改动产融影像并向下游同步；`COPY` 只记日志、不落库——因此“复制”在客户影像链路上不可依赖。

```ground:states
field: ClientMediaEvent.eventType
states:
  - value: UPLOAD
    label: 影像上传
    source: code_enum
  - value: DELETE
    label: 影像删除
    source: code_enum
  - value: COPY
    label: 影像复制
    source: code_enum
  - value: INFO_CHANGE
    label: 影像信息变更（改分类/重命名）
    source: code_enum
```

```ground:transitions
transitions:
  - from: 任意
    event: UPLOAD
    to: 落产融影像树并向下游客户端同步
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent -> CustMediaFacade.doUpload/upload"
  - from: 任意
    event: DELETE
    to: 删除产融影像并同步删除事件
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent -> CustMediaFacade.doDel/del"
  - from: 任意
    event: INFO_CHANGE
    to: 按 src/dest 判定改分类或重命名并同步
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent -> CustMediaFacade.change"
  - from: 任意
    event: COPY
    to: 仅记录日志，不做落库处理
    evidence: "code_path:MediaEventSyncProvider.java:onCustEvent"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

`INFO_CHANGE` 由 `src`/`dest` 对比推导到底是“改分类”还是“重命名”，说明该事件是一个复合语义事件，落到 [[tables/media_file]] 上会分别命中 `catgId` 与命名三字段（见 [[concepts/catg-id]]、[[concepts/specify-file-name]]）。

## 版本演进

- v0（本页）：事件取值与去向来自 [代码] 证据；`COPY` 不落库属当前实现事实，是否为长期设计意图未在本次分析中给出结论。

---END FILE---

---FILE: processes/media-busi-type-routing.md ---
---
type: process
title: 影像业务类型
page_key: processes/media-busi-type-routing
domain: 文件/附件/媒体
status: draft
aliases: [ClientMediaEvent.busiType 路由, 影像业务类型分发, 客户影像与资产影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:ClientMediaEvent
  - code_path:MediaEventSyncProvider.java:onEvent
contract_version: "0.1"
---

# 影像业务类型

## 业务定位

影像回调进入系统后，先按 `ClientMediaEvent.busiType` 判断这是“客户/建档影像”还是“资产影像”，再决定是否进入落库链路。`CUST` 进入客户影像处理分支，`ASSET` 只记日志不落库，其他取值直接抛 `GenericException`（不支持的事件类型）。

这条路由决定了大量客户侧影像能力（授权书、法人证件、操作人证件等口径）只在 `CUST` 分支生效，相关分类口径见 [[calibers/auth-media-a0004]] 与 [[calibers/legal-person-cert-media-a0007-a0008]]。

```ground:states
field: ClientMediaEvent.busiType
states:
  - value: CUST
    label: 客户/建档影像
    source: code_enum
  - value: ASSET
    label: 资产影像
    source: code_enum
```

```ground:transitions
transitions:
  - from: CUST
    event: 收到事件回调
    to: 进入客户影像处理分支
    evidence: "code_path:MediaEventSyncProvider.java:onEvent"
  - from: ASSET
    event: 收到事件回调
    to: 仅记录日志，不落库
    evidence: "code_path:MediaEventSyncProvider.java:onAssetEvent"
  - from: 其他
    event: 收到事件回调
    to: 抛 GenericException 不支持的事件类型
    evidence: "code_path:MediaEventSyncProvider.java:onEvent default"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

`CUST` 分支内部还有“是否实时处理”的前置判断（见 [[rules/archived-media-isdo]]），因此“业务类型路由”只是第一跳，第二跳才是建档/变更流程判定。

## 版本演进

- v0（本页）：业务类型取值与分支去向来自 [代码] 证据；`ASSET` 仅记日志属当前实现事实。

---END FILE---

---FILE: calibers/auth-media-a0004.md ---
---
type: caliber
title: 授权书影像（A0004）
page_key: calibers/auth-media-a0004
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

---END FILE---

---FILE: calibers/electronic-auth-media-a0050.md ---
---
type: caliber
title: 电子签约版授权书影像（A0050）
page_key: calibers/electronic-auth-media-a0050
domain: 文件/附件/媒体
status: draft
aliases: [A0050, 电子签约版授权书, 电子授权书影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
  - code_path:CustMediaFacade.java:uploadElectronicAuthMediaFile
contract_version: "0.1"
---

# 电子签约版授权书影像（A0050）

## 业务定位

`catgId = 'A0050'` 表示电子签约版授权书影像。它与纸质/常规授权书（[[calibers/auth-media-a0004]]）在写入语义上是刻意隔离的：A0050 增量保存、仅新增不删除，禁止写入 A0004、禁止调用 `deleteFileByCatgId`。因此按流程号（`appNo`）追加历史版本是预期行为，不会覆盖既有电子授权书。

```ground:caliber
name: 电子签约版授权书影像
predicate: "MediaFile.catgId = 'A0050'"
scope: 增量保存，仅新增不删除，禁止写入 A0004、禁止调用 deleteFileByCatgId
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

幂等控制细节见 [[rules/electronic-auth-media-idempotent]]：以 `busiKey`/`userBusiKey`/`specifyFileName` 作为命中键。

## 版本演进

- v0（本页）：口径与隔离约束来自 [代码] 证据。

---END FILE---

---FILE: calibers/ca-upgrade-auth-media-a0049.md ---
---
type: caliber
title: CA升级授权书影像（A0049）
page_key: calibers/ca-upgrade-auth-media-a0049
domain: 文件/附件/媒体
status: draft
aliases: [A0049, CA升级授权书, CA 升级授权书影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
contract_version: "0.1"
---

# CA升级授权书影像（A0049）

## 业务定位

`catgId = 'A0049'` 是 CA 升级授权书影像。它的关键特征是“双写”：同时写入运营中台与产融影像树。因此排查 A0049 影像缺失时，需要同时看两侧，而不能只看产融侧。

```ground:caliber
name: CA升级授权书影像
predicate: "MediaFile.catgId = 'A0049'"
scope: CA 升级授权书，同时写运营中台与产融影像树
evidence: code
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

与其他授权书类分类（[[calibers/auth-media-a0004]]、[[calibers/electronic-auth-media-a0050]]）的差异在于写入目标是一对多，而不是命名或幂等策略。

## 版本演进

- v0（本页）：口径来自 [代码] 证据。

---END FILE---

---FILE: calibers/legal-person-cert-media-a0007-a0008.md ---
---
type: caliber
title: 法人证件影像（A0007/A0008）
page_key: calibers/legal-person-cert-media-a0007-a0008
domain: 文件/附件/媒体
status: draft
aliases: [A0007, A0008, 法人证件影像, 法人证件类]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
contract_version: "0.1"
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

---END FILE---

---FILE: calibers/operator-auth-cert-media-a0011-a0012.md ---
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

---END FILE---

---FILE: calibers/archived-media-busikey.md ---
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

---END FILE---

---FILE: calibers/project-config-media.md ---
---
type: caliber
title: 项目配置影像
page_key: calibers/project-config-media
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

---END FILE---

---FILE: concepts/media-image.md ---
---
type: concept
title: 影像（媒体/文件/附件）
page_key: concepts/media-image
domain: 文件/附件/媒体
status: draft
aliases: [影像, 媒体, 文件, 附件]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile
maps_to: "MediaFile（lls.media 影像平台模型，modelCode=MA001）"
field_targets: [MediaFile.modelCode]
also_confused_with: [project_file_info（项目运营文件管理表）, AttachmentInfoDTO（表单附件）]
adjudication: boundary
boundary: "‘影像’指影像平台 MediaFile（catgId/busiKey/modelCode）；project_file_info 是项目运营文件元数据表，二者不同源，仅业务上都属“文件”域。"
contract_version: "0.1"
---

# 影像（媒体/文件/附件）

## 业务定位

在口语与需求表述中，“影像”“媒体”“文件”“附件”经常被混用。本页给出本域裁决：当说的是“影像”时，指的是影像平台模型 [[tables/media_file]]（`lls.media`），它通过 `catgId`（分类）、`busiKey`（归属）、`modelCode`（模型，建档固定 `MA001`）三件套被定位。

最容易混淆的有两个邻居：`project_file_info`（[[tables/project_file_info]]，项目运营文件管理表）与 `AttachmentInfoDTO`（表单附件）。它们都不在影像平台上，也不参与影像上传/删除/复制/信息变更事件（见 [[processes/client-media-event-routing]]）。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：裁决边界来自 [代码] 证据；`AttachmentInfoDTO` 的字段与归属未在本次分析中展开。

---END FILE---

---FILE: concepts/busi-key.md ---
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

---END FILE---

---FILE: concepts/catg-id.md ---
---
type: concept
title: catgId 影像分类ID
page_key: concepts/catg-id
domain: 文件/附件/媒体
status: draft
aliases: [catgId, 影像分类ID, 影像分类]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
maps_to: "MediaFile.catgId（如 A0004/A0049/A0050）"
field_targets: [MediaFile.catgId]
also_confused_with: [modelCode, fileType]
adjudication: boundary
boundary: "catgId 是影像分类维度，modelCode 是模型维度（建档固定 MA001），project_file_info.file_type 是另一套文件模块类型（cust/approve/check/collate/other）。"
contract_version: "0.1"
---

# catgId 影像分类ID

## 业务定位

`catgId` 是影像的分类维度，也是绝大多数影像业务口径的谓词载体：授权书 `A0004`（[[calibers/auth-media-a0004]]）、CA 升级授权书 `A0049`（[[calibers/ca-upgrade-auth-media-a0049]]）、电子签约版授权书 `A0050`（[[calibers/electronic-auth-media-a0050]]）、法人证件 `A0007`/`A0008`（[[calibers/legal-person-cert-media-a0007-a0008]]）、操作人/授权类证件 `A0011`/`A0012`（[[calibers/operator-auth-cert-media-a0011-a0012]]）。分类还支持后缀细分（如 `A000701`、`A001101`），即 `catgId` 自带两级语义。

三个概念不可互译：`catgId`（影像分类）、`modelCode`（影像模型，建档固定 `MA001`）、`project_file_info.file_type`（运营文件模块类型 `cust/approve/check/collate/other`）。把 `file_type` 当成 `catgId` 使用会直接落到另一张表 [[tables/project_file_info]]。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：边界来自 [代码] 与 [DB] 证据；`catgId` 的完整枚举（含全部后缀）未在本次分析中给出。

---END FILE---

---FILE: concepts/specify-file-name.md ---
---
type: concept
title: specifyFileName 指定文件名
page_key: concepts/specify-file-name
domain: 文件/附件/媒体
status: draft
aliases: [specifyFileName, 指定文件名]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.specifyFileName
maps_to: "MediaFile.specifyFileName"
field_targets: [MediaFile.specifyFileName]
also_confused_with: [fileRename, fileName]
adjudication: boundary
boundary: "specifyFileName 为业务指定名（常不带后缀），fileRename 为展示名，fileName 为原始文件名。"
contract_version: "0.1"
---

# specifyFileName 指定文件名

## 业务定位

`specifyFileName` 是业务语义名（通常不带后缀），在 [[tables/media_file]] 的命名三兄弟中承担“业务怎么称呼这份影像”。边界：`fileRename` 是展示名/重命名后的名称，`fileName` 是原始文件名（`A0004` 缺省时置为“授权书.pdf”）。

它同时是若干业务规则的参与字段：A0004 的默认命名口径（[[rules/auth-media-default-file-name]]）与 A0050 的幂等命中键（[[rules/electronic-auth-media-idempotent]]，命中组合为 `busiKey`/`userBusiKey`/`specifyFileName`）。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：边界来自 [代码] 证据。

---END FILE---

---FILE: rules/project-file-save-or-update.md ---
---
type: rule
title: 项目运营文件保存/更新规则
page_key: rules/project-file-save-or-update
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件保存规则, saveOrUpdate 规则]
oid: 1
scope:
  databases: [project_file_info]
sources:
  - code_path:ProjectFileController.java:saveOrUpdate
contract_version: "0.1"
---

# 项目运营文件保存/更新规则

## 业务定位

`project_file_info` 的新增与编辑共用一个入口：`saveOrUpdate` 要求入参 `id` 不能为空；按 `id` 查得记录则仅更新 `title`、`content` 及更新人/时间；查不到则按入参新增并写入创建人/时间。

对使用方的直接影响：能否“保存成功”取决于 `id` 是否命中既有记录，而不是内容是否重复——因此该接口不能被当作“按标题去重写入”的手段。

```ground:rule
name: 项目运营文件保存/更新规则
content: saveOrUpdate 要求入参 id 不能为空；按 id 查得记录则仅更新 title、content 及更新人/时间；查不到则按入参新增并写入创建人/时间。
impact: 项目运营文件的新增与编辑语义由是否存在记录决定，不能用于按标题去重。
field_targets:
  - project_file_info.id
  - project_file_info.title
  - project_file_info.content
evidence: "code_path:ProjectFileController.java:saveOrUpdate"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

表结构见 [[tables/project_file_info]]；列表读取口径见 [[rules/project-file-page-query]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。

---END FILE---

---FILE: rules/project-file-page-query.md ---
---
type: rule
title: 项目运营文件分页查询规则
page_key: rules/project-file-page-query
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件列表口径, buildQueryWrapper 规则, 项目文件检索口径]
oid: 1
scope:
  databases: [project_file_info]
sources:
  - code_path:ProjectFileController.java:buildQueryWrapper
contract_version: "0.1"
---

# 项目运营文件分页查询规则

## 业务定位

项目运营文件列表的检索口径是：`projectId`、`fileType` 为等值过滤，`title`、`content` 为模糊过滤，结果按 `updateTime` 倒序。

这决定了使用方式：先用“项目 + 模块类型”精确定位一个范围，再用标题/描述做模糊收窄；因为排序键是 `updateTime`，列表的“最新”语义是“最近被编辑过”，而不是“最近创建”。

```ground:rule
name: 项目运营文件分页查询规则
content: projectId、fileType 为等值过滤，title、content 为模糊过滤，按 updateTime 倒序。
impact: 列表检索口径：项目+模块类型精确定位，标题/描述模糊。
field_targets:
  - project_file_info.project_id
  - project_file_info.file_type
  - project_file_info.title
  - project_file_info.content
evidence: "code_path:ProjectFileController.java:buildQueryWrapper"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

字段语义见 [[tables/project_file_info]]；写入语义见 [[rules/project-file-save-or-update]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。

---END FILE---

---FILE: rules/auth-media-default-file-name.md ---
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

---END FILE---

---FILE: rules/electronic-auth-media-idempotent.md ---
---
type: rule
title: 电子签约版授权书幂等
page_key: rules/electronic-auth-media-idempotent
domain: 文件/附件/媒体
status: draft
aliases: [A0050 幂等, 电子授权书去重, skipIfSameProcessExists]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:uploadElectronicAuthMediaFile
contract_version: "0.1"
---

# 电子签约版授权书幂等

## 业务定位

电子签约版授权书（[[calibers/electronic-auth-media-a0050]]）的写入是“追加式”的：`A0050` 上传前若 `skipIfSameProcessExists` 且按 `busiKey`/`userBusiKey`/`specifyFileName` 命中既有影像，则跳过；整体策略为仅新增不删除，禁止写入 `A0004`、禁止调用 `deleteFileByCatgId`。

使用方影响：电子授权书按流程号（`appNo`）累积，历史影像不会被覆盖或清除；如果期望“改一份就替换一份”，那是不成立的预期。

```ground:rule
name: 电子签约版授权书幂等
content: A0050 上传前若 skipIfSameProcessExists 且按 busiKey/userBusiKey/specifyFileName 命中既有影像，则跳过；仅新增不删除，禁止写入 A0004、禁止 deleteFileByCatgId。
impact: 电子授权书按流程号（appNo）追加，不覆盖历史。
field_targets:
  - MediaFile.catgId
  - MediaFile.specifyFileName
  - MediaFile.userBusiKey
evidence: "code_path:CustMediaFacade.java:uploadElectronicAuthMediaFile"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

与项目配置影像的“先清空再写入”策略形成对照，见 [[calibers/project-config-media]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。

---END FILE---

---FILE: rules/archived-media-isdo.md ---
---
type: rule
title: 建档影像仅在建档流程实时处理
page_key: rules/archived-media-isdo
domain: 文件/附件/媒体
status: draft
aliases: [isdo 判断, 建档影像实时处理, 变更影像延后处理]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:isdo
contract_version: "0.1"
---

# 建档影像仅在建档流程实时处理

## 业务定位

并不是所有客户影像回调都会立刻落库：`isdo()` 判断要求“影像对应企业存在于产融，且非变更流程（`CustSourceEnum.PLATFORM_PUSH` 或非变更）”时才实时处理；变更类影像则在变更审核通过后统一拉取。

这样做的意图是避免变更流程中的影像回调与变更流程自身产生冲突（例如变更未生效就先把影像挂上）。排查“影像为什么没立刻出现”时，应先确认该影像是否属于变更流程，而不是先怀疑同步链路。

```ground:rule
name: 建档影像仅在建档流程实时处理
content: isdo() 判断：影像对应企业存在于产融，且非变更流程（CustSourceEnum.PLATFORM_PUSH 或非变更）时才实时处理；变更影像审核通过后统一拉取。
impact: 变更类影像回调不实时落库，避免与变更流程冲突。
field_targets:
  - MediaFile.busiKey
evidence: "code_path:CustMediaFacade.java:isdo"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

前置的业务类型路由见 [[processes/media-busi-type-routing]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。

---END FILE---

---FILE: rules/multi-role-media-copy.md ---
---
type: rule
title: 多角色建档影像复制
page_key: rules/multi-role-media-copy
domain: 文件/附件/媒体
status: draft
aliases: [uploadMultiRole, 多角色影像复制, companyTypes 复制影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:uploadMultiRole
contract_version: "0.1"
---

# 多角色建档影像复制

## 业务定位

互通产品场景下，运营中台回传的是单角色，而产融目标系统可能存在多角色。为此系统对 `A0004`/`A0011`/`A0012`（[[calibers/auth-media-a0004]]、[[calibers/operator-auth-cert-media-a0011-a0012]]）按 `extText.companyTypes` 的剩余角色重传影像。

结果与影响：同一份授权书/操作人影像会按角色复制多份。做影像去重统计时，不能假设“一份授权书只有一条记录”，应以角色维度聚合。

```ground:rule
name: 多角色建档影像复制
content: 互通产品下运营中台回传单角色，产融目标系统可能多角色，对 A0004/A0011/A0012 按 extText.companyTypes 剩余角色重传影像。
impact: 同一授权书/操作人影像会按角色复制多份。
field_targets:
  - MediaFile.catgId
  - MediaFile.companyType
evidence: "code_path:CustMediaFacade.java:uploadMultiRole"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：规则来自 [代码] 证据；`companyType` 字段未出现在本次字段语义清单中，其取值集合待补充。

---END FILE---

---FILE: rules/media-download-url.md ---
---
type: rule
title: 影像下载URL生成
page_key: rules/media-download-url
domain: 文件/附件/媒体
status: draft
aliases: [fileUrl 生成, getDownloadUrl 规则, 影像 URL 口径]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:ClientMediaSyncService.java:setInvokeArg
  - code_path:ClientMediaSyncService.java:getRelativePath
contract_version: "0.1"
---

# 影像下载URL生成

## 业务定位

同步下游前，系统按 `path` 生成 `fileUrl`：若 `path` 含 `?` 则截断，并按 `cosHost` 去前缀后调用 `getDownloadUrl`；非全路径则用 `getBrowsUrl`。

对使用方的影响：对外同步出去的 `fileUrl` 统一由 COS 相对路径换取，而不是直接透传入库的 `path`。因此库里存的 `path`（含 http 全路径或带签名参数的情况）与下游拿到的 URL 可能不同形态，排查时必须看生成后的 `fileUrl`。

```ground:rule
name: 影像下载URL生成
content: 同步下游时按 path 生成 fileUrl：path 含 ? 则截断并按 cosHost 去前缀后 getDownloadUrl；非全路径用 getBrowsUrl。
impact: 对外同步的 fileUrl 统一由 COS 相对路径换取。
field_targets:
  - MediaFile.fileUrl
  - MediaFile.path
evidence: "code_path:ClientMediaSyncService.java:setInvokeArg/getRelativePath"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

字段语义见 [[tables/media_file]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。

---END FILE---

---REVIEW: scope | 各页 frontmatter 的 scope.databases 取值---
本次语义分析未给出 `project_file_info`、`MediaFile` 的物理库名：`project_file_info` 仅有 [DB] 证据（无库/schema 信息），`MediaFile` 只有“lls.media 影像平台模型”这一模型级描述。因此各页 `scope.databases` 暂分别取 `project_file_info` 与 `lls.media` 作为库位标识，属占位性质。待确认物理库/schema 命名后需统一回填。
---END REVIEW---