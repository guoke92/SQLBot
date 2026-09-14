---FILE: tables/cust_change_record.md ---
---
type: table
title: 企业变更记录表 (cust_change_record)
page_key: cust_change_record
domain: 企业变更与运营变更
status: draft
aliases: [企业变更记录, 变更记录, cust_change_record]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - code:CustChangeApplication.java
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

`cust_change_record` 是企业客户「一次变更申请」的流程实例表：企业客户（或运营方代客）发起变更时落一条记录，承载本次变更的变更项集合、审核状态、以及运营中台回传的客户侧信息。它是 [[cust_change_cfg]]（变更项配置）与 [[cust_company_info]]（企业主体）之间的业务过程对象，流程状态见 [[cust_change_record_status]]，与 [[cust_oper_change_record]]（运营人员归属变更）是完全不同的两类「变更」，见 [[customer_change]]。

关键区分：`cust_id` 是本平台侧企业主键（[[cust_id]]），`oper_cust_id` 是运营中台侧客户 ID，两者不可混用；`alter_type_id` 是逗号分隔的配置主键列表，与字典编码 `item_code`（[[change_item_code]]）不是同一物；`alter_data` 是编码的 JSON 快照。

## 需求背景

企业信息变更需要同时满足两端的诉求：平台侧要能按变更项维度展示、审核与追踪，运营中台侧要能接收同一次变更并回传审核结果。因此本表以「一条记录 = 一次变更流程」建模，用 `status` 承载审核流转，用 `oper_cust_info` 承载中台返回的变更前后对照信息（[[before_after_comparison]]），用 `need_cust_confirm`/`msg_send`/`*_auth` 承载客户确认、通知与授权材料标记。

## 版本演进

v0.1：首次从语义分析抽取字段口径，字段含义与字典来源以锚点块为准；本页暂无历史版本差异记录。

```ground:table
table: cust_change_record
fields:
  - name: status
    type: varchar
    desc: "变更记录审核状态，取值来自 OperApiConstants.CheckStatus 常量（以 name() 落库）；DB 默认 '1' 为历史初始值"
    dict: OperApiConstants.CheckStatus
  - name: alter_mode
    type: varchar
    desc: "变更方式：1=平台变更(PLAT_ALTER)，2=企业自行变更(SELF_ALTER)，AlterModeEnum.getDictKey 落库"
    dict: AlterModeEnum
  - name: alter_type_id
    type: varchar
    desc: "本次变更所选变更项在 cust_change_cfg.id 上的逗号分隔主键列表（非单一外键）"
    dict: null
  - name: alter_data
    type: text
    desc: "变更项编码(item_code)的 JSON 数组快照"
    dict: null
  - name: alter_type
    type: varchar
    desc: "变更类型文本描述"
    dict: null
  - name: cust_id
    type: bigint
    desc: "发起变更的平台企业主键，对应 cust_company_info.id（非 code）"
    dict: null
  - name: cust_type
    type: varchar
    desc: "客户类型：1个人客户/2企业客户/3运营方企业客户/4企业客户(全部)"
    dict: null
  - name: cust_company_type
    type: varchar
    desc: "客户企业角色（CORE/SUPPLIER/FINANCE/DEALER/...）"
    dict: null
  - name: oper_cust_id
    type: varchar
    desc: "运营中台侧客户ID（外部系统ID，不能与本平台 cust_id 混用）"
    dict: null
  - name: oper_cust_info
    type: text
    desc: "运营中台返回的客户信息 JSON，其中 personId=变更后管理员、oldPersonId=变更前管理员"
    dict: null
  - name: oper_channel
    type: varchar
    desc: "运营中台变更渠道标识（DIRECT_INIT / operation-pplatform-common-new / operation-pplatform-not-edit-new）"
    dict: null
  - name: need_cust_confirm
    type: char(1)
    desc: "是否需要客户确认 Y/N"
    dict: null
  - name: electronic_auth_sign_status
    type: varchar
    desc: "电子授权书签署状态（PENDING/SIGNED）"
    dict: null
  - name: need_resign_auth
    type: char(1)
    desc: "是否需要重签授权书 Y/N（直推识别变更项时写入，后续只读）"
    dict: null
  - name: msg_send
    type: char(1)
    desc: "变更结果通知是否已发送 Y/N"
    dict: null
  - name: admin_auth
    type: char(1)
    desc: "企业管理授权材料标记 Y/N"
    dict: null
  - name: legal_auth
    type: char(1)
    desc: "法人代表授权材料标记 Y/N"
    dict: null
  - name: enable
    type: char(1)
    desc: "逻辑有效标记，实测仅 Y"
    dict: null
```

相关页面：[[change_status]]、[[alter_mode]]、[[change_item_code]]、[[cust_id]]、[[change_rebuild]]、[[valid_change_record]]、[[company_in_change]]。

---REVIEW: table | 企业变更记录表 (cust_change_record)---
1) `scope.databases` 无事实来源：语义分析未给出物理库名，本页暂填 `unknown`，需由维护者补全。2) 锚点块 `type` 列无 DDL 证据，为按语义（Y/N 标记、逗号列表、JSON 快照）推断，待 DDL 校准。3) `status` 的 DB 分布值 `'1'` 在代码常量 `OperApiConstants.CheckStatus` 中无对应状态，属历史默认值，语义未声明，见 [[cust_change_record_status]] 的 REVIEW。
---END REVIEW---

---END FILE---

---FILE: tables/cust_change_cfg.md ---
---
type: table
title: 客户变更项配置表 (cust_change_cfg)
page_key: cust_change_cfg
domain: 企业变更与运营变更
status: draft
aliases: [变更项配置, 变更项字典, cust_change_cfg]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_cfg
  - code:CustChangeApplication.java
contract_version: "0.1"
---

`cust_change_cfg` 是变更项的配置字典：每一行是一个「可变更项」，用 `item_code`（UN0001~UN0016）标识，同时携带平台侧展示名 `plat_item` 与运营中台侧名称 `oper_item`。企业可见的变更项清单由 [[change_cfg_match]] 规则按 `client_type + identify_style + cust_type + head_company + enable` 过滤得到，配置主键 `id` 被 [[cust_change_record]] 的 `alter_type_id` 以逗号分隔引用（[[change_item_contains]]）。

`oper_item` 与 `plat_item` 非一一对应（如平台「法定代表人手机号码变更」对应运营「法人手机号变更」），跨端对齐时必须按 `item_code` 而非名称。

## 需求背景

