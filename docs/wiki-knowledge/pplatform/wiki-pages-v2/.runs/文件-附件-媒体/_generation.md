---FILE: tables/project_file_info.md ---
---
type: table
title: 项目文件信息表
page_key: project_file_info
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件表, 项目文件表]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info 字段语义", "code:ProjectFileController.java:buildQueryWrapper"]
contract_version: "0.1"
---
project_file_info 是「项目运营文件管理」的元数据主表：登记项目下审批（approve）、审核（check）、整理（collate）、客户（cust）、其他（other）五类文件的标题与描述，文件实体仍存放在对象存储，本表只保留元数据与审批流程关联字段。它与 [[media_file]]（客户影像树）、[[attachment_info]]（表单模板附件）不是同一套存储，边界见 [[project_file]]、[[media]]、[[catg_id]]。

## 需求背景
本期语义分析未提供需求文档主张（reqdoc_claims 为空），业务定位与字段含义均来自库表与代码证据。

## 版本演进
v0 初版：字段语义、五个文件类型口径（[[project_file_type_cust]]、[[project_file_type_approve]]、[[project_file_type_check]]、[[project_file_type_collate]]、[[project_file_type_other]]）与分页查询规则 [[project_file_page_query]] 均来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: project_file_info
fields:
  - name: id
    type: unknown
    desc: 表主键
    dict: "-"
  - name: title
    type: unknown
    desc: 文件标题
    dict: "-"
  - name: content
    type: unknown
    desc: 文件描述
    dict: "-"
  - name: file_type
    type: unknown
    desc: 文件模块类型，取值 approve/check/collate/cust/other
    dict: "字面量 approve/check/collate/cust/other"
  - name: project_id
    type: unknown
    desc: 关联项目ID，指向 tenant_project.id
    dict: "-"
  - name: enable
    type: unknown
    desc: 逻辑删除标识，Y 有效
    dict: "Y/N"
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识
    dict: "-"
  - name: app_tenant_code
    type: unknown
    desc: 逻辑租户标识
    dict: "-"
  - name: create_by
    type: unknown
    desc: 创建人id
    dict: "-"
  - name: create_user
    type: unknown
    desc: 创建人名称
    dict: "-"
  - name: create_time
    type: unknown
    desc: 创建时间
    dict: "-"
  - name: update_by
    type: unknown
    desc: 更新人id
    dict: "-"
  - name: update_user
    type: unknown
    desc: 更新人名称
    dict: "-"
  - name: update_time
    type: unknown
    desc: 更新时间，默认按此字段倒序
    dict: "-"
  - name: act_procinst_id
    type: unknown
    desc: 流程实例ID
    dict: "-"
  - name: act_procinst_no
    type: unknown
    desc: 流程申请编号
    dict: "-"
  - name: act_procinst_status
    type: unknown
    desc: 当前审批状态
    dict: "-"
  - name: act_procinst_date
    type: unknown
    desc: 审批结束时间
    dict: "-"
  - name: code
    type: unknown
    desc: 编码
    dict: "-"
  - name: name
    type: unknown
    desc: 名称
    dict: "-"
  - name: remark
    type: unknown
    desc: 备注
    dict: "-"
  - name: organization_id
    type: unknown
    desc: 机构编号
    dict: "-"
```

关联：[[tenant_project]]、[[project_file]]、[[media_file]]。

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 客户企业信息表
page_key: cust_company_info
domain: 文件/附件/媒体
status: draft
aliases: [企业信息表, 客户企业表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany", "code:CustMediaFacade.java:isdo"]
contract_version: "0.1"
---
cust_company_info 是企业建档与认证的主表，也是客户影像（[[media]]）业务的锚点：影像查询规则 [[cust_media_precheck]] 以本表 id 反查企业与管理员，建档影像同步规则 [[build_media_sync_condition]] 依赖本表 cust_source。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据（CustCompanyInfoApplication、CustMediaFacade、CustCompanyInfoDao）。

## 版本演进
v0 初版：字段语义、状态口径 [[cust_cert_success]]、[[platform_push_source]] 与枚举 [[CustBuildStatusEnum]]、[[CustStatusEnum]]、[[CustSourceEnum]]、[[IDTypeEnum]]、[[OpenStatus]] 来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: cust_company_info
fields:
  - name: id
    type: unknown
    desc: 企业主键
    dict: "-"
  - name: code
    type: unknown
    desc: 企业编码，被 cust_person_info.ref_cust_company_info 等引用
    dict: "-"
  - name: cust_company_type
    type: unknown
    desc: 企业角色，存储为 JSON 数组字符串（如 ["SUPPLIER"]）
    dict: CustCompanyTypeEnum
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识
    dict: "-"
  - name: platform_cust_id
    type: unknown
    desc: 运营中台企业id
    dict: "-"
  - name: cust_source
    type: unknown
    desc: 建档数据来源，PLATFORM_PUSH 表示平台推送
    dict: CustSourceEnum
  - name: cust_build_status
    type: unknown
    desc: 企业认证/建档状态
    dict: CustBuildStatusEnum
  - name: cust_status
    type: unknown
    desc: 客户状态
    dict: CustStatusEnum
  - name: legal_certification_type
    type: unknown
    desc: 法人证件类型，存储 IDTypeEnum.name()
    dict: IDTypeEnum
  - name: need_register_ca
    type: unknown
    desc: 是否开通电子签章，Y/N
    dict: OpenStatus
```