变更能力由配置驱动而非硬编码：不同端（AGW 平台录入端 / ACCOUNT_PRODUCT 账号产品端）、不同认证方式（INVITE/INVITE_AGW/SELF/SIMPLE）、不同客户类型、是否总公司维度，可见的变更项不同；`open_process` 决定该变更项是否走流程。`data_desc` 仅用于前端展示所需材料说明，未参与校验。

## 版本演进

v0.1：首次抽取配置维度与过滤键；本页暂无历史版本差异记录。

```ground:table
table: cust_change_cfg
fields:
  - name: id
    type: bigint
    desc: "变更项配置主键，被 cust_change_record.alter_type_id 以逗号分隔列表引用"
    dict: null
  - name: item_code
    type: varchar
    desc: "变更项字典编码 UN0001~UN0016（UN0012=企业管理员变更，UN0013=管理员手机号变更）"
    dict: null
  - name: plat_item
    type: varchar
    desc: "平台侧变更项展示名称"
    dict: null
  - name: oper_item
    type: varchar
    desc: "运营中台侧变更项名称，与 plat_item 非一一对应（如平台'法定代表人手机号码变更'对应运营'法人手机号变更'）"
    dict: null
  - name: client_type
    type: varchar
    desc: "端类型：AGW=平台录入端，ACCOUNT_PRODUCT=账号产品端"
    dict: null
  - name: identify_style
    type: varchar
    desc: "认证方式：INVITE/INVITE_AGW/SELF/SIMPLE，用于匹配可用变更项"
    dict: null
  - name: head_company
    type: char(1)
    desc: "是否总公司维度配置 Y/N（企业客户需按企业 head_company 过滤）"
    dict: null
  - name: open_process
    type: char(1)
    desc: "该变更项是否开启流程 Y/N"
    dict: null
  - name: cust_type
    type: varchar
    desc: "适用客户类型 1/2/3，与 cust_change_record.cust_type 同源"
    dict: null
  - name: data_desc
    type: varchar
    desc: "变更所需材料说明文案（仅展示，未参与校验）"
    dict: null
  - name: enable
    type: char(1)
    desc: "有效标记，配置列表查询口径固定为 'Y'（EnableEnum.Y.name()）"
    dict: EnableEnum
```

相关页面：[[change_item_code]]、[[change_cfg_match]]、[[valid_change_cfg]]、[[admin_mobile_change_items]]、[[cust_change_record]]。

---END FILE---

---FILE: tables/cust_oper_change_record.md ---
---
type: table
title: 运营人员变更记录表 (cust_oper_change_record)
page_key: cust_oper_change_record
domain: 企业变更与运营变更
status: draft
aliases: [运营人员变更记录, 运营变更记录, cust_oper_change_record]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_oper_change_record
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
---

`cust_oper_change_record` 记录企业联系人（运营人员）归属的变更历史：一次变更一条记录，以 `before_operator_id` / `after_operator_id` 结构化保存变更前后运营人员。它与 [[cust_change_record]] 是两类不同业务，见 [[customer_change]]；`person_id` 指向 [[cust_person_info]] 的主键，运营人员维度语义见 [[operator]]。

`change_type` 以字面量落库（非枚举 `name()`），与 [[change_status]] 所描述的枚举式状态字段在落库方式上不同，写入方必须保持一致。

## 需求背景

运营人员变更来源多样（手动、批量、自动分配、自动更新、资产审核同步、企业变更回调），需要在同一张表中留存可追溯的变更链路，因此把「谁触发（`source_system` / `change_type`）、改了什么（before/after）、为什么（`change_reason`）」拆开保存；资产审核同步场景额外落 `asset_id`。查询口径见 [[valid_oper_change_record]] 与 [[oper_change_query]]。

## 版本演进

v0.1：首次抽取字段含义与查询口径；本页暂无历史版本差异记录。

```ground:table
table: cust_oper_change_record
fields:
  - name: person_id
    type: bigint
    desc: "企业联系人ID，对应 cust_person_info.id"
    dict: null
  - name: change_type
    type: varchar
    desc: "运营人员变更类型：MANUAL/BATCH/AUTO_ASSIGN/AUTO_UPDATE/ASSET_AUDIT_SYNC/CUST_CHANGE_CALLBACK（字面量落库，非枚举 name）"
    dict: null
  - name: before_operator_id
    type: bigint
    desc: "变更前运营人员ID"
    dict: null
  - name: after_operator_id
    type: bigint
    desc: "变更后运营人员ID"
    dict: null
  - name: change_reason
    type: varchar
    desc: "变更原因文案（手动变更运营人员/批量变更运营人员/资产审核同步/企业变更回调运营人员变更）"
    dict: null
  - name: source_system
    type: varchar
    desc: "变更来源系统标识"
    dict: null
  - name: asset_id
    type: bigint
    desc: "资产审核同步场景关联的资产ID"
    dict: null
  - name: enable
    type: char(1)
    desc: "逻辑有效标记；查询口径固定 enable='Y'（字面量直写，非 EnableEnum）"
    dict: null
```

相关页面：[[cust_person_info]]、[[operator]]、[[valid_oper_change_record]]、[[oper_change_query]]、[[customer_change]]。

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 企业客户信息表 (cust_company_info)
page_key: cust_company_info
domain: 企业变更与运营变更
status: draft
aliases: [企业客户信息, 企业主体表, cust_company_info]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_company_info
  - code:CustCompanyInfoApplication.java
  - code:CustChangeApplication.java
contract_version: "0.1"
---

`cust_company_info` 是企业客户主体表，本主题下它主要作为变更业务的「被改对象」与「准入/生命周期约束来源」：`cust_status` 决定是否已有变更在途（[[cust_company_info_cust_status]]、[[company_in_change]]），`check_status` 决定能否发起变更（[[checking_company_cannot_change]]），`identify_style` + `head_company` 参与变更项配置匹配（[[change_cfg_match]]），`cust_build_status` 支撑「重新建档」类变更项（[[cust_company_info_cust_build_status]]）。

本表的 `id` 是 [[cust_change_record]] 的 `cust_id` 取值来源，与运营中台客户 ID 不可混用（[[cust_id]]）。

## 需求背景

企业客户在平台上的状态是多条线并行的：准入审核（`check_status`）、生命周期（`cust_status`）、建档（`cust_build_status`）。变更业务必须同时读这三条线——已冻结/已注销/审核中的企业能否变更、变更中企业如何跳转、公司维度如何取配置，都由这几个字段组合判定。

## 版本演进

v0.1：首次抽取三个状态字段与两个配置匹配键；本页暂无历史版本差异记录。文档主张「已冻结或已注销不允许变更」在代码中未覆盖，见 [[change_precheck]] 的版本演进说明。

```ground:table
table: cust_company_info
fields:
  - name: id
    type: bigint
    desc: "企业客户主键，对应 cust_change_record.cust_id（非 code）"
    dict: null
  - name: cust_status
    type: varchar
    desc: "企业客户生命周期状态：ADD/EFFECT/FREEZE/WRITEOFF/CHANGE（CHANGE=变更中）"
    dict: null
  - name: check_status
    type: varchar
    desc: "企业准入审核状态，取值同 CheckStatus（CUST_CHECK_CHECKING 等）"
    dict: OperApiConstants.CheckStatus
  - name: cust_build_status
    type: varchar
    desc: "企业认证/建档状态（INIT/CUST_CONFIRM_AWAIT/CUST_BUILDING/BUILD_SUCCESS/BUILD_FAIL）"
    dict: null
  - name: head_company
    type: char(1)
    desc: "是否总公司 Y/N，决定加载哪一套变更项配置"
    dict: null
  - name: identify_style
    type: varchar
    desc: "企业认证方式，作为变更项配置匹配键之一"
    dict: null
  - name: manager_id
    type: bigint
    desc: "企业维度业务经理；与 cust_person_info.operator_id 不同表不同粒度"
    dict: null
```

相关页面：[[cust_company_info_cust_status]]、[[cust_company_info_cust_build_status]]、[[company_in_change]]、[[checking_company_cannot_change]]、[[cust_id]]、[[cust_change_record]]。

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: 企业联系人表 (cust_person_info)
page_key: cust_person_info
domain: 企业变更与运营变更
status: draft
aliases: [企业联系人, 联系人表, cust_person_info]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_person_info
  - code:CustChangeApplication.java
  - code:CustSyncEventProvider.java
contract_version: "0.1"
---

`cust_person_info` 是企业联系人表。在变更链路里它承担两个角色：一是企业管理员（`user_type='admin'`）的定位与手机号对比，用于「管理员手机号变更」类变更项的判定与跳转（[[company_admin_contact]]、[[admin_mobile_redirect]]）；二是运营人员归属的载体，`operator_id` / `operator_realname` 是联系人维度的运营人员，见 [[operator]]。

本表主键被 [[cust_oper_change_record]] 的 `person_id` 引用，运营人员变更历史因此挂到联系人粒度而非企业粒度。

## 需求背景

同一企业下存在多个联系人，变更判定必须先锁定「人」再判断「号」：管理员手机号变更需要拿运营中台回传的新旧管理员信息（[[before_after_comparison]]）与本地 `phone` 对比；运营人员变更则需要按联系人维度留痕。

## 版本演进

v0.1：首次抽取联系人与运营人员两个维度的字段；本页暂无历史版本差异记录。

```ground:table
table: cust_person_info
fields:
  - name: id
    type: bigint
    desc: "联系人主键，被 cust_oper_change_record.person_id 引用"
    dict: null
  - name: phone
    type: varchar
    desc: "联系人手机号；管理员手机号变更判定时用于新旧对比"
    dict: null
  - name: user_type
    type: varchar
    desc: "联系人类型：admin=企业管理员，operator=经办人"
    dict: UserTypeEnum
  - name: operator_id
    type: bigint
    desc: "联系人维度的运营人员ID；与 cust_company_info.manager_id 不同粒度"
    dict: null
  - name: operator_realname
    type: varchar
    desc: "联系人维度的运营人员姓名"
    dict: null
```

相关页面：[[company_admin_contact]]、[[admin_mobile_redirect]]、[[operator]]、[[cust_oper_change_record]]、[[before_after_comparison]]。

---END FILE---

---FILE: processes/cust_change_record_status.md ---
---
type: process
title: 企业变更记录审核状态机 (cust_change_record.status)
page_key: cust_change_record_status
domain: 企业变更与运营变更
status: draft
aliases: [变更审核状态机, 变更流程状态, CUST_CHECK]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustChangeApplication.java
  - db:cust_change_record
contract_version: "0.1"
---

本状态机描述单条变更记录（[[cust_change_record]]）从发起到终态的流转，状态值来自 `OperApiConstants.CheckStatus` 并以 `name()` 落库。它与 [[cust_company_info_cust_status]]（企业生命周期）不是同一状态轴：[[change_status]] 页面记录了三者的边界。

终态为 `CUST_CHECK_PASS` / `CUST_CHECK_REJECT`；非终态记录才允许被流程重建（[[change_rebuild]]、[[rebuildable_change_process]]）。DB 中还存在历史默认值 `'1'`，代码常量中无对应语义，见 REVIEW。

## 需求背景

变更由平台发起、运营中台审核，因此状态机需要表达「发起 → 审核中 → 通过/拒绝」的主干，以及两个非主干分支：中台退回让客户补充（`CUST_CHECK_BACKTOCUSTOM`）与客户重新发起时拒绝旧流程（`CUST_CHECK_REJECT`）。

## 版本演进

v0.1：首次抽取状态取值与四条迁移；`'1'` 历史默认值语义未声明，待与历史数据/旧版本对齐。

```ground:process
name: 企业变更记录审核状态机
field: cust_change_record.status
states:
  - value: CUST_CHECK_INIT
    label: 变更发起
    source: code_const
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_const
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户补充
    source: code_const
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_const
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_const
  - value: "1"
    label: 历史默认值（语义未声明）
    source: db_dist
transitions:
  - from: CUST_CHECK_INIT
    event: 发起变更同步运营中台
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustCompanyInfoApplication.java#submitCust(CheckStatus.CUST_CHECK_INIT) + OperApiConstants.CheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核退回
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustCompanyInfoApplication.java#syncClientForSimple(CheckStatus.CUST_CHECK_BACKTOCUSTOM)"
  - from: CUST_CHECK_CHECKING
    event: 客户操作重新发起/拒绝旧流程
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java#changeRebuild"
  - from: "*非终态"
    event: 流程重建
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java#changeRebuild(notIn PASS,REJECT 取最新非终态记录后调用 operCustFacade.changeRejectProcess)"
```

相关页面：[[cust_change_record]]、[[change_status]]、[[change_rebuild]]、[[rebuildable_change_process]]、[[company_in_change]]。

---REVIEW: process | 企业变更记录审核状态机 (cust_change_record.status)---
状态取值 `'1'` 仅有 DB 分布证据，代码常量 `OperApiConstants.CheckStatus` 中不存在该值，且现有迁移均不产生该状态。需确认是历史版本遗留、初始化默认值，还是存在未覆盖的写入点；在确认前，任何按 `status` 过滤的口径都应显式排除或解释 `'1'`。
---END REVIEW---