关联：[[cust_person_info]]、[[cust_role_info]]、[[cust_build_record]]、[[cust_change_record]]、[[cust_build_status]]。

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: 客户联系人信息表
page_key: cust_person_info
domain: 文件/附件/媒体
status: draft
aliases: [联系人表, 客户联系人表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany", "code:PlatFormMediaApplication.java:personInfoService.getOne"]
contract_version: "0.1"
---
cust_person_info 保存企业下的联系人（管理员/操作员）及其证件与角色信息，通过 ref_cust_company_info 逻辑外键指向 [[cust_company_info]].code。客户影像查询前置校验 [[cust_media_precheck]] 与按操作人过滤规则 [[catg_operator_filter]] 都以本表的管理员记录为基准。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据。

## 版本演进
v0 初版：字段语义与口径 [[admin_person]]、角色口径 [[role_supplier]]、[[role_core]]、[[role_dealer]]、[[role_finance]] 来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: cust_person_info
fields:
  - name: id
    type: unknown
    desc: 联系人主键
    dict: "-"
  - name: ref_cust_company_info
    type: unknown
    desc: 关联企业 code，逻辑外键指向 cust_company_info.code
    dict: "-"
  - name: user_type
    type: unknown
    desc: 联系人类型，admin 管理员/operator 操作员
    dict: UserTypeEnum
  - name: company_type
    type: unknown
    desc: 客户角色，单个角色 dictKey
    dict: CustCompanyTypeEnum
  - name: certification_type
    type: unknown
    desc: 证件类型，存储 IDTypeEnum.name()
    dict: IDTypeEnum
  - name: enable
    type: unknown
    desc: 启用标识，Y 有效
    dict: "Y/N"
```

关联：[[cust_company_info]]、[[cust_role_info]]、[[busi_key]]。

---END FILE---

---FILE: tables/cust_role_info.md ---
---
type: table
title: 客户角色信息表
page_key: cust_role_info
domain: 文件/附件/媒体
status: draft
aliases: [角色表, 客户角色表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:listCustMediaFile"]
contract_version: "0.1"
---
cust_role_info 记录企业持有的角色（单个角色 dictKey），与 [[cust_company_info]].cust_company_type 的 JSON 数组多角色形态不同。它是客户影像查询前置校验 [[cust_media_precheck]] 的必需条件之一：角色记录不存在时直接抛异常。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据。

## 版本演进
v0 初版：字段语义与客户角色口径 [[role_supplier]]、[[role_core]]、[[role_dealer]]、[[role_finance]] 来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: cust_role_info
fields:
  - name: ref_cust_company_info
    type: unknown
    desc: 关联企业 code
    dict: "-"
  - name: role_type
    type: unknown
    desc: 角色类型，单个角色 dictKey
    dict: CustCompanyTypeEnum
  - name: platform_cust_id
    type: unknown
    desc: 运营中台企业id
    dict: "-"
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识
    dict: "-"
```

关联：[[cust_company_info]]、[[cust_person_info]]。

---END FILE---

---FILE: tables/cust_build_record.md ---
---
type: table
title: 企业建档记录表
page_key: cust_build_record
domain: 文件/附件/媒体
status: draft
aliases: [建档记录表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java", "code:CustMediaFacade.java"]
contract_version: "0.1"
---
cust_build_record 记录运营中台客户与产融联系人之间的建档过程关联，是建档影像同步与 [[cust_build_status]] 状态流转的辅助记录表。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据。

## 版本演进
v0 初版：字段语义来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: cust_build_record
fields:
  - name: plat_cust_id
    type: unknown
    desc: 运营中台客户id
    dict: "-"
  - name: person_id
    type: unknown
    desc: 产融联系人id
    dict: "-"
```

关联：[[cust_company_info]]、[[cust_person_info]]、[[build_media_sync_condition]]。

---END FILE---

---FILE: tables/cust_change_record.md ---
---
type: table
title: 客户变更记录表
page_key: cust_change_record
domain: 文件/附件/媒体
status: draft
aliases: [变更记录表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:isdo/doDel/doUpload"]
contract_version: "0.1"
---
cust_change_record 记录运营中台客户与产融企业之间的变更信息；变更过程中的影像不在事件回调里实时同步，而由规则 [[build_media_sync_condition]] 约束在审核通过后统一拉取。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据。

## 版本演进
v0 初版：字段语义来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: cust_change_record
fields:
  - name: oper_cust_id
    type: unknown
    desc: 运营中台客户id
    dict: "-"
  - name: cust_id
    type: unknown
    desc: 产融企业id
    dict: "-"
  - name: oper_cust_info
    type: unknown
    desc: 运营中台客户信息 JSON，包含 personId/oldPersonId 等
    dict: "-"
```

关联：[[cust_company_info]]、[[build_media_sync_condition]]。

---END FILE---

---FILE: tables/tenant_project.md ---
---
type: table
title: 租户项目表
page_key: tenant_project
domain: 文件/附件/媒体
status: draft
aliases: [项目表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectFileController.java:buildQueryWrapper"]
contract_version: "0.1"
---
tenant_project 是项目主表，其 id 被 [[project_file_info]].project_id 引用，构成项目运营文件（[[project_file]]）的归属维度。

## 需求背景
本期语义分析未提供需求文档主张，字段语义来自代码证据。

## 版本演进
v0 初版：字段语义来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: tenant_project
fields:
  - name: id
    type: unknown
    desc: 租户项目主键，被 project_file_info.project_id 引用
    dict: "-"
  - name: project_status
    type: unknown
    desc: 项目状态
    dict: "-"
```

关联：[[project_file_info]]、[[project_file_page_query]]。

---END FILE---

---FILE: tables/media_file.md ---
---
type: table
title: 客户影像文件表
page_key: media_file
domain: 文件/附件/媒体
status: draft
aliases: [media_file, 影像表, 影像树]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:listCustMediaFile/lookupCustMedia", "code:CustMediaFacade.java:uploadElectronicAuthMediaFile", "code:ProjectMediaFacade.java:streamApprovalMediaZip"]
contract_version: "0.1"
---
media_file 是「影像」（[[media]]）的底层存储表，由 IMediaOperaProvider 维护、经 MediaFacade/CustMediaFacade 访问，按分类编码 catgId（[[catg_id]]）与业务键 busiKey（[[busi_key]]）/userBusiKey 组织。影像分类口径见 [[media_catg_a0004]]、[[media_catg_a0049]]、[[media_catg_a0050]]；上传与查询受 [[cust_media_precheck]]、[[catg_operator_filter]]、[[electronic_auth_incremental_upload]]、[[dual_side_media_upload]]、[[project_config_overwrite_upload]]、[[project_approval_zip_download]] 等规则约束。

## 需求背景
本期语义分析未提供需求文档主张；本页业务定位来自术语桥与规则证据（MediaFacade、CustMediaFacade、ProjectMediaFacade、PlatFormMediaApplication）。

## 版本演进
v0 初版：本表未获得字段级语义证据，故不产出 ground:table 锚点块；已涉及的字段引用（catg_id、busi_key、user_busi_key、path、specify_file_name）仅出现在规则锚点中，待补充库表证据后补齐（见 REVIEW）。

关联：[[media]]、[[attachment_info]]、[[project_file_info]]、[[catg_id]]、[[busi_key]]、[[media_event_handling]]。

---END FILE---

---FILE: tables/attachment_info.md ---
---
type: table
title: 附件信息表
page_key: attachment_info
domain: 文件/附件/媒体
status: draft
aliases: [attachment_info, 表单附件表]
oid: 1
scope:
  databases: [unknown]
sources: ["code:AttachMentFacade/AttachmentInfoProvider（术语桥证据）"]
contract_version: "0.1"
---
attachment_info 是「附件」（[[attachment]]）的存储表，通过 AttachMentFacade/AttachmentInfoProvider 查询，用于表单模板附件；与影像树 [[media_file]]、项目文件 [[project_file_info]] 属于三套不同存储。

## 需求背景
本期语义分析未提供需求文档主张；本页业务定位来自术语桥证据。

## 版本演进
v0 初版：本表未获得字段级语义证据，故不产出 ground:table 锚点块（见 REVIEW）。

关联：[[attachment]]、[[media]]、[[project_file]]。

---END FILE---

---FILE: enums/CustBuildStatusEnum.md ---
---
type: enum
title: 企业建档状态枚举（CustBuildStatusEnum）
page_key: CustBuildStatusEnum
domain: 文件/附件/媒体
status: draft
aliases: [CustBuildStatusEnum, 建档状态]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:updateCustBuildStatus/getCustBuildStatus/messageNotify"]
contract_version: "0.1"
---
CustBuildStatusEnum 是 [[cust_company_info]].cust_build_status 的取值来源，多处以 getDictKey() 落库更新；完整状态流转见过程页 [[cust_build_status]]，成功态口径见 [[cust_cert_success]]。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：枚举名与 BUILD_SUCCESS 取值证据来自 updateCustBuildStatus；其余取值的 java_name 按同枚举命名约定补齐（见 REVIEW）。

```ground:enum
enum: CustBuildStatusEnum
field: cust_company_info.cust_build_status
stored_as: getDictKey()
values:
  - value: INIT
    java_name: CustBuildStatusEnum.INIT
    label: 初始
    stored_as: getDictKey()
  - value: BUILD_FAIL
    java_name: CustBuildStatusEnum.BUILD_FAIL
    label: 建档失败/拒绝
    stored_as: getDictKey()
  - value: CUST_CONFIRM_AWAIT
    java_name: CustBuildStatusEnum.CUST_CONFIRM_AWAIT
    label: 待客户确认
    stored_as: getDictKey()
  - value: CUST_BUILDING
    java_name: CustBuildStatusEnum.CUST_BUILDING
    label: 客户提交/运营中台审核中
    stored_as: getDictKey()
  - value: BUILD_SUCCESS
    java_name: CustBuildStatusEnum.BUILD_SUCCESS
    label: 建档成功
    stored_as: getDictKey()
    note: updateCustBuildStatus 多处使用 getDictKey() 更新
  - value: AWAIT_CUST_CONFIRM
    java_name: CustBuildStatusEnum.AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    stored_as: getDictKey()
```

关联：[[cust_build_status]]、[[cust_cert_success]]、[[cust_company_info]]。

---END FILE---

---FILE: enums/CustCompanyTypeEnum.md ---
---
type: enum
title: 客户角色枚举（CustCompanyTypeEnum）
page_key: CustCompanyTypeEnum
domain: 文件/附件/媒体
status: draft
aliases: [CustCompanyTypeEnum, 企业角色]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany", "code:PlatFormMediaApplication.java:listCustMediaFile"]
contract_version: "0.1"
---
CustCompanyTypeEnum 同时服务两处字段：[[cust_company_info]].cust_company_type 以 JSON 数组字符串承载多角色，[[cust_person_info]].company_type 与 [[cust_role_info]].role_type 则存单个 dictKey。角色口径见 [[role_supplier]]、[[role_core]]、[[role_dealer]]、[[role_finance]]。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：SUPPLIER 取值与两种落库形态来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:enum
enum: CustCompanyTypeEnum
field: cust_company_info.cust_company_type
stored_as: JSON 数组字符串字面量（["SUPPLIER"]）
values:
  - value: SUPPLIER
    java_name: CustCompanyTypeEnum.SUPPLIER
    label: 供应商
    stored_as: JSON 数组字符串字面量（["SUPPLIER"]）
    note: 企业主表存 JSON 数组以支持多角色；cust_person_info.company_type 存单个 dictKey（getDictKey()）。
```

关联：[[cust_company_info]]、[[cust_person_info]]、[[cust_role_info]]、[[role_supplier]]。

---END FILE---

---FILE: enums/IDTypeEnum.md ---
---
type: enum
title: 证件类型枚举（IDTypeEnum）
page_key: IDTypeEnum
domain: 文件/附件/媒体
status: draft
aliases: [IDTypeEnum, 证件类型]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany"]
contract_version: "0.1"
---
IDTypeEnum 用于法人证件类型与联系人证件类型两处字段，以 .name() 落库、以 valueOf 反解。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：CRET_ID 取值与 .name() 落库方式来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:enum
enum: IDTypeEnum
field: cust_company_info.legal_certification_type
stored_as: name()
values:
  - value: CRET_ID
    java_name: IDTypeEnum.CRET_ID
    label: 身份证
    stored_as: name()
    note: 使用 .name() 落库，查询时 IDTypeEnum.valueOf(certType)；cust_person_info.certification_type 同样存 IDTypeEnum.name()。
```

关联：[[cust_company_info]]、[[cust_person_info]]。

---END FILE---

---FILE: enums/CustSourceEnum.md ---
---
type: enum
title: 建档数据来源枚举（CustSourceEnum）
page_key: CustSourceEnum
domain: 文件/附件/媒体
status: draft
aliases: [CustSourceEnum, 建档来源]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:isdo"]
contract_version: "0.1"
---
CustSourceEnum 标识建档数据来源，PLATFORM_PUSH 表示平台推送，并作为建档影像是否实时同步的判断条件（见 [[build_media_sync_condition]] 与口径 [[platform_push_source]]）。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：PLATFORM_PUSH 取值来自 CustMediaFacade.isdo 证据；无 action=uncovered 的文档主张。

```ground:enum
enum: CustSourceEnum
field: cust_company_info.cust_source
stored_as: getDictKey()
values:
  - value: PLATFORM_PUSH
    java_name: CustSourceEnum.PLATFORM_PUSH
    label: 平台推送
    stored_as: getDictKey()
    note: 用于判断影像同步是否实时处理。
```

关联：[[cust_company_info]]、[[platform_push_source]]、[[build_media_sync_condition]]。

---END FILE---

---FILE: enums/CustStatusEnum.md ---
---
type: enum
title: 客户状态枚举（CustStatusEnum）
page_key: CustStatusEnum
domain: 文件/附件/媒体
status: draft
aliases: [CustStatusEnum, 客户状态]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoDao.java:updateStatus"]
contract_version: "0.1"
---
CustStatusEnum 描述客户状态，与 [[CustBuildStatusEnum]] 配合使用。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：EFFECT 取值来自 CustCompanyInfoDao.updateStatus 证据；无 action=uncovered 的文档主张。

```ground:enum
enum: CustStatusEnum
field: cust_company_info.cust_status
stored_as: getDictKey()
values:
  - value: EFFECT
    java_name: CustStatusEnum.EFFECT
    label: 生效
    stored_as: getDictKey()
    note: 与 CustBuildStatusEnum 配合使用。
```

关联：[[cust_company_info]]、[[CustBuildStatusEnum]]。

---END FILE---

---FILE: enums/OpenStatus.md ---
---
type: enum
title: 开通状态枚举（OpenStatus）
page_key: OpenStatus
domain: 文件/附件/媒体
status: draft
aliases: [OpenStatus, 开通状态]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:submitForSimpleAuth"]
contract_version: "0.1"
---
OpenStatus 用于企业「是否开通电子签章」标志，语义上等同于 Y/N 开关。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：Y 取值来自 submitForSimpleAuth 证据；无 action=uncovered 的文档主张。

```ground:enum
enum: OpenStatus
field: cust_company_info.need_register_ca
stored_as: getDictKey()
values:
  - value: Y
    java_name: OpenStatus.Y
    label: 开通
    stored_as: getDictKey()
    note: 同时存在字面量 "Y" 比较。
```

关联：[[cust_company_info]]。

---END FILE---

---FILE: enums/UserTypeEnum.md ---
---
type: enum
title: 联系人类型枚举（UserTypeEnum）
page_key: UserTypeEnum
domain: 文件/附件/媒体
status: draft
aliases: [UserTypeEnum, 联系人类型]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:personInfoService.getOne", "code:CustCompanyInfoApplication.java"]
contract_version: "0.1"
---
UserTypeEnum 区分企业下的管理员与操作员。影像查询前置校验 [[cust_media_precheck]] 与按操作人过滤 [[catg_operator_filter]] 都以管理员（admin）联系人为基准，口径见 [[admin_person]]。

## 需求背景
本期语义分析未提供需求文档主张，取值来自代码枚举证据。

## 版本演进
v0 初版：admin 取值来自 personInfoService.getOne 查询条件（getDictKey()）；operator 取值来自 cust_person_info.user_type 字段语义证据，其 java_name 按同枚举命名约定补齐（见 REVIEW）。

```ground:enum
enum: UserTypeEnum
field: cust_person_info.user_type
stored_as: getDictKey()
values:
  - value: admin
    java_name: UserTypeEnum.admin
    label: 管理员
    stored_as: getDictKey()
    note: 查询条件使用 getDictKey()。
  - value: operator
    java_name: UserTypeEnum.operator
    label: 操作员
    stored_as: getDictKey()
    note: 取值与标签来自 cust_person_info.user_type 字段语义；java_name 为命名约定推定。
```

关联：[[cust_person_info]]、[[admin_person]]、[[catg_operator_filter]]。

---END FILE---

---FILE: enums/MediaEventType.md ---
---
type: enum
title: 影像事件类型（MediaEventType）
page_key: MediaEventType
domain: 文件/附件/媒体
status: draft
aliases: [MediaEventType, 影像事件类型]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:setDelOrUploadMedia", "code:MediaEventSyncProvider.java:onEvent"]
contract_version: "0.1"
---
MediaEventType 描述运营中台推送的影像事件类型，是影像事件处理规则 [[media_event_handling]] 的取值依据。

## 需求背景
本期语义分析未提供需求文档主张；事件类型取值来自代码证据。

## 版本演进
v0 初版：UPLOAD 取值来自 setDelOrUploadMedia 证据；DELETE、INFO_CHANGE 取值来自 MediaEventSyncProvider.onEvent 规则证据，其 java_name 按同枚举命名约定补齐（见 REVIEW）。

```ground:enum
enum: MediaEventType
field: PlatClientMediaEvent.eventType
stored_as: name()
values:
  - value: UPLOAD
    java_name: MediaEventType.UPLOAD
    label: 上传
    stored_as: name()
    note: setDelOrUploadMedia 中使用。
  - value: DELETE
    java_name: MediaEventType.DELETE
    label: 删除
    stored_as: name()
    note: 取值来自 MediaEventSyncProvider 处理 UPLOAD/DELETE/INFO_CHANGE 的规则证据。
  - value: INFO_CHANGE
    java_name: MediaEventType.INFO_CHANGE
    label: 信息变更
    stored_as: name()
    note: 取值来自 MediaEventSyncProvider 处理 UPLOAD/DELETE/INFO_CHANGE 的规则证据。
```

关联：[[media_event_handling]]、[[media_file]]、[[cust_change_record]]。

---END FILE---

---FILE: processes/cust_build_status.md ---
---
type: process
title: 企业建档状态流转
page_key: cust_build_status
domain: 文件/附件/媒体
status: draft
aliases: [建档状态机, 企业建档流程]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:getCustBuildStatus", "code:CustCompanyInfoApplication.java:messageNotify"]
contract_version: "0.1"
---
企业建档状态机描述 [[cust_company_info]].cust_build_status 的取值与流转，取值定义见 [[CustBuildStatusEnum]]，成功态口径见 [[cust_cert_success]]。流转由提交、客户提交与运营中台审核结果消息（messageNotify）驱动。建档/变更过程中的影像同步时机取决于来源是否为 [[CustSourceEnum]].PLATFORM_PUSH，见 [[build_media_sync_condition]]。

## 需求背景
本期语义分析未提供需求文档主张；状态与事件来自代码证据。

## 版本演进
v0 初版：状态集合与 7 条流转均来自 getCustBuildStatus / messageNotify 证据；无 action=uncovered 的文档主张。

```ground:process
name: 企业建档状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败/拒绝
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户提交/运营中台审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    source: code_enum
transitions:
  - from: INIT
    event: submit
    to: CUST_CONFIRM_AWAIT
    evidence: CustCompanyInfoApplication.java:getCustBuildStatus
  - from: INIT
    event: submit(INVITE_AGW)
    to: CUST_BUILDING
    evidence: CustCompanyInfoApplication.java:getCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交
    to: CUST_BUILDING
    evidence: CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: CustCompanyInfoApplication.java:messageNotify
  - from: BUILD_FAIL
    event: 重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: CustCompanyInfoApplication.java:messageNotify
```

关联：[[cust_company_info]]、[[CustBuildStatusEnum]]、[[cust_cert_success]]、[[build_media_sync_condition]]。

---END FILE---

---FILE: concepts/media.md ---
---
type: concept
title: 影像
page_key: media
domain: 文件/附件/媒体
status: draft
aliases: [media, 客户影像, 影像文件]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:影像", "code:MediaFacade/CustMediaFacade/IMediaOperaProvider"]
contract_version: "0.1"
maps_to: media_file
adjudication: synonym
field_targets: [media_file.catg_id, media_file.busi_key, media_file.user_busi_key]
also_confused_with: [附件, 项目文件]
---
影像指通过 MediaFacade/CustMediaFacade 管理的客户文件，底层由 IMediaOperaProvider 维护，分类使用 catgId（[[catg_id]]），业务归属用 busiKey（[[busi_key]]）。影像与 [[attachment]]、[[project_file]] 是三套不同存储，容易混淆，判据见下。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立「影像」为 media_file 的同义词，并与附件、项目文件做边界切分；无 action=uncovered 的文档主张。

边界：影像走 MediaFacade/CustMediaFacade + IMediaOperaProvider，分类用 catgId；附件走 AttachMentFacade/AttachmentInfoProvider；项目文件是 [[project_file_info]] 的元数据记录。

关联：[[media_file]]、[[attachment]]、[[project_file]]、[[catg_id]]、[[busi_key]]。

---END FILE---

---FILE: concepts/attachment.md ---
---
type: concept
title: 附件
page_key: attachment
domain: 文件/附件/媒体
status: draft
aliases: [attachment, 附件信息]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:附件", "code:AttachMentFacade/AttachmentInfoProvider"]
contract_version: "0.1"
maps_to: attachment_info
adjudication: boundary
field_targets: []
also_confused_with: [影像, 项目文件]
---
附件通过 AttachMentFacade/AttachmentInfoProvider 查询，用于表单模板附件；与影像树（[[media]]）、项目文件（[[project_file]]）不是同一套存储。本概念以边界判定为主，不建立同义关系。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立附件＝attachment_info 的边界判定；本期未获得附件字段级证据，故 frontmatter 未列 field_targets；无 action=uncovered 的文档主张。

关联：[[attachment_info]]、[[media]]、[[project_file]]。

---END FILE---

---FILE: concepts/project_file.md ---
---
type: concept
title: 项目文件
page_key: project_file
domain: 文件/附件/媒体
status: draft
aliases: [project file, 项目运营文件]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:项目文件", "code:ProjectFileController.java:buildQueryWrapper"]
contract_version: "0.1"
maps_to: project_file_info
adjudication: boundary
field_targets: [project_file_info.project_id, project_file_info.file_type, project_file_info.update_time]
also_confused_with: [影像, 附件]
---
项目文件指 [[project_file_info]] 中登记的项目运营文件元数据（标题、描述、类型、关联项目ID），文件实体仍在对象存储；按 [[project_file_info]].file_type 分五类，口径见 [[project_file_type_cust]]、[[project_file_type_approve]]、[[project_file_type_check]]、[[project_file_type_collate]]、[[project_file_type_other]]。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立项目文件＝project_file_info 的边界判定，与影像树、附件区分；无 action=uncovered 的文档主张。

关联：[[project_file_info]]、[[media]]、[[attachment]]、[[project_file_page_query]]。

---END FILE---

---FILE: concepts/catg_id.md ---
---
type: concept
title: catgId（影像分类）
page_key: catg_id
domain: 文件/附件/媒体
status: draft
aliases: [分类ID, 影像分类]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:catgId", "code:MediaFacade.java:getMediaCategoryDisplayName", "code:CustMediaFacade.java:uploadElectronicAuthMediaFile"]
contract_version: "0.1"
maps_to: media_file.catg_id
adjudication: boundary
field_targets: [media_file.catg_id]
also_confused_with: [fileType]
---
catgId 是影像分类编码（如 A0004 授权书、A0007 法人证件等），落在 [[media_file]].catg_id 上；按操作人过滤、分类名回退等规则都以此为键，口径见 [[media_catg_a0004]]、[[media_catg_a0049]]、[[media_catg_a0050]]。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立 catgId 与 fileType 的边界（前者影像分类编码，后者为 [[project_file_info]].file_type 的文件模块类型）；无 action=uncovered 的文档主张。

关联：[[media_file]]、[[media]]、[[catg_operator_filter]]、[[media_category_name_fallback]]。

---END FILE---

---FILE: concepts/busi_key.md ---
---
type: concept
title: busiKey（影像业务键）
page_key: busi_key
domain: 文件/附件/媒体
status: draft
aliases: [业务键, 业务KEY]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:busiKey", "code:ProjectMediaFacade.java:uploadProjectConfigFiles", "code:CustMediaFacade.java:hasAuthorizationAgreementMedia"]
contract_version: "0.1"
maps_to: media_file.busi_key
adjudication: boundary
field_targets: [media_file.busi_key, media_file.user_busi_key]
also_confused_with: [userBusiKey]
---
busiKey 通常为企业 id 或运营中台客户 id，用于按业务对象组织影像；userBusiKey 为联系人 id，用于区分操作人影像，二者是不同粒度的业务键，勿混用。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立 busiKey 与 userBusiKey 的边界；无 action=uncovered 的文档主张。

关联：[[media_file]]、[[media]]、[[catg_operator_filter]]、[[company_auth_media_existence]]。

---END FILE---

---FILE: calibers/project_file_type_cust.md ---
---
type: caliber
title: 项目文件类型-客户
page_key: project_file_type_cust
domain: 文件/附件/媒体
status: draft
aliases: [file_type=cust]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info.file_type"]
contract_version: "0.1"
---
「客户」类项目运营文件口径，用于项目文件列表的精确筛选。

## 需求背景
本期语义分析未提供需求文档主张；口径来自库表取值证据。

## 版本演进
v0 初版：口径来自 project_file_info.file_type 取值证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 项目文件类型-客户
predicate: project_file_info.file_type = 'cust'
scope: 项目运营文件管理
evidence: db
```

关联：[[project_file_info]]、[[project_file]]、[[project_file_page_query]]。

---END FILE---

---FILE: calibers/project_file_type_approve.md ---
---
type: caliber
title: 项目文件类型-审批
page_key: project_file_type_approve
domain: 文件/附件/媒体
status: draft
aliases: [file_type=approve]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info.file_type"]
contract_version: "0.1"
---
「审批」类项目运营文件口径，用于项目文件列表的精确筛选。

## 需求背景
本期语义分析未提供需求文档主张；口径来自库表取值证据。

## 版本演进
v0 初版：口径来自 project_file_info.file_type 取值证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 项目文件类型-审批
predicate: project_file_info.file_type = 'approve'
scope: 项目运营文件管理
evidence: db
```

关联：[[project_file_info]]、[[project_file]]、[[project_file_page_query]]。

---END FILE---

---FILE: calibers/project_file_type_check.md ---
---
type: caliber
title: 项目文件类型-审核
page_key: project_file_type_check
domain: 文件/附件/媒体
status: draft
aliases: [file_type=check]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info.file_type"]
contract_version: "0.1"
---
「审核」类项目运营文件口径，用于项目文件列表的精确筛选。

## 需求背景
本期语义分析未提供需求文档主张；口径来自库表取值证据。

## 版本演进
v0 初版：口径来自 project_file_info.file_type 取值证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 项目文件类型-审核
predicate: project_file_info.file_type = 'check'
scope: 项目运营文件管理
evidence: db
```

关联：[[project_file_info]]、[[project_file]]、[[project_file_page_query]]。

---END FILE---

---FILE: calibers/project_file_type_collate.md ---
---
type: caliber
title: 项目文件类型-整理
page_key: project_file_type_collate
domain: 文件/附件/媒体
status: draft
aliases: [file_type=collate]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info.file_type"]
contract_version: "0.1"
---
「整理」类项目运营文件口径，用于项目文件列表的精确筛选。

## 需求背景
本期语义分析未提供需求文档主张；口径来自库表取值证据。

## 版本演进
v0 初版：口径来自 project_file_info.file_type 取值证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 项目文件类型-整理
predicate: project_file_info.file_type = 'collate'
scope: 项目运营文件管理
evidence: db
```

关联：[[project_file_info]]、[[project_file]]、[[project_file_page_query]]。

---END FILE---

---FILE: calibers/project_file_type_other.md ---
---
type: caliber
title: 项目文件类型-其他
page_key: project_file_type_other
domain: 文件/附件/媒体
status: draft
aliases: [file_type=other]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info.file_type"]
contract_version: "0.1"
---
「其他」类项目运营文件口径，用于项目文件列表的精确筛选。

## 需求背景
本期语义分析未提供需求文档主张；口径来自库表取值证据。

## 版本演进
v0 初版：口径来自 project_file_info.file_type 取值证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 项目文件类型-其他
predicate: project_file_info.file_type = 'other'
scope: 项目运营文件管理
evidence: db
```

关联：[[project_file_info]]、[[project_file]]、[[project_file_page_query]]。

---END FILE---

---FILE: calibers/cust_cert_success.md ---
---
type: caliber
title: 客户认证成功
page_key: cust_cert_success
domain: 文件/附件/媒体
status: draft
aliases: [建档成功口径]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:updateCustBuildStatus"]
contract_version: "0.1"
---
判定企业已完成认证/建档的口径，是 [[cust_build_status]] 状态机的终态之一。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 updateCustBuildStatus 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 客户认证成功
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
scope: 企业建档
evidence: code
```

关联：[[cust_company_info]]、[[CustBuildStatusEnum]]、[[cust_build_status]]。

---END FILE---

---FILE: calibers/platform_push_source.md ---
---
type: caliber
title: 平台推送来源
page_key: platform_push_source
domain: 文件/附件/媒体
status: draft
aliases: [PLATFORM_PUSH 口径]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:isdo"]
contract_version: "0.1"
---
判定建档数据来自运营中台推送的口径，直接影响影像是否实时同步，见 [[build_media_sync_condition]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 CustMediaFacade.isdo 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 平台推送来源
predicate: cust_company_info.cust_source = 'PLATFORM_PUSH'
scope: 企业建档
evidence: code
```

关联：[[cust_company_info]]、[[CustSourceEnum]]、[[build_media_sync_condition]]。

---END FILE---

---FILE: calibers/admin_person.md ---
---
type: caliber
title: 管理员联系人
page_key: admin_person
domain: 文件/附件/媒体
status: draft
aliases: [user_type=admin]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:personInfoService.getOne"]
contract_version: "0.1"
---
判定企业下管理员联系人的口径，是影像查询与按操作人过滤的前置条件，见 [[cust_media_precheck]]、[[catg_operator_filter]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 personInfoService.getOne 查询条件证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 管理员联系人
predicate: cust_person_info.user_type = 'admin'
scope: 客户联系人
evidence: code
```

关联：[[cust_person_info]]、[[UserTypeEnum]]、[[cust_media_precheck]]。

---END FILE---

---FILE: calibers/role_supplier.md ---
---
type: caliber
title: 供应商角色
page_key: role_supplier
domain: 文件/附件/媒体
status: draft
aliases: [company_type=SUPPLIER]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany"]
contract_version: "0.1"
---
供应商角色口径，落在联系人的单个角色字段上；企业主表以 JSON 数组承载多角色，见 [[CustCompanyTypeEnum]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 供应商角色
predicate: cust_person_info.company_type = 'SUPPLIER'
scope: 客户角色
evidence: code
```

关联：[[cust_person_info]]、[[cust_role_info]]、[[CustCompanyTypeEnum]]。

---END FILE---

---FILE: calibers/role_core.md ---
---
type: caliber
title: 核心企业角色
page_key: role_core
domain: 文件/附件/媒体
status: draft
aliases: [company_type=CORE]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany"]
contract_version: "0.1"
---
核心企业角色口径，落在联系人的单个角色字段上。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 核心企业角色
predicate: cust_person_info.company_type = 'CORE'
scope: 客户角色
evidence: code
```

关联：[[cust_person_info]]、[[cust_role_info]]、[[CustCompanyTypeEnum]]。

---END FILE---

---FILE: calibers/role_dealer.md ---
---
type: caliber
title: 经销商角色
page_key: role_dealer
domain: 文件/附件/媒体
status: draft
aliases: [company_type=DEALER]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany"]
contract_version: "0.1"
---
经销商角色口径，落在联系人的单个角色字段上。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 经销商角色
predicate: cust_person_info.company_type = 'DEALER'
scope: 客户角色
evidence: code
```

关联：[[cust_person_info]]、[[cust_role_info]]、[[CustCompanyTypeEnum]]。

---END FILE---

---FILE: calibers/role_finance.md ---
---
type: caliber
title: 金融机构角色
page_key: role_finance
domain: 文件/附件/媒体
status: draft
aliases: [company_type=FINANCE]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany"]
contract_version: "0.1"
---
金融机构角色口径，落在联系人的单个角色字段上。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 金融机构角色
predicate: cust_person_info.company_type = 'FINANCE'
scope: 客户角色
evidence: code
```

关联：[[cust_person_info]]、[[cust_role_info]]、[[CustCompanyTypeEnum]]。

---END FILE---

---FILE: calibers/media_catg_a0004.md ---
---
type: caliber
title: 授权书影像分类
page_key: media_catg_a0004
domain: 文件/附件/媒体
status: draft
aliases: [catgId=A0004, 授权书分类]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:hasAuthorizationAgreementMedia", "code:PlatFormMediaApplication.java:lookupCustMedia"]
contract_version: "0.1"
---
影像树中企业授权书分类口径。该分类受按操作人过滤规则 [[catg_operator_filter]] 约束，并用于授权书存在性判断 [[company_auth_media_existence]]；规则 [[electronic_auth_incremental_upload]] 明确禁止向本分类写入电子授权书。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 lookupCustMedia、hasAuthorizationAgreementMedia 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 授权书影像分类
predicate: media_file.catg_id = 'A0004'
scope: 影像树
evidence: code
```

关联：[[media_file]]、[[catg_id]]、[[company_auth_media_existence]]、[[catg_operator_filter]]。

---END FILE---

---FILE: calibers/media_catg_a0049.md ---
---
type: caliber
title: CA升级授权书分类
page_key: media_catg_a0049
domain: 文件/附件/媒体
status: draft
aliases: [catgId=A0049, CA升级授权书]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadCaUpgradeAuthMediaFile"]
contract_version: "0.1"
---
影像树中 CA 升级授权书分类口径，上传遵循双端上传规则 [[dual_side_media_upload]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 uploadCaUpgradeAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: CA升级授权书分类
predicate: media_file.catg_id = 'A0049'
scope: 影像树
evidence: code
```

关联：[[media_file]]、[[catg_id]]、[[dual_side_media_upload]]。

---END FILE---

---FILE: calibers/media_catg_a0050.md ---
---
type: caliber
title: 电子授权书分类
page_key: media_catg_a0050
domain: 文件/附件/媒体
status: draft
aliases: [catgId=A0050, 电子授权书]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadElectronicAuthMediaFile"]
contract_version: "0.1"
---
影像树中电子授权书分类口径，仅新增不删除，规则见 [[electronic_auth_incremental_upload]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 uploadElectronicAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 电子授权书分类
predicate: media_file.catg_id = 'A0050'
scope: 影像树
evidence: code
```

关联：[[media_file]]、[[catg_id]]、[[electronic_auth_incremental_upload]]。

---END FILE---

---FILE: rules/cust_media_precheck.md ---
---
type: rule
title: 客户影像查询前置校验
page_key: cust_media_precheck
domain: 文件/附件/媒体
status: draft
aliases: [影像查询前置校验]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:listCustMediaFile"]
contract_version: "0.1"
---
查询客户影像（[[media]]）时必须传 companyType；随后按 pplatCustId 查企业，再查管理员联系人与角色记录，任一不存在即抛异常。该规则以 [[cust_company_info]]、[[cust_person_info]]、[[cust_role_info]] 三张表为判定依据。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 listCustMediaFile 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 客户影像查询前置校验
content: 查询客户影像时必须传 companyType；根据 pplatCustId 查企业，再查管理员联系人和角色记录，任一不存在抛异常。
impact: 阻止无角色或管理员的企业查询影像
field_targets: [cust_company_info.id, cust_person_info.user_type, cust_role_info.role_type]
evidence: PlatFormMediaApplication.java:listCustMediaFile
```

关联：[[media]]、[[admin_person]]、[[cust_company_info]]、[[cust_person_info]]、[[cust_role_info]]。

---END FILE---

---FILE: rules/catg_operator_filter.md ---
---
type: rule
title: 特定分类按操作人过滤
page_key: catg_operator_filter
domain: 文件/附件/媒体
status: draft
aliases: [按操作人过滤影像]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:lookupCustMedia"]
contract_version: "0.1"
---
查询影像时，对 A0004/A0011/A0012 分类的文件只保留 userBusiKey 等于当前管理员 id 的记录，确保授权书与操作人证件只返回当前操作人的影像。涉及分类口径 [[media_catg_a0004]] 与业务键 [[busi_key]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 lookupCustMedia 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 特定分类按操作人过滤
content: 查询影像时，对 A0004/A0011/A0012 分类的文件，只保留 userBusiKey 等于当前管理员 id 的记录。
impact: 确保授权书/操作人证件只返回当前操作人的影像
field_targets: [media_file.catg_id, media_file.user_busi_key]
evidence: PlatFormMediaApplication.java:lookupCustMedia
```

关联：[[media_file]]、[[catg_id]]、[[busi_key]]、[[admin_person]]、[[media_catg_a0004]]。

---END FILE---

---FILE: rules/project_config_overwrite_upload.md ---
---
type: rule
title: 项目配置文件覆盖上传
page_key: project_config_overwrite_upload
domain: 文件/附件/媒体
status: draft
aliases: [项目配置影像覆盖]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectMediaFacade.java:uploadProjectConfigFiles"]
contract_version: "0.1"
---
上传项目配置文件到影像树前，先删除该 projectApprovalId 下 PROJECT_CONFIG 分类的所有影像，再写入新文件，保证同项目重复推送时配置目录不残留旧文件。与「只增不删」的 [[electronic_auth_incremental_upload]] 形成对照。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 uploadProjectConfigFiles 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 项目配置文件覆盖上传
content: 上传项目配置文件到影像树前，先删除该 projectApprovalId 下 PROJECT_CONFIG 分类的所有影像，再写入新文件。
impact: 保证同项目重复推送时配置目录不残留旧文件
field_targets: [media_file.busi_key, media_file.catg_id]
evidence: ProjectMediaFacade.java:uploadProjectConfigFiles
```

关联：[[media_file]]、[[busi_key]]、[[catg_id]]、[[electronic_auth_incremental_upload]]。

---END FILE---

---FILE: rules/electronic_auth_incremental_upload.md ---
---
type: rule
title: 电子授权书增量上传
page_key: electronic_auth_incremental_upload
domain: 文件/附件/媒体
status: draft
aliases: [电子授权书仅新增]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadElectronicAuthMediaFile"]
contract_version: "0.1"
---
A0050 电子授权书仅新增不删除，禁止写入 A0004，禁止调用 deleteFileByCatgId；同一流程已存在时跳过，从而保证幂等并避免覆盖历史授权书。相关分类口径见 [[media_catg_a0050]]、[[media_catg_a0004]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 uploadElectronicAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 电子授权书增量上传
content: A0050 电子授权书仅新增不删除，禁止写入 A0004，禁止调用 deleteFileByCatgId；同流程已存在时跳过。
impact: 避免覆盖历史授权书，保证幂等
field_targets: [media_file.catg_id, media_file.specify_file_name]
evidence: CustMediaFacade.java:uploadElectronicAuthMediaFile
```

关联：[[media_catg_a0050]]、[[media_catg_a0004]]、[[media_file]]、[[dual_side_media_upload]]。

---END FILE---

---FILE: rules/dual_side_media_upload.md ---
---
type: rule
title: 双端影像上传
page_key: dual_side_media_upload
domain: 文件/附件/媒体
status: draft
aliases: [运营中台与产融双写]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadCustContractFile/uploadCaUpgradeAuthMediaFile/uploadElectronicAuthMediaFile"]
contract_version: "0.1"
---
上传授权书、CA 升级授权书、电子授权书时先上传运营中台，再上传产融影像树，保证两端影像数据一致。分类口径见 [[media_catg_a0004]]、[[media_catg_a0049]]、[[media_catg_a0050]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 uploadCustContractFile / uploadCaUpgradeAuthMediaFile / uploadElectronicAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 双端影像上传
content: 上传授权书/CA升级授权书/电子授权书时，先上传运营中台，再上传产融影像树。
impact: 保证运营中台与产融影像数据一致
field_targets: [media_file.busi_key, media_file.catg_id]
evidence: CustMediaFacade.java:uploadCustContractFile/uploadCaUpgradeAuthMediaFile/uploadElectronicAuthMediaFile
```

关联：[[media_file]]、[[busi_key]]、[[catg_id]]、[[media_catg_a0049]]、[[media_catg_a0050]]。

---END FILE---

---FILE: rules/build_media_sync_condition.md ---
---
type: rule
title: 建档影像同步条件
page_key: build_media_sync_condition
domain: 文件/附件/媒体
status: draft
aliases: [影像同步条件]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:isdo/doDel/doUpload"]
contract_version: "0.1"
---
运营中台回调影像事件时，仅当企业存在且非变更流程（或来源非 PLATFORM_PUSH）才处理；变更影像在审核通过后统一拉取，避免变更过程中实时同步导致数据不一致。来源判定口径见 [[platform_push_source]]，状态流转见 [[cust_build_status]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 isdo/doDel/doUpload 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 建档影像同步条件
content: 运营中台回调影像事件时，仅当企业存在且非变更流程（或来源非 PLATFORM_PUSH）才处理；变更影像在审核通过后统一拉取。
impact: 避免变更流程中实时同步影像导致数据不一致
field_targets: [cust_company_info.cust_source, cust_change_record.oper_cust_id]
evidence: CustMediaFacade.java:isdo/doDel/doUpload
```

关联：[[cust_company_info]]、[[cust_change_record]]、[[platform_push_source]]、[[cust_build_status]]。

---END FILE---

---FILE: rules/media_event_handling.md ---
---
type: rule
title: 影像事件处理
page_key: media_event_handling
domain: 文件/附件/媒体
status: draft
aliases: [MediaEventSyncProvider 事件处理]
oid: 1
scope:
  databases: [unknown]
sources: ["code:MediaEventSyncProvider.java:onEvent"]
contract_version: "0.1"
---
MediaEventSyncProvider 只处理 CUST 类型事件的 UPLOAD/DELETE/INFO_CHANGE（见 [[MediaEventType]]），ASSET 类型仅打日志，从而区分客户影像与资产影像的同步。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 MediaEventSyncProvider.onEvent 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 影像事件处理
content: MediaEventSyncProvider 处理 CUST 类型的 UPLOAD/DELETE/INFO_CHANGE；ASSET 类型仅日志。
impact: 区分客户影像与资产影像同步
field_targets: [PlatClientMediaEvent.busiType, PlatClientMediaEvent.eventType]
evidence: MediaEventSyncProvider.java:onEvent
```

关联：[[MediaEventType]]、[[media_file]]、[[build_media_sync_condition]]。

---END FILE---

---FILE: rules/project_file_page_query.md ---
---
type: rule
title: 项目文件分页查询
page_key: project_file_page_query
domain: 文件/附件/媒体
status: draft
aliases: [项目文件列表查询]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectFileController.java:buildQueryWrapper"]
contract_version: "0.1"
---
按 projectId、fileType 精确查询，title/content 模糊查询，按 updateTime 倒序，支撑项目运营文件列表页（[[project_file]]）。涉及类型口径见 [[project_file_type_cust]] 等五个文件类型口径。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 buildQueryWrapper 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 项目文件分页查询
content: 按 projectId、fileType 精确查询，title/content 模糊查询，按 updateTime 倒序。
impact: 支撑项目运营文件列表页
field_targets: [project_file_info.project_id, project_file_info.file_type, project_file_info.update_time]
evidence: ProjectFileController.java:buildQueryWrapper
```

关联：[[project_file_info]]、[[project_file]]、[[tenant_project]]。

---END FILE---

---FILE: rules/media_download_url.md ---
---
type: rule
title: 影像下载URL生成
page_key: media_download_url
domain: 文件/附件/媒体
status: draft
aliases: [影像URL生成]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ClientMediaSyncService.java:setInvokeArg/getRelativePath"]
contract_version: "0.1"
---
同步影像到第三方时，对相对路径生成 COS 下载 URL；若 path 含 `?` 则截取并去掉 COS host，保证第三方可下载影像。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 setInvokeArg / getRelativePath 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 影像下载URL生成
content: 同步影像到第三方时，对相对路径生成 COS 下载 URL；若 path 含 ? 则截取并去掉 COS host。
impact: 保证第三方能通过 URL 下载影像
field_targets: [media_file.path, PlatFormMediaFileDTO.file_url]
evidence: ClientMediaSyncService.java:setInvokeArg/getRelativePath
```

关联：[[media_file]]、[[media]]。

---END FILE---

---FILE: rules/media_category_name_fallback.md ---
---
type: rule
title: 影像分类名称回退
page_key: media_category_name_fallback
domain: 文件/附件/媒体
status: draft
aliases: [分类名称回退]
oid: 1
scope:
  databases: [unknown]
sources: ["code:MediaFacade.java:getMediaCategoryDisplayName"]
contract_version: "0.1"
---
获取影像分类中文名失败或为空时回退返回 catgId 本身（[[catg_id]]），保证打包下载时目录名不丢失。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 getMediaCategoryDisplayName 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 影像分类名称回退
content: 获取影像分类中文名失败或为空时，回退返回 catgId 本身。
impact: 保证打包下载时目录名不因分类查询失败而丢失
field_targets: [media_file.catg_id]
evidence: MediaFacade.java:getMediaCategoryDisplayName
```

关联：[[media_file]]、[[catg_id]]、[[project_approval_zip_download]]。

---END FILE---

---FILE: rules/project_approval_zip_download.md ---
---
type: rule
title: 项目上线审批打包下载
page_key: project_approval_zip_download
domain: 文件/附件/媒体
status: draft
aliases: [上线审批附件下载]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectMediaFacade.java:streamApprovalMediaZip/resolveApprovalZipFileName"]
contract_version: "0.1"
---
流式将 MA003 影像树写入 zip，按分类目录组织，重名文件加序号，zip 命名为「项目名称+上线审批+yyyymmdd.zip」，支持审批附件一键下载。目录命名依赖 [[media_category_name_fallback]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 streamApprovalMediaZip / resolveApprovalZipFileName 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 项目上线审批打包下载
content: 流式将 MA003 影像树写入 zip，按分类目录组织，重名文件加序号，zip 命名“项目名称+上线审批+yyyymmdd.zip”。
impact: 支持审批附件一键下载
field_targets: [media_file.busi_key, media_file.catg_id]
evidence: ProjectMediaFacade.java:streamApprovalMediaZip/resolveApprovalZipFileName
```

关联：[[media_file]]、[[busi_key]]、[[catg_id]]、[[media_category_name_fallback]]。

---END FILE---

---FILE: rules/company_auth_media_existence.md ---
---
type: rule
title: 企业授权书存在性判断
page_key: company_auth_media_existence
domain: 文件/附件/媒体
status: draft
aliases: [授权书存在性判断]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:hasAuthorizationAgreementMedia"]
contract_version: "0.1"
---
检查 A0004 分类下是否存在指定 companyId/personId 的影像，用于判断企业授权书是否已上传。分类口径见 [[media_catg_a0004]]，业务键见 [[busi_key]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 hasAuthorizationAgreementMedia 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 企业授权书存在性判断
content: 检查 A0004 分类下是否有指定 companyId/personId 的影像。
impact: 用于判断是否已上传企业授权书
field_targets: [media_file.catg_id, media_file.busi_key, media_file.user_busi_key]
evidence: CustMediaFacade.java:hasAuthorizationAgreementMedia
```

关联：[[media_catg_a0004]]、[[media_file]]、[[busi_key]]、[[catg_id]]。

---END FILE---

---REVIEW: table | media_file 字段级证据缺失---
语义分析中 media_file 只作为术语桥 maps_to 与规则 field_targets 出现，未提供字段类型、含义与取值来源，因此本页未产出 ground:table 锚点块。请补充 media_file 的库表字段清单（catg_id、busi_key、user_busi_key、path、specify_file_name 及其它列）后补齐。
---END REVIEW---

---REVIEW: table | attachment_info 字段级证据缺失---
语义分析中 attachment_info 仅由术语桥「附件」指向，未提供任何字段证据，本页仅保留边界说明；待补充库表字段后补齐 ground:table。
---END REVIEW---

---REVIEW: table | 物理库名未在语义分析中给出---
所有表页 frontmatter 的 scope.databases 暂填 `unknown`：语义分析仅提供字段语义与代码证据，未给出物理库名（分析中出现的是 db_tenant_code/app_tenant_code 等租户列）。请确认物理库名后批量回填。
---END REVIEW---

---REVIEW: enum | 枚举 java_name 命名约定推定---
以下取值的 java_name 未在证据中逐字出现，按同枚举命名约定推定，需以写值点/枚举类源码复核：CustBuildStatusEnum 除 BUILD_SUCCESS 外的状态、UserTypeEnum.operator、MediaEventType.DELETE/INFO_CHANGE。
---END REVIEW---