---END FILE---

---FILE: processes/cust_company_info_cust_status.md ---
---
type: process
title: 企业客户生命周期状态机 (cust_company_info.cust_status)
page_key: cust_company_info_cust_status
domain: 企业变更与运营变更
status: draft
aliases: [企业生命周期状态机, cust_status, 企业状态流转]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustChangeApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

本状态机描述企业客户主体（[[cust_company_info]]）的生命周期流转，其中 `CHANGE`（变更中）是与本主题直接相关的态：企业一旦发起变更，主体被打上 `CHANGE`，变更入口与页面跳转随之变化（[[company_in_change]]、[[change_on_way]]）。

注意本状态机的 `status` 与企业准入审核状态 `check_status` 是两条独立的轴，见 [[change_status]]。

## 需求背景

企业既有日常运营态（生效/冻结/注销），也有变更在途态。把「变更中」建模为企业级状态而非仅记录级状态，是为了让入口、待办页、重复发起校验都能用同一字段判定，避免并发发起多次变更。

## 版本演进

v0.1：首次抽取五个状态与四条迁移；文档主张「已冻结或已注销不允许变更」未被代码覆盖，见 [[change_precheck]]。

```ground:process
name: 企业客户生命周期状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 待建档/新增
    source: code_const
  - value: EFFECT
    label: 已生效
    source: code_const
  - value: FREEZE
    label: 已冻结
    source: code_const
  - value: WRITEOFF
    label: 已注销
    source: code_const
  - value: CHANGE
    label: 变更中
    source: code_const
transitions:
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java#freeze→custStatusOperator(CustStatusOperatorConstant.FREEZE)"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java#unfreeze→custStatusOperator(UNFREEZE)"
  - from: EFFECT
    event: 注销
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java#diable→custStatusOperator(DISABLE)"
  - from: EFFECT
    event: 发起企业变更（运营中台同步变更状态）
    to: CHANGE
    evidence: "code_path:CustChangeApplication.java#getRedirectPage(判定 cust_status=CHANGE) + CustCompanyInfoApplication.java#doIfNecessaryChange(operCustFacade.change)"
```

相关页面：[[cust_company_info]]、[[company_in_change]]、[[change_on_way]]、[[change_status]]、[[cust_company_info_cust_build_status]]。

---END FILE---

---FILE: processes/cust_company_info_cust_build_status.md ---
---
type: process
title: 企业认证/建档状态机 (cust_company_info.cust_build_status)
page_key: cust_company_info_cust_build_status
domain: 企业变更与运营变更
status: draft
aliases: [建档状态机, cust_build_status, 重新建档状态]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustCompanyInfoApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

本状态机描述企业客户（[[cust_company_info]]）认证/建档的流转，服务于变更项中的「重新建档」相关场景。建档成功后企业进入 `cust_status=EFFECT`，与 [[cust_company_info_cust_status]] 联动。

## 需求背景

变更项可能要求企业重新提交材料并由运营中台重新审核建档，因此需要一条独立于变更审核（[[cust_change_record_status]]）的建档状态线：客户确认 → 中台审核 → 成功/拒绝，退回时可回到待客户确认。

## 版本演进

v0.1：首次抽取五个状态与五条迁移；本页暂无历史版本差异记录。

```ground:process
name: 企业认证/建档状态机（变更项'重新建档'相关）
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_const
  - value: CUST_BUILDING
    label: 运营中台审核中
    source: code_const
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_const
  - value: BUILD_FAIL
    label: 建档拒绝
    source: code_const
transitions:
  - from: INIT/BUILD_FAIL
    event: 客户提交资料
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(before INIT|BUILD_FAIL → after CUST_CONFIRM_AWAIT)"
  - from: CUST_CONFIRM_AWAIT
    event: 推运营中台审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(before CUST_CONFIRM_AWAIT → after CUST_BUILDING)"
  - from: CUST_BUILDING
    event: 运营中台退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(before CUST_BUILDING → after CUST_CONFIRM_AWAIT)"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(after BUILD_SUCCESS → cust_status=EFFECT)"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(after BUILD_FAIL)"
```

相关页面：[[cust_company_info]]、[[cust_company_info_cust_status]]、[[cust_change_record_status]]。

---END FILE---

---FILE: calibers/valid_change_cfg.md ---
---
type: caliber
title: 有效变更项配置
page_key: valid_change_cfg
domain: 企业变更与运营变更
status: draft
aliases: [变更项配置口径, enable=Y 配置]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

口径定义：变更项配置列表只取 `cust_change_cfg.enable = 'Y'` 的行。它是 [[change_cfg_match]] 规则的第一道过滤，与端类型、认证方式、客户类型、是否总公司等条件叠加后得到企业可见的变更项清单（[[cust_change_cfg]]）。

## 需求背景

变更项配置需要支持下线而不物理删除，因此所有读取路径统一加 `enable` 条件，避免历史配置重新出现在企业可见清单中。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 有效变更项配置
predicate: "cust_change_cfg.enable = 'Y'"
scope: 客户变更配置列表查询
evidence: "code_path:CustChangeApplication.java#list(EnableEnum.Y.name())"
```

相关页面：[[cust_change_cfg]]、[[change_cfg_match]]、[[valid_change_record]]、[[valid_oper_change_record]]。

---END FILE---

---FILE: calibers/valid_change_record.md ---
---
type: caliber
title: 有效变更记录
page_key: valid_change_record
domain: 企业变更与运营变更
status: draft
aliases: [变更记录有效口径, enable=Y 记录]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

口径定义：读取或判定变更记录（[[cust_change_record]]）时只认 `enable = 'Y'` 的行，用于变更记录读取与跳转判定。

## 需求背景

变更记录存在作废/失效场景，入口跳转与展示必须基于有效记录，否则会把已失效的在途流程当成真实在途。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 有效变更记录
predicate: "cust_change_record.enable = 'Y'"
scope: 变更记录读取/跳转判定
evidence: "code_path:CustChangeApplication.java#getRedirectPage"
```

相关页面：[[cust_change_record]]、[[valid_change_cfg]]、[[valid_oper_change_record]]、[[admin_mobile_redirect]]。

---END FILE---

---FILE: calibers/valid_oper_change_record.md ---
---
type: caliber
title: 有效运营变更记录
page_key: valid_oper_change_record
domain: 企业变更与运营变更
status: draft
aliases: [运营人员变更记录口径, 运营变更 enable=Y]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
---

口径定义：按联系人查询运营人员变更历史（[[cust_oper_change_record]]）时固定 `enable='Y'`。该条件在代码中以字面量 `'Y'` 直写，未走 `EnableEnum`，与 [[valid_change_cfg]] 的写法不同。

## 需求背景

运营人员变更记录是对外展示的历史列表，需要过滤失效行；字面量写法属于实现差异，口径本身与「有效记录」一致。

## 版本演进

v0.1：首次固化该口径，并标注字面量直写的实现差异。

```ground:caliber
name: 有效运营变更记录
predicate: "cust_oper_change_record.enable = 'Y'"
scope: 运营人员变更记录查询（字面量 'Y' 直写）
evidence: "code_path:OperChangeRecordApplication.java#queryByPersonId"
```

相关页面：[[cust_oper_change_record]]、[[oper_change_query]]、[[valid_change_record]]、[[valid_change_cfg]]。

---END FILE---

---FILE: calibers/rebuildable_change_process.md ---
---
type: caliber
title: 可重建的变更流程
page_key: rebuildable_change_process
domain: 企业变更与运营变更
status: draft
aliases: [非终态变更流程, 可重建流程口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

口径定义：可被流程重建逻辑命中的变更记录，是 `status NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')` 的记录。命中后取最新一条非终态记录，调用运营中台 `changeRejectProcess` 结束旧流程，由客户重新发起，见 [[change_rebuild]]。

## 需求背景

客户在流程未结束时重新发起变更，需要先收敛旧流程，避免同一企业存在多条在途变更；因此以「非终态」而非「审核中」为条件，把退回补充等中间态一并纳入。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 可重建的变更流程
predicate: "cust_change_record.status NOT IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')"
scope: 变更流程重建前置条件
evidence: "code_path:CustChangeApplication.java#changeRebuild(notIn CheckStatus.PASS/REJECT)"
```

相关页面：[[change_rebuild]]、[[cust_change_record_status]]、[[cust_change_record]]、[[valid_change_record]]。

---END FILE---

---FILE: calibers/company_in_change.md ---
---
type: caliber
title: 变更中企业
page_key: company_in_change
domain: 企业变更与运营变更
status: draft
aliases: [变更在途企业, CHANGE 状态口径]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

口径定义：`cust_company_info.cust_status = 'CHANGE'` 即视为该企业存在变更在途。该口径用于变更待办页与变更提交成功页的跳转判定，也是 [[change_on_way]] 规则的判定依据。

## 需求背景

变更在途的判定以企业主体状态为唯一入口，避免逐条扫描变更记录；跳转分支因此稳定且可缓存。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 变更中企业
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: 变更待办页/变更提交成功页跳转判定
evidence: "code_path:CustChangeApplication.java#getRedirectPage"
```

相关页面：[[cust_company_info]]、[[cust_company_info_cust_status]]、[[change_on_way]]、[[admin_mobile_redirect]]。

---END FILE---

---FILE: calibers/checking_company_cannot_change.md ---
---
type: caliber
title: 审核中企业不可发起变更
page_key: checking_company_cannot_change
domain: 企业变更与运营变更
status: draft
aliases: [准入审核中不可变更, check_status=CUST_CHECK_CHECKING]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

口径定义：`cust_company_info.check_status = 'CUST_CHECK_CHECKING'` 时不允许发起变更，是 [[change_precheck]] 规则的核心判定。

注意该口径只覆盖准入审核中一种情况；文档还主张「已冻结/已注销不允许变更」，代码未覆盖，见 [[change_precheck]] 的版本演进。

## 需求背景

企业准入审核与信息变更会互相改写同一批资质字段，准入审核中再叠加变更会造成两端状态冲突，因此前置拦截。

## 版本演进

v0.1：首次固化该口径，并标注其覆盖范围小于文档主张。

```ground:caliber
name: 审核中企业不可发起变更
predicate: "cust_company_info.check_status = 'CUST_CHECK_CHECKING'"
scope: 是否可变更申请校验
evidence: "code_path:CustChangeApplication.java#changeEnable"
```

相关页面：[[change_precheck]]、[[cust_company_info]]、[[change_status]]、[[change_on_way]]。

---END FILE---

---FILE: calibers/company_admin_contact.md ---
---
type: caliber
title: 企业管理员联系人
page_key: company_admin_contact
domain: 企业变更与运营变更
status: draft
aliases: [管理员联系人口径, user_type=admin]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
  - code:CustSyncEventProvider.java
contract_version: "0.1"
---

口径定义：定位企业管理员时取 [[cust_person_info]] 中 `user_type = 'admin'` 的联系人。管理员变更、管理员手机号变更（[[admin_mobile_change_items]]）都以此为起点。

## 需求背景

同一企业下联系人类型混杂（管理员、经办人），变更判定必须只针对管理员这一类型，否则会把经办人手机号误判为管理员手机号。

## 版本演进

v0.1：首次固化该口径。

```ground:caliber
name: 企业管理员联系人
predicate: "cust_person_info.user_type = 'admin'"
scope: 管理员变更/手机号变更时定位联系人
evidence: "code_path:CustChangeApplication.java#getRedirectPage + CustSyncEventProvider.java#getAuthChangeCompanyType(UserTypeEnum.admin)"
```

相关页面：[[cust_person_info]]、[[admin_mobile_change_items]]、[[admin_mobile_redirect]]、[[operator]]。

---END FILE---

---FILE: calibers/admin_mobile_change_items.md ---
---
type: caliber
title: 管理员手机号类变更项
page_key: admin_mobile_change_items
domain: 企业变更与运营变更
status: draft
aliases: [UN0012/UN0013 变更项, 管理员手机号变更项集合]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

口径定义：变更项编码落在 `UN0012`（企业管理员变更）、`UN0013`（管理员手机号变更）的集合，即为触发变更提交成功页跳转判定的变更项，见 [[admin_mobile_redirect]] 与 [[change_item_contains]]。

## 需求背景

只有会改变管理员手机号的变更项才需要提示登录人重新确认身份，因此把这两个编码作为固定集合维护。

## 版本演进

v0.1：首次固化该口径；编码取自 `CustUpdateItemCodeConstants`。

```ground:caliber
name: 管理员手机号类变更项
predicate: "cust_change_cfg.item_code IN ('UN0012','UN0013')"
scope: 触发变更提交成功页跳转的变更项集合
evidence: "code_path:CustChangeApplication.java#getRedirectPage(CustUpdateItemCodeConstants.UN0012/UN0013)"
```

相关页面：[[change_item_code]]、[[change_item_contains]]、[[admin_mobile_redirect]]、[[company_admin_contact]]。

---END FILE---

---FILE: concepts/change_item_code.md ---
---
type: concept
title: 变更项编码
page_key: change_item_code
domain: 企业变更与运营变更
status: draft
aliases: [itemCode, UN编码, 变更项 code]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_cfg
  - db:cust_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_cfg.item_code
field_targets:
  - cust_change_cfg.item_code
adjudication: boundary
also_confused_with:
  - cust_change_record.alter_type_id
  - cust_change_record.alter_data
---

「变更项编码」在口语中常被简称为「变更项」，但它特指配置字典编码：`cust_change_cfg.item_code`，取值 UN0001~UN0016（[[cust_change_cfg]]）。判定某个变更是否包含某项能力时，正确链路是 `alter_type_id` → `cust_change_cfg.id` → `item_code`（[[change_item_contains]]），而不是直接比较记录上的字段。

边界：`item_code` 是配置字典编码（UN0001~UN0016）；[[cust_change_record]].`alter_type_id` 是 `cust_change_cfg.id` 的逗号分隔列表；`alter_data` 是编码的 JSON 数组快照。三者不可互换。

## 需求背景

变更项需要在端、认证方式、客户类型、总公司维度上分别配置，同时又要跨端对齐名称不一致的项（`plat_item` vs `oper_item`），因此引入稳定编码作为唯一语义键。

## 版本演进

v0.1：首次建立术语桥；本页暂无历史版本差异记录。

相关页面：[[cust_change_cfg]]、[[change_item_contains]]、[[admin_mobile_change_items]]、[[cust_change_record]]。

---END FILE---

---FILE: concepts/change_status.md ---
---
type: concept
title: 变更状态
page_key: change_status
domain: 企业变更与运营变更
status: draft
aliases: [status, 审核状态, 变更流程状态]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - db:cust_company_info
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.status
field_targets:
  - cust_change_record.status
adjudication: boundary
also_confused_with:
  - cust_company_info.check_status
  - cust_company_info.cust_status
---

「变更状态」默认指 `cust_change_record.status`，即单条变更流程的审核状态，取值与流转见 [[cust_change_record_status]]。

边界：`cust_change_record.status` 是单条变更流程状态；`cust_company_info.check_status` 是企业准入审核状态（[[cust_company_info]]）；`cust_company_info.cust_status` 是企业生命周期状态（[[cust_company_info_cust_status]]）。三者分属不同表、不同轴，不可互相替代。

## 需求背景

变更业务同时受「本条变更走到哪」「企业能否变更」「企业是否已在变更」三类判断影响，状态字段被复用时极易串台，本术语桥用于固定默认所指。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record_status]]、[[cust_company_info_cust_status]]、[[checking_company_cannot_change]]、[[company_in_change]]。

---END FILE---

---FILE: concepts/customer_change.md ---
---
type: concept
title: 客户变更 / 企业变更
page_key: customer_change
domain: 企业变更与运营变更
status: draft
aliases: [企业变更, 企业信息变更, 客户变更]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - db:cust_oper_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: null
field_targets:
  - cust_change_record.cust_id
  - cust_oper_change_record.person_id
adjudication: boundary
also_confused_with:
  - cust_oper_change_record
---

「客户变更 / 企业变更」在本域内特指企业客户信息与资质的变更，落 [[cust_change_record]]，走审核状态机 [[cust_change_record_status]]。

边界：`cust_change_record` 是企业客户信息/资质变更；[[cust_oper_change_record]] 是企业联系人（运营人员）归属变更记录。两者表、触发源、状态字段均不同，不能合并统计。

本术语指向的是业务实体而非单个字段，因此不在 `maps_to` 上落字段锚点，改由 `field_targets` 记录两侧的判别字段。

## 需求背景

两类「变更」在中文口语中高度重合（都叫「变更」），但一侧影响企业资质、一侧影响服务归属，混淆会导致统计与权限判断出错，故单列术语桥。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[cust_oper_change_record]]、[[operator]]、[[alter_mode]]。

---REVIEW: concept | 客户变更 / 企业变更---
该术语的所指是实体级（表），按 concept 页约定 `maps_to` 必须是「表.字段」或 dictKey.VALUE，故本页暂置 `maps_to: null`，仅以 `field_targets` 记录判别字段。需要维护者决策：是接受实体级 `maps_to: cust_change_record`，还是在本域新增一层聚合概念页。
---END REVIEW---

---END FILE---

---FILE: concepts/alter_mode.md ---
---
type: concept
title: 变更方式
page_key: alter_mode
domain: 企业变更与运营变更
status: draft
aliases: [alterMode, 平台变更, 企业自行变更]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.alter_mode
field_targets:
  - cust_change_record.alter_mode
adjudication: synonym
also_confused_with: []
---

「变更方式」即 [[cust_change_record]].`alter_mode`，标识这次变更是谁发起的：1=平台变更（PLAT_ALTER），2=企业自行变更（SELF_ALTER），由 `AlterModeEnum.getDictKey` 落库。

## 需求背景

同一次变更在平台代客操作与企业自助操作下的材料要求、通知对象不同，需要独立字段留存发起方式，且必须落字典键值而非枚举名。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[customer_change]]、[[change_status]]。

---END FILE---

---FILE: concepts/cust_id.md ---
---
type: concept
title: 企业ID / 客户ID
page_key: cust_id
domain: 企业变更与运营变更
status: draft
aliases: [custId, 企业ID, 客户ID]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.cust_id
field_targets:
  - cust_change_record.cust_id
adjudication: boundary
also_confused_with:
  - cust_change_record.oper_cust_id
  - cust_change_record.id
---

「企业ID / 客户ID」在本域默认指 `cust_change_record.cust_id`，其取值是本平台企业主键，对应 [[cust_company_info]].`id`（不是 `code`）。

边界：`cust_id` 是本平台 `cust_company_info.id`；`oper_cust_id` 是运营中台客户 ID（外部系统）；`id` 是变更记录主键。三者不可互换，尤其在流程重建时 `companyId` 必须等于当前登录企业（[[change_rebuild]]）。

## 需求背景

变更业务跨平台与运营中台两侧，两侧对「客户」的编号体系不同，历史上出现过把中台 ID 当本平台 ID 使用的问题，故显式固化边界。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[change_rebuild]]、[[before_after_comparison]]、[[cust_company_info]]。

---END FILE---

---FILE: concepts/operator.md ---
---
type: concept
title: 运营人员
page_key: operator
domain: 企业变更与运营变更
status: draft
aliases: [运营人, operator, 归属运营]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_person_info
  - db:cust_oper_change_record
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
maps_to: cust_person_info.operator_id
field_targets:
  - cust_person_info.operator_id
adjudication: boundary
also_confused_with:
  - cust_company_info.manager_id
---

「运营人员」指联系人维度上绑定的运营人，落 [[cust_person_info]].`operator_id` / `operator_realname`，其变更历史见 [[cust_oper_change_record]]。

边界：`cust_person_info.operator_id` / `operator_realname` 为联系人维度的运营人员；`cust_company_info.manager_id` 为企业维度业务经理，两者不同表不同粒度。

## 需求背景

服务归属既可按企业维度指定业务经理，也可按联系人维度指定运营人；变更、通知、权限判断取错粒度会直接影响服务对象。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_person_info]]、[[cust_oper_change_record]]、[[oper_change_query]]、[[cust_company_info]]。

---END FILE---

---FILE: concepts/before_after_comparison.md ---
---
type: concept
title: 变更前后信息对比
page_key: before_after_comparison
domain: 企业变更与运营变更
status: draft
aliases: [oldPersonId/personId, 变更前后对比, oper_cust_info 对比]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - db:cust_oper_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.oper_cust_info
field_targets:
  - cust_change_record.oper_cust_info
adjudication: boundary
also_confused_with:
  - cust_oper_change_record.before_operator_id
---

「变更前后信息对比」默认指 [[cust_change_record]].`oper_cust_info`——运营中台返回的客户信息 JSON，其中 `personId` 为变更后管理员、`oldPersonId` 为变更前管理员，用于管理员手机号变更的判定与跳转（[[admin_mobile_redirect]]）。

边界：`oper_cust_info` 是运营中台返回的 JSON（含 `personId` / `oldPersonId`）；[[cust_oper_change_record]].`before_operator_id`/`after_operator_id` 是运营人员变更的独立结构化字段。一侧需解析 JSON，一侧可直接比较，不可互换。

## 需求背景

管理员变更发生在运营中台侧，平台需要拿到变更前后的管理员身份才能判断登录人手机号是否失效，因此以 JSON 快照形式留存并本地解析。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[admin_mobile_redirect]]、[[cust_oper_change_record]]、[[operator]]、[[cust_person_info]]。

---END FILE---

---FILE: rules/change_precheck.md ---
---
type: rule
title: 变更申请前置校验
page_key: change_precheck
domain: 企业变更与运营变更
status: draft
aliases: [changeEnable, 是否可变更校验]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

**(document_claim，未证实)**

规则内容：当企业 `check_status = CUST_CHECK_CHECKING`（准入审核中）时，`changeEnable` 返回 false，不允许发起变更，直接阻断变更申请入口。判定口径见 [[checking_company_cannot_change]]。

## 需求背景

准入审核与信息变更会写同一批企业资质字段，准入审核中再发起变更会造成两端状态互相覆盖，因此在入口处拦截，避免脏数据进入变更流程。

## 版本演进

v0.1：代码侧仅覆盖「准入审核中」一种情形。需求文档 3.4.3 主张「企业状态为『已冻结』或『已注销』时不允许变更」，语义分析判定为 uncovered：`CustChangeApplication.java#changeEnable` 仅校验 `check_status=CUST_CHECK_CHECKING`，未见 `cust_status=FREEZE/WRITEOFF` 拦截。该主张未经证实，暂不进入锚点块，也不作为现有规则的一部分。

```ground:rule
name: 变更申请前置校验
content: "企业 check_status=CUST_CHECK_CHECKING（准入审核中）时 changeEnable 返回 false，不允许发起变更"
impact: 阻断变更申请入口
field_targets:
  - cust_company_info.check_status
evidence: "code_path:CustChangeApplication.java#changeEnable"
```

相关页面：[[checking_company_cannot_change]]、[[cust_company_info]]、[[change_on_way]]、[[cust_company_info_cust_status]]。

---REVIEW: rule | 变更申请前置校验---
需求文档 3.4.3（企业状态为「已冻结」或「已注销」时不允许变更）与代码现状不一致：`changeEnable` 只拦 `CUST_CHECK_CHECKING`，没有冻结/注销拦截。需确认是文档过期、校验落在前端或其他入口，还是确实缺失实现；在确认前，本页不为其生成锚点。
---END REVIEW---

---END FILE---

---FILE: rules/change_on_way.md ---
---
type: rule
title: 变更在途判定
page_key: change_on_way
domain: 企业变更与运营变更
status: draft
aliases: [changeHasBusiOnWay, 变更在途]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

规则内容：`cust_company_info.cust_status='CHANGE'` 即视为该企业存在变更在途业务（`changeHasBusiOnWay` 返回 true），用于控制变更入口与页面跳转。口径定义见 [[company_in_change]]。

## 需求背景

企业级「变更中」标记让入口无需扫描变更记录即可判断在途，保证重复发起与跳转判定的一致性。

## 版本演进

v0.1：首次固化。

```ground:rule
name: 变更在途判定
content: "cust_company_info.cust_status='CHANGE' 即视为存在变更在途业务（changeHasBusiOnWay 返回 true）"
impact: 控制变更入口与页面跳转
field_targets:
  - cust_company_info.cust_status
evidence: "code_path:CustChangeApplication.java#changeHasBusiOnWay(CustStatusEnum.CHANGE.name())"
```

相关页面：[[company_in_change]]、[[cust_company_info]]、[[cust_company_info_cust_status]]、[[change_rebuild]]。

---END FILE---

---FILE: rules/change_rebuild.md ---
---
type: rule
title: 变更流程重建
page_key: change_rebuild
domain: 企业变更与运营变更
status: draft
aliases: [changeRebuild, 变更重建/拒绝旧流程]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

规则内容：取该企业最新一条 `status` 非 `CUST_CHECK_PASS`/`CUST_CHECK_REJECT` 的变更记录（[[rebuildable_change_process]]）；不存在则抛「无变更流程，不支持拒绝」；存在则调用运营中台 `changeRejectProcess` 结束旧流程并由客户重新发起；且 `companyId` 必须等于当前登录企业，构成越权校验。

## 需求背景

同一企业只允许存在一条在途变更。客户重新发起时，平台需要先结束旧流程再建新流程，同时防止跨企业操作他人流程。

## 版本演进

v0.1：首次固化，含越权校验要求。

```ground:rule
name: 变更流程重建
content: "取该企业最新一条 status 非 CUST_CHECK_PASS/CUST_CHECK_REJECT 的变更记录；不存在则抛'无变更流程，不支持拒绝'；存在则调用运营中台 changeRejectProcess 结束旧流程并由客户重新发起；且 companyId 必须等于当前登录企业"
impact: 拒绝旧流程、重建新流程；越权校验
field_targets:
  - cust_change_record.cust_id
  - cust_change_record.status
  - cust_change_record.oper_cust_id
evidence: "code_path:CustChangeApplication.java#changeRebuild"
```

相关页面：[[rebuildable_change_process]]、[[cust_change_record_status]]、[[cust_id]]、[[cust_change_record]]。

---END FILE---

---FILE: rules/admin_mobile_redirect.md ---
---
type: rule
title: 管理员手机号变更后的页面跳转
page_key: admin_mobile_redirect
domain: 企业变更与运营变更
status: draft
aliases: [getRedirectPage, 变更提交成功页跳转]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

规则内容：变更项命中 `UN0012`/`UN0013`（[[admin_mobile_change_items]]）时，解析 `oper_cust_info` 的 `oldPersonId`/`personId` 取新旧管理员手机号（[[before_after_comparison]]、[[company_admin_contact]]）；若新旧手机号不同且与登录手机号不同，跳转变更提交成功页并回带新管理员手机号/姓名，否则跳运营中台变更待办页。

## 需求背景

管理员手机号被改掉后，当前登录人的手机号可能已不是企业管理员手机号，需要引导其确认身份或前往中台待办，避免继续用失效身份操作。

## 版本演进

v0.1：首次固化跳转分支与判定顺序。

```ground:rule
name: 管理员手机号变更后的页面跳转
content: "变更项命中 UN0012/UN0013 时解析 oper_cust_info 的 oldPersonId/personId 取新旧管理员手机号；若新旧手机号不同且与登录手机号不同，跳转变更提交成功页并回带新管理员手机号/姓名，否则跳运营中台变更待办页"
impact: 变更后登录人手机号与管理员不一致时引导重新登录/查看
field_targets:
  - cust_change_record.alter_type_id
  - cust_change_record.oper_cust_info
  - cust_person_info.phone
evidence: "code_path:CustChangeApplication.java#getRedirectPage"
```

相关页面：[[admin_mobile_change_items]]、[[before_after_comparison]]、[[company_admin_contact]]、[[cust_person_info]]、[[valid_change_record]]。

---END FILE---

---FILE: rules/change_cfg_match.md ---
---
type: rule
title: 变更项配置匹配
page_key: change_cfg_match
domain: 企业变更与运营变更
status: draft
aliases: [配置过滤, 可用变更项匹配]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

规则内容：企业客户按 `client_type + identify_style + cust_type + head_company + enable='Y'` 过滤（[[valid_change_cfg]]）；个人客户（`clientType=INDIVIDUALS`）不按 `head_company` 过滤，`headCompany` 取自当前登录用户 `companyCode` 对应企业。

## 需求背景

同一套变更能力要按端、认证方式、客户类型、公司维度差异化发布；个人客户无总分公司概念，必须走另一条过滤分支。

## 版本演进

v0.1：首次固化过滤键与个人客户分支。

```ground:rule
name: 变更项配置匹配
content: "企业客户按 client_type + identify_style + cust_type + head_company + enable='Y' 过滤；个人客户(clientType=INDIVIDUALS)不按 head_company 过滤，headCompany 取自当前登录用户 companyCode 对应企业"
impact: 决定企业可见的变更项清单
field_targets:
  - cust_change_cfg.client_type
  - cust_change_cfg.identify_style
  - cust_change_cfg.cust_type
  - cust_change_cfg.head_company
  - cust_change_cfg.enable
evidence: "code_path:CustChangeApplication.java#list"
```

相关页面：[[cust_change_cfg]]、[[valid_change_cfg]]、[[cust_company_info]]、[[change_item_code]]。

---END FILE---

---FILE: rules/change_item_contains.md ---
---
type: rule
title: 变更项包含性判定
page_key: change_item_contains
domain: 企业变更与运营变更
status: draft
aliases: [checkChangeItems, alter_type_id 解析]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
---

规则内容：`alter_type_id` 按逗号拆分后 `in cust_change_cfg.id` 批量查询，再判断命中记录的 `item_code` 是否落在目标编码集合中，作为跳转分支判定依据（[[admin_mobile_redirect]]）。

## 需求背景

变更记录上存的是配置主键列表而非编码列表，任何按编码的判定都必须经配置表翻译一次，该规则固化翻译链路，避免直接比较 `alter_type_id` 与 `item_code`。

## 版本演进

v0.1：首次固化。

```ground:rule
name: 变更项包含性判定
content: "alter_type_id 按逗号拆分后 in cust_change_cfg.id 批量查询，再判断命中记录的 item_code 是否落在目标编码集合中"
impact: 跳转分支判定依据
field_targets:
  - cust_change_record.alter_type_id
  - cust_change_cfg.id
  - cust_change_cfg.item_code
evidence: "code_path:CustChangeApplication.java#checkChangeItems"
```

相关页面：[[change_item_code]]、[[cust_change_cfg]]、[[cust_change_record]]、[[admin_mobile_change_items]]。

---END FILE---

---FILE: rules/oper_change_query.md ---
---
type: rule
title: 运营变更记录查询口径
page_key: oper_change_query
domain: 企业变更与运营变更
status: draft
aliases: [queryByPersonId, 运营变更历史查询]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:OperChangeRecordApplication.java
contract_version: "0.1"
---

规则内容：按 `person_id` 查询且 `enable='Y'`（[[valid_oper_change_record]]），按 `create_time` 倒序；`change_type` 经 `CHANGE_TYPE_DESC` 映射为中文描述，`operatorId`/`operatorName` 取自 `createBy`/`createUser`。

## 需求背景

运营人员变更历史要求最新的在最前，且对外展示中文字面量与操作者名称，因此查询层固定排序与字段映射。

## 版本演进

v0.1：首次固化查询与展示映射。

```ground:rule
name: 运营变更记录查询口径
content: "按 person_id 查询且 enable='Y'，按 create_time 倒序；change_type 经 CHANGE_TYPE_DESC 映射为中文描述，operatorId/operatorName 取自 createBy/createUser"
impact: 运营人员变更历史展示
field_targets:
  - cust_oper_change_record.person_id
  - cust_oper_change_record.enable
  - cust_oper_change_record.change_type
evidence: "code_path:OperChangeRecordApplication.java#queryByPersonId/#toVO"
```

相关页面：[[cust_oper_change_record]]、[[valid_oper_change_record]]、[[operator]]、[[cust_person_info]]。

---END FILE---