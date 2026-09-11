---FILE: tables/cust_change_record.md ---
---
type: table
title: cust_change_record（企业变更单）
page_key: cust_change_record
domain: 企业变更与运营变更
status: draft
aliases: [变更单, 企业变更申请单, 客户变更记录]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - code_path:CustChangeApplication.java:changeRebuild
  - code_path:CustChangeApplication.java:getRedirectPage
  - code_path:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
---

`cust_change_record` 是企业客户信息变更申请单的主表，一条记录代表某企业的一次变更发起。变更单的审核状态 [[concepts.change-status]]（`status`）驱动整条变更链路的生命周期，终态口径见 [[calibers.change-record-terminal-status]]；变更项本身不直接落库为业务编码，而是以 `alter_type_id` 关联 [[tables.cust_change_cfg]]，变更数据快照落在 `alter_data`。运营中台侧的流程与人员信息通过 `oper_cust_id`、`oper_cust_info` 回写到本表，变更管理员场景的跳转判定依赖它们，见 [[rules.admin-phone-change-redirect]]。变更单的发起与准入受 [[tables.cust_company_info]] 的准入审核状态约束，见 [[rules.change-application-admission]]。

## 需求背景

平台侧与运营中台侧并行承担变更审批：平台侧记录变更项与材料要求，运营中台侧承载流程实例。因此本表既要保存变更项快照（`alter_data`、`alter_type_id`），也要保存中台客户与流程信息（`oper_cust_id`、`oper_cust_info`、`pp_cust_info`），并记录是否需要客户确认、是否需要重签授权书、电子授权书签署状态、消息发送标记等业务开关字段。管理员手机号变更项（`UN0012`/`UN0013`）的跳转判定见 [[calibers.admin-phone-change-item]]。

## 版本演进

v0.1：首次登记，字段语义全部来自库表实际取值分布（db）与代码引用（code），未引入需求文档主张。

```ground:table
table: cust_change_record
fields:
  - name: status
    meaning: "变更单审核状态。代码引用 OperApiConstants.CheckStatus：CUST_CHECK_CHECKING=审核中、CUST_CHECK_PASS=审核通过（终态）、CUST_CHECK_REJECT=审核拒绝（终态）、CUST_CHECK_BACKTOCUSTOM=退回客户；DB 另存有 '1'（表默认值）及 CUSTS003、returnCust-<时间戳> 等历史/脏值"
    evidence: db
  - name: alter_type_id
    meaning: "变更项记录 id 列表，存 cust_change_cfg.id 的逗号分隔串（代码 split(\",\") 后按 id IN 查配置还原 item_code）"
    evidence: code
  - name: alter_data
    meaning: "变更数据，变更项编码的 JSON 数组，如 [\"UN0001\",\"UN0002\",\"UN0014\"]"
    evidence: db
  - name: alter_mode
    meaning: "变更方式，DB 实测取值 1/2（对应 AlterModeEnum，枚举定义未在本次代码层给出）"
    evidence: db
  - name: alter_type
    meaning: 变更类型
    evidence: db
  - name: admin_auth
    meaning: 企业管理授权（Y/N）
    evidence: db
  - name: legal_auth
    meaning: 法人代表授权（Y/N）
    evidence: db
  - name: oper_channel
    meaning: "运营中台变更渠道，DB 实测：operation-pplatform-common-new、operation-pplatform-not-edit-new、DIRECT_INIT"
    evidence: db
  - name: oper_cust_id
    meaning: 运营中台客户 id，changeRebuild 用它调运营中台查流程信息
    evidence: code
  - name: oper_cust_info
    meaning: 运营中台客户信息 JSON，含 oldPersonId（旧管理员）与 personId（新管理员），用于变更前后对比与跳转判定
    evidence: code
  - name: pp_cust_info
    meaning: 产融客户信息快照
    evidence: code
  - name: need_cust_confirm
    meaning: 是否需要客户确认（Y/N）
    evidence: db
  - name: need_resign_auth
    meaning: 是否需要重签授权书（Y/N），直推识别变更项时写入，后续只读
    evidence: db
  - name: electronic_auth_sign_status
    meaning: 电子授权书签署状态，DB 实测 PENDING/SIGNED
    evidence: db
  - name: msg_send
    meaning: 消息发送标记（Y/N）
    evidence: db
  - name: cust_type
    meaning: 客户类型（DB 实测 1/2/3/4；代码按 CustTypeEnum.ENTERPRISE / INDIVIDUALS 分支处理）
    evidence: db
  - name: cust_company_type
    meaning: 客户企业角色，DB 实测 CORE/SUPPLIER/DEALER/FINANCE/PROJECT_COMPANY/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY/CORE_MANAGER
    evidence: db
  - name: enable
    meaning: 逻辑有效标记（Y）
    evidence: db
```

---END FILE---

---FILE: tables/cust_change_cfg.md ---
---
type: table
title: cust_change_cfg（变更项配置）
page_key: cust_change_cfg
domain: 企业变更与运营变更
status: draft
aliases: [变更配置, 变更项配置表, 变更项字典]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_cfg
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
---

`cust_change_cfg` 是变更项的配置字典：每一行代表一个可发起的变更项（`item_code`，DB 实测 `UN0001`–`UN0016`），并给出平台侧与运营中台侧的名称、所需材料说明，以及该变更项在「端类型 × 认证方式 × 客户类型 × 是否总公司」四维下的适用性。它是 [[concepts.item-code]] 的权威来源，也是变更项清单查询的唯一入口，匹配口径见 [[calibers.change-cfg-match-dimensions]]，查询恒带有效标记，见 [[calibers.change-cfg-enable]]。

## 需求背景

不同端（`ACCOUNT_PRODUCT` / `AGW`）、不同认证方式（`INVITE` / `INVITE_AGW` / `SELF` / `SIMPLE`）、不同客户类型下可做的变更项不同；企业类型还要再按是否总公司（`head_company`）细分，个人类型不叠加该维度。配置表因此以多维组合的方式表达「谁能改什么」，并由 `open_process` 决定是否走流程。

## 版本演进

v0.1：首次登记，字段语义来自库表取值分布与 `CustChangeApplication.list` 的查询条件。

```ground:table
table: cust_change_cfg
fields:
  - name: item_code
    meaning: 变更项编码，DB 实测 UN0001–UN0016
    evidence: db
  - name: plat_item
    meaning: 平台侧变更项名称（如 企业管理员手机号变更、法定代表人变更）
    evidence: db
  - name: oper_item
    meaning: 运营中台侧变更项名称
    evidence: db
  - name: data_desc
    meaning: 变更需要材料说明（如 营业执照、法定代表人身份证正反面、企业授权书、人脸识别）
    evidence: db
  - name: client_type
    meaning: 端类型，DB 实测 ACCOUNT_PRODUCT / AGW
    evidence: db
  - name: cust_type
    meaning: 适用客户类型（DB 实测 1/2/3）
    evidence: db
  - name: identify_style
    meaning: 适用认证方式，DB 实测 INVITE / INVITE_AGW / SELF / SIMPLE
    evidence: db
  - name: head_company
    meaning: 是否总公司（Y/N），企业类型配置再按此维度细分
    evidence: db
  - name: enable
    meaning: 配置有效标记，查询恒带 ='Y'
    evidence: code
  - name: open_process
    meaning: 是否开启流程（Y/N）
    evidence: db
```

---END FILE---

---FILE: tables/cust_oper_change_record.md ---
---
type: table
title: cust_oper_change_record（运营人员变更记录）
page_key: cust_oper_change_record
domain: 企业变更与运营变更
status: draft
aliases: [运营变更流水, 操作运营变更记录]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_oper_change_record
  - code_path:OperChangeRecordApplication.java:queryByPersonId
  - code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC
contract_version: "0.1"
---

`cust_oper_change_record` 记录企业联系人（经办人）所绑定运营人员的前后变更流水，是「谁把哪个联系人从哪个运营人员改到了哪个运营人员」的审计轨迹。它与 [[tables.cust_change_record]] 不是一回事，术语边界见 [[concepts.oper-change-record]]；记录按 `person_id`（企业联系人）组织，见 [[concepts.operator]]。变更类型的分类口径见 [[processes.oper-change-type]]，查询口径见 [[rules.oper-change-record-query]]。

## 需求背景

运营人员的变更来源多样：人工手动调整、批量分配、资产审核同步、企业变更回调触发的自动调整。因此本表以 `change_type` 区分来源、以 `change_reason` 保存可读原因、以 `source_system` 标注来源系统、以 `asset_id` 关联资产审核场景，从而支撑联系人详情页的变更历史展示。

## 版本演进

v0.1：首次登记，字段语义来自库表取值分布与 `OperChangeRecordApplication` 的查询与字典映射代码。

```ground:table
table: cust_oper_change_record
fields:
  - name: change_type
    meaning: "运营人员变更类型，代码字典 CHANGE_TYPE_DESC：MANUAL=手动变更、BATCH=批量变更、AUTO_ASSIGN=自动分配、AUTO_UPDATE=自动更新、ASSET_AUDIT_SYNC=资产审核同步、CUST_CHANGE_CALLBACK=企业变更回调"
    evidence: code
  - name: change_reason
    meaning: "变更原因，DB 实测：手动变更运营人员 / 批量变更运营人员 / 资产审核同步 / 企业变更回调运营人员变更"
    evidence: db
  - name: person_id
    meaning: 企业联系人 id（cust_person_info.id），查询入口参数
    evidence: code
  - name: before_operator_name
    meaning: 变更前运营人员姓名
    evidence: code
  - name: after_operator_name
    meaning: 变更后运营人员姓名
    evidence: code
  - name: asset_id
    meaning: 资产 id（资产审核同步场景来源）
    evidence: code
  - name: source_system
    meaning: 来源系统
    evidence: code
  - name: enable
    meaning: 逻辑有效标记，查询恒带 ='Y'
    evidence: code
```

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（企业客户信息）
page_key: cust_company_info
domain: 企业变更与运营变更
status: draft
aliases: [企业信息表, 企业客户主表]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code_path:CustChangeApplication.java:changeEnable
  - code_path:CustChangeApplication.java:changeHasBusiOnWay
  - code_path:CustCompanyInfoApplication.java:freeze
contract_version: "0.1"
---

`cust_company_info` 是企业客户主体表，在企业变更链路中承担两个关键判定：企业生命周期状态 `cust_status` 决定是否存在在途变更（见 [[calibers.company-change-on-way]]、[[rules.change-on-way-company]]），准入审核状态 `check_status` 决定能否发起变更（见 [[calibers.company-change-enable]]、[[rules.change-application-admission]]）。生命周期状态机见 [[processes.cust-company-info-status]]，其中的 `check_status` 与变更单状态 [[concepts.change-status]] 语义不同，勿混用。

## 需求背景

企业从新建到生效、冻结、注销的流转由平台侧维护，而变更审批在运营中台侧进行，两者通过状态字段实现「在途变更不可重复发起」的约束。建档/认证状态（`cust_build_status`）的流转更新还限定在主数据（`data_type='1'`）上，见 [[calibers.company-master-data]]。

## 版本演进

v0.1：首次登记，字段语义来自代码枚举与 `CustCompanyInfoApplication`、`CustChangeApplication` 的状态判定逻辑。

```ground:table
table: cust_company_info
fields:
  - name: cust_status
    meaning: "企业生命周期状态，代码枚举 CustStatusEnum：ADD=新增/待提交、CHANGE=变更中、EFFECT=已生效、FREEZE=已冻结、WRITEOFF=已注销"
    evidence: code
  - name: check_status
    meaning: 企业准入审核状态（OperApiConstants.CheckStatus），changeEnable 以 CUST_CHECK_CHECKING 判定不可发起变更
    evidence: code
  - name: cust_build_status
    meaning: "企业建档/认证状态（CustBuildStatusEnum：INIT/BUILD_FAIL/BUILD_SUCCESS/CUST_CONFIRM_AWAIT/CUST_BUILDING 等）"
    evidence: code
  - name: data_type
    meaning: 数据类型：1=主数据、0=记录数据；状态流转更新条件限定为 '1'
    evidence: code
```

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（企业联系人信息）
page_key: cust_person_info
domain: 企业变更与运营变更
status: draft
aliases: [联系人表, 企业经办人信息]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_person_info
  - code_path:CustChangeApplication.java:getRedirectPage
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
---

`cust_person_info` 存放企业联系人（管理员 / 经办人）信息，是运营人员变更流水 [[tables.cust_oper_change_record]] 的主体来源（`person_id` 即本表主键）。术语「运营人员 / 经办人」的区分见 [[concepts.operator]]。管理员手机号变更场景中，联系人手机号 `phone` 与登录用户名（`getUserName` 返回手机号）及中台新旧管理员手机号三方比对，见 [[rules.admin-phone-change-redirect]]。

## 需求背景

联系人的 `user_type` 区分管理员与经办人，决定了变更管理员手机号时的判定对象；`phone` 既是对外联系方式，也是登录标识，因此手机号变更会直接影响旧管理员与新管理员进入变更页面时的跳转结果。

## 版本演进

v0.1：首次登记，字段语义来自代码枚举与跳转判定逻辑。

```ground:table
table: cust_person_info
fields:
  - name: user_type
    meaning: "联系人类型（UserTypeEnum：admin=管理员、operator=经办人）"
    evidence: code
  - name: phone
    meaning: 手机号；管理员手机号变更判定中与登录用户名（getUserName 返回手机号）比较
    evidence: code
```

---END FILE---

---FILE: processes/cust-change-record-status.md ---
---
type: process
title: 客户变更单状态机（cust_change_record.status）
page_key: process.cust-change-record-status
domain: 企业变更与运营变更
status: draft
aliases: [变更单状态, 变更审批状态, CheckStatus]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - code_path:CustSyncEventProvider.java:onEvent
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

变更单状态挂在 [[tables.cust_change_record]] 的 `status` 上，取值来自 `OperApiConstants.CheckStatus` 枚举：审核中（`CUST_CHECK_CHECKING`）、审核通过（`CUST_CHECK_PASS`，终态）、审核拒绝（`CUST_CHECK_REJECT`，终态）、退回客户（`CUST_CHECK_BACKTOCUSTOM`）。终态口径被流程重建直接使用，见 [[calibers.change-record-terminal-status]] 与 [[rules.change-record-terminal-filter]]。调用方重新发起变更时，会先结束旧流程并把旧单置为拒绝，见 [[rules.change-rebuild]]。

## 需求背景

审核终态由运营中台回调驱动：`CUST_CHECK_PASS` 与 `CUST_CHECK_REJECT` 回调统一交由工作流审核执行器处理，事件提供者 `CustSyncEventProvider.onEvent` 直接跳过，见 [[rules.audit-callback-dispatch]]。因此本状态机的终态写入并不在本模块内完成，本页只登记状态与可观测的流转。

## 版本演进

v0.1：首次登记。状态取值中 `1`（表默认值）、`CUSTS003`、`returnCust-<时间戳>` 为库表实测值，代码层未见对应枚举声明，暂按历史/脏值处理。

```ground:process
name: 客户变更单状态
field: cust_change_record.status
states:
  - value: "1"
    label: 待提交/初始（表默认值，代码层未见枚举声明）
    source: db_dist
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户
    source: db_dist
  - value: CUST_CHECK_PASS
    label: 审核通过（终态）
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝（终态）
    source: code_enum
  - value: CUSTS003
    label: 未识别的历史值（1 条）
    source: db_dist
  - value: "returnCust-<时间戳>"
    label: 历史退回标记，非标准枚举（13 条）
    source: db_dist
transitions:
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核通过回调
    to: CUST_CHECK_PASS
    evidence: "code_path:CustSyncEventProvider.java:onEvent（CUST_CHECK_PASS 由 CustWorkflowAuditCommitProcessor 处理，onEvent 直接跳过）"
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核拒绝回调
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustSyncEventProvider.java:onEvent（CUST_CHECK_REJECT 同上，交由工作流审核执行器）"
  - from: CUST_CHECK_CHECKING
    event: 客户操作重新发起/流程重建（拒绝旧流程，发起新流程）
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustChangeApplication.java:changeRebuild（取最新非终态记录，调 operCustFacade.changeRejectProcess 结束旧流程）"
```

---END FILE---

---FILE: processes/cust-company-info-status.md ---
---
type: process
title: 企业生命周期状态机（cust_company_info.cust_status）
page_key: process.cust-company-info-status
domain: 企业变更与运营变更
status: draft
aliases: [企业状态, CustStatusEnum, 企业生命周期]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code_path:CustCompanyInfoApplication.java:freeze
  - code_path:CustCompanyInfoApplication.java:unfreeze
  - code_path:CustCompanyInfoApplication.java:diable
contract_version: "0.1"
---

企业生命周期状态由 `CustStatusEnum` 定义，挂在 [[tables.cust_company_info]] 的 `cust_status` 上：新增/待提交（`ADD`）、变更中（`CHANGE`）、已生效（`EFFECT`）、已冻结（`FREEZE`）、已注销（`WRITEOFF`）。冻结、解冻、注销分别由 `CustCompanyInfoApplication.freeze`、`unfreeze`、`diable` 驱动并调用 `custStatusSync` 落状态。`CHANGE` 是变更在途的判定依据，见 [[calibers.company-change-on-way]] 与 [[rules.change-on-way-company]]。

## 需求背景

变更链路只依赖 `CHANGE` 这一个中间态来判断「企业是否已有在途变更」；冻结与注销属于企业维度的运营动作，与变更单状态 [[concepts.change-status]] 分属不同层面：前者描述企业生命周期，后者描述单次变更申请的审批进度。

## 版本演进

v0.1：首次登记，状态取值与迁移均来自代码枚举与状态同步调用点。

```ground:process
name: 企业生命周期状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/待提交
    source: code_enum
  - value: CHANGE
    label: 变更中（存在在途变更）
    source: code_enum
  - value: EFFECT
    label: 已生效
    source: code_enum
  - value: FREEZE
    label: 已冻结
    source: code_enum
  - value: WRITEOFF
    label: 已注销
    source: code_enum
transitions:
  - from: EFFECT
    event: freeze
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze + custStatusSync(FREEZE->CustStatusEnum.FREEZE)"
  - from: FREEZE
    event: unfreeze
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze + custStatusSync(UNFREEZE->CustStatusEnum.EFFECT)"
  - from: EFFECT
    event: diable（注销）
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable + custStatusSync(DISABLE->CustStatusEnum.WRITEOFF)"
```

---END FILE---

---FILE: processes/oper-change-type.md ---
---
type: process
title: 运营人员变更类型（cust_oper_change_record.change_type）
page_key: process.oper-change-type
domain: 企业变更与运营变更
status: draft
aliases: [change_type, 运营变更类型枚举, CHANGE_TYPE_DESC]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_oper_change_record
  - code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC
contract_version: "0.1"
---

`change_type` 是 [[tables.cust_oper_change_record]] 上的分类字段，取值集合由代码字典 `CHANGE_TYPE_DESC` 给出：`MANUAL`=手动变更、`BATCH`=批量变更、`AUTO_ASSIGN`=自动分配、`AUTO_UPDATE`=自动更新、`ASSET_AUDIT_SYNC`=资产审核同步、`CUST_CHANGE_CALLBACK`=企业变更回调。字典映射与未命中回显规则见 [[rules.oper-change-type-dict]]。

## 需求背景

运营人员变更来源分散在人工操作、批量任务、资产审核同步与企业变更回调等多条链路，本字段是这些链路在流水上的统一归类维度，前端展示名由字典映射；映射未命中时直接回显原值，保证新增来源不丢数据。

## 版本演进

v0.1：首次登记。该状态机当前无状态迁移语义，仅登记取值集合（transitions 为空）。

```ground:process
name: 运营人员变更类型
field: cust_oper_change_record.change_type
states:
  - value: MANUAL
    label: 手动变更
    source: code_enum
  - value: BATCH
    label: 批量变更
    source: code_enum
  - value: AUTO_ASSIGN
    label: 自动分配
    source: code_enum
  - value: AUTO_UPDATE
    label: 自动更新
    source: code_enum
  - value: ASSET_AUDIT_SYNC
    label: 资产审核同步
    source: code_enum
  - value: CUST_CHANGE_CALLBACK
    label: 企业变更回调
    source: code_enum
transitions: []
```

---END FILE---

---FILE: calibers/change-record-terminal-status.md ---
---
type: caliber
title: 变更单终态
page_key: caliber.change-record-terminal-status
domain: 企业变更与运营变更
status: draft
aliases: [变更终态口径, 非终态变更单]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

「变更单终态」是 [[tables.cust_change_record]] 上用于识别企业是否存在未完结变更流程的口径：`CUST_CHECK_PASS` 与 `CUST_CHECK_REJECT` 视为终态，取在途变更单时以 notIn 排除，取最新一条非终态记录用于流程重建。状态取值全集见 [[processes.cust-change-record-status]]，应用规则见 [[rules.change-record-terminal-filter]] 与 [[rules.change-rebuild]]。注意本口径只描述变更单维度，与企业生命周期状态 [[calibers.company-change-on-way]] 不同层。

## 需求背景

流程重建要求「同一企业同一时刻只保留一条在途变更单」，因此必须有一个稳定的终态集合把已完结单据排除在外。终态的写入由运营中台回调链路负责，本地模块只读该口径，见 [[rules.audit-callback-dispatch]]。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.changeRebuild` 的查询条件。

```ground:caliber
name: 变更单终态
predicate: "cust_change_record.status IN ('CUST_CHECK_PASS','CUST_CHECK_REJECT')"
scope: 识别企业是否存在未完结变更流程
evidence: code_path:CustChangeApplication.java:changeRebuild（notIn PASS/REJECT 取最新一条）
```

---END FILE---

---FILE: calibers/company-change-enable.md ---
---
type: caliber
title: 企业可发起变更
page_key: caliber.company-change-enable
domain: 企业变更与运营变更
status: draft
aliases: [变更入口可用性, changeEnable]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeEnable
contract_version: "0.1"
---

「企业可发起变更」是变更入口的可用性口径：企业准入审核状态不等于 `CUST_CHECK_CHECKING` 时才允许发起变更。字段语义见 [[tables.cust_company_info]]，与变更单状态 [[concepts.change-status]] 的边界见该概念页；落地规则见 [[rules.change-application-admission]]。

## 需求背景

企业准入审核在途时，企业主体信息本身可能还在变化，此时不允许叠加变更申请，避免同一企业出现两条互相冲突的审批链路。该口径是企业不存在时同样返回不可用的前置校验。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.changeEnable`。

```ground:caliber
name: 企业可发起变更
predicate: "cust_company_info.check_status <> 'CUST_CHECK_CHECKING'"
scope: 变更入口可用性校验
evidence: code_path:CustChangeApplication.java:changeEnable
```

---END FILE---

---FILE: calibers/company-change-on-way.md ---
---
type: caliber
title: 企业在途变更
page_key: caliber.company-change-on-way
domain: 企业变更与运营变更
status: draft
aliases: [在途变更口径, changeHasBusiOnWay]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeHasBusiOnWay
  - code_path:CustChangeApplication.java:getRedirectPage
contract_version: "0.1"
---

「企业在途变更」以 [[tables.cust_company_info]] 的 `cust_status = 'CHANGE'` 判定：命中即认为企业存在在途变更业务，`changeHasBusiOnWay` 返回 true。该口径同时影响变更入口可用性与页面跳转（是否进入运营中台变更待办页）。生命周期状态机见 [[processes.cust-company-info-status]]，落地规则见 [[rules.change-on-way-company]]；与单张变更单的终态口径 [[calibers.change-record-terminal-status]] 互补：前者是结果态，后者是单据集合。

## 需求背景

变更审批在运营中台进行，平台侧需要在用户进入时快速判断「是否有事正在办」，因此选择一个单字段的结果态作为在途标识，而不是每次聚合变更单集合。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.changeHasBusiOnWay` / `getRedirectPage`。

```ground:caliber
name: 企业在途变更
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: 变更在途判定与页面跳转
evidence: code_path:CustChangeApplication.java:changeHasBusiOnWay / getRedirectPage
```

---END FILE---

---FILE: calibers/change-cfg-enable.md ---
---
type: caliber
title: 生效变更配置
page_key: caliber.change-cfg-enable
domain: 企业变更与运营变更
status: draft
aliases: [配置有效标记, 变更配置查询口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
---

「生效变更配置」是 [[tables.cust_change_cfg]] 查询的基础过滤口径：只取 `enable = 'Y'` 的配置行。该口径是 [[calibers.change-cfg-match-dimensions]] 的组成部分，配置下线的标准做法是改标记而不是删行。

## 需求背景

变更项配置需要支持上下线而不丢失历史引用，因此以逻辑有效标记控制可见性；查询条件恒定携带该标记，保证任何入口拿到的都是生效配置。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.list`（`EnableEnum.Y.name()`）。

```ground:caliber
name: 生效变更配置
predicate: "cust_change_cfg.enable = 'Y'"
scope: 变更项配置查询
evidence: code_path:CustChangeApplication.java:list（EnableEnum.Y.name()）
```

---END FILE---

---FILE: calibers/change-cfg-match-dimensions.md ---
---
type: caliber
title: 企业变更配置匹配维度
page_key: caliber.change-cfg-match-dimensions
domain: 企业变更与运营变更
status: draft
aliases: [变更项匹配口径, 配置四维匹配]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
---

变更项清单按「端类型 + 认证方式 + 客户类型 + 是否总公司 + 有效标记」匹配 [[tables.cust_change_cfg]]；其中企业类型按 `head_company` 细分，个人类型不叠加该维度。落地规则见 [[rules.change-cfg-identity-match]]，有效标记口径见 [[calibers.change-cfg-enable]]，配置字段含义见配置表页。

## 需求背景

同一次变更在不同端、不同认证方式下的材料要求与可选范围不同，因此配置表以多维组合表达适用性；个人客户没有「是否总公司」概念，匹配时必须去掉该维度，否则会取不到配置。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.list` 的查询条件拼装。

```ground:caliber
name: 企业变更配置匹配维度
predicate: "cust_change_cfg.client_type = ? AND cust_change_cfg.identify_style = ? AND cust_change_cfg.cust_type = ? AND cust_change_cfg.head_company = ? AND cust_change_cfg.enable = 'Y'"
scope: 企业类型按 head_company 细分；个人类型不叠加 head_company
evidence: code_path:CustChangeApplication.java:list
```

---END FILE---

---FILE: calibers/admin-phone-change-item.md ---
---
type: caliber
title: 管理员手机号变更项
page_key: caliber.admin-phone-change-item
domain: 企业变更与运营变更
status: draft
aliases: [UN0012, UN0013, 管理员手机号变更]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:getRedirectPage
contract_version: "0.1"
---

「管理员手机号变更项」是跳转页判定的识别口径：变更项编码落在 `UN0012`/`UN0013`（`CustUpdateItemCodeConstants`）即视为管理员手机号变更。变更单与配置的关联方式见 [[concepts.item-code]]，判定后的跳转逻辑见 [[rules.admin-phone-change-redirect]]。

## 需求背景

管理员手机号变更会改变登录主体与新管理员的可见内容，因此需要单独识别该变更项并走不同的落地页；识别依据是稳定的业务编码而非数据库主键，以兼容配置表主键漂移。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.getRedirectPage`。

```ground:caliber
name: 管理员手机号变更项
predicate: "cust_change_cfg.item_code IN ('UN0012','UN0013')"
scope: 变更单跳转页判定
evidence: code_path:CustChangeApplication.java:getRedirectPage（CustUpdateItemCodeConstants.UN0012/UN0013）
```

---END FILE---

---FILE: calibers/oper-change-record-valid.md ---
---
type: caliber
title: 有效运营人员变更记录
page_key: caliber.oper-change-record-valid
domain: 企业变更与运营变更
status: draft
aliases: [运营变更流水有效口径, enable=Y 流水]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
---

运营人员变更流水的查询口径为 [[tables.cust_oper_change_record]] 上 `enable = 'Y'`，按联系人精确匹配后返回。完整查询行为见 [[rules.oper-change-record-query]]，术语边界见 [[concepts.oper-change-record]]。

## 需求背景

流水表用于对外展示历史，删除行会破坏审计连续性，因此以逻辑有效标记过滤；查询恒带该标记，保证列表与详情一致。

## 版本演进

v0.1：首次登记，口径来自 `OperChangeRecordApplication.queryByPersonId`。

```ground:caliber
name: 有效运营人员变更记录
predicate: "cust_oper_change_record.enable = 'Y'"
scope: 按联系人查询运营人员变更流水
evidence: code_path:OperChangeRecordApplication.java:queryByPersonId
```

---END FILE---

---FILE: calibers/company-master-data.md ---
---
type: caliber
title: 主数据企业
page_key: caliber.company-master-data
domain: 企业变更与运营变更
status: draft
aliases: [data_type=1, 主数据口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
contract_version: "0.1"
---

「主数据企业」是 [[tables.cust_company_info]] 上 `data_type = '1'` 的口径，用于限定建档/认证状态流转更新的作用范围（`1`=主数据、`0`=记录数据）。相关字段语义见企业客户信息表页。

## 需求背景

同一企业在库中可能存在记录数据行，状态流转只应作用于主数据行，否则会污染历史/记录数据；因此更新条件显式限定 `data_type = '1'`。

## 版本演进

v0.1：首次登记，口径来自 `CustCompanyInfoApplication.appenUpdateCustBulidStatus`。

```ground:caliber
name: 主数据企业
predicate: "cust_company_info.data_type = '1'"
scope: 建档/认证状态流转更新的过滤条件
evidence: code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
```

---END FILE---

---FILE: concepts/item-code.md ---
---
type: concept
title: 变更项编码
page_key: concept.item-code
domain: 企业变更与运营变更
status: draft
aliases: [item_code, 变更项, UN00xx]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_cfg
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
maps_to: cust_change_cfg.item_code
field_targets: [cust_change_cfg.item_code]
adjudication: boundary
also_confused_with: [cust_change_record.alter_type_id, cust_change_record.alter_data]
---

「变更项编码」指配置表 [[tables.cust_change_cfg]] 上的 `item_code`（DB 实测 `UN0001`–`UN0016`），是稳定的业务编码，也是对外与跨系统沟通变更项时使用的标识。变更单 [[tables.cust_change_record]] 上另有两个易混字段：`alter_type_id` 存的是配置表主键 `cust_change_cfg.id` 的逗号分隔串，必须 join 配置表才能还原为 `item_code`；`alter_data` 存的是 `item_code` 的 JSON 数组快照。

## 需求背景

变更项需要跨平台侧与运营中台侧对齐，因此用业务编码而非自增主键做语义标识；变更单保存主键列表是为了关联配置，保存编码数组是为了留存发起时的快照。识别管理员手机号变更项使用的正是编码，见 [[calibers.admin-phone-change-item]]。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

---END FILE---

---FILE: concepts/change-status.md ---
---
type: concept
title: 变更状态/审核状态
page_key: concept.change-status
domain: 企业变更与运营变更
status: draft
aliases: [status, checkStatus, 审核状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - db:cust_company_info
contract_version: "0.1"
maps_to: cust_change_record.status
field_targets: [cust_change_record.status]
adjudication: boundary
also_confused_with: [cust_company_info.check_status, cust_company_info.act_procinst_status, cust_company_info.cust_status]
---

「变更状态 / 审核状态」在本域内指 [[tables.cust_change_record]] 的 `status`，即变更单维度的审批状态（`CheckStatus` 枚举），状态机见 [[processes.cust-change-record-status]]。它与三个字段容易混淆：`cust_company_info.check_status` 是企业准入审核状态（决定能否发起变更，见 [[calibers.company-change-enable]]）；`cust_company_info.act_procinst_status` 是工作流引擎侧审批状态；`cust_company_info.cust_status` 是企业生命周期状态（见 [[processes.cust-company-info-status]]）。

## 需求背景

同一家企业同时存在「准入审批」「变更审批」「工作流实例状态」「生命周期状态」四条不同粒度的状态线，字段命名相近但归属对象不同；本概念用于在口径与规则页之间固定指代，避免把企业状态当作单据状态使用。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

---END FILE---

---FILE: concepts/oper-change-record.md ---
---
type: concept
title: 运营人员变更记录
page_key: concept.oper-change-record
domain: 企业变更与运营变更
status: draft
aliases: [操作运营变更, cust_oper_change_record]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_oper_change_record
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
maps_to: cust_oper_change_record
field_targets: [cust_oper_change_record]
adjudication: boundary
also_confused_with: [cust_change_record]
---

「运营人员变更记录」指 [[tables.cust_oper_change_record]]，记录企业联系人（经办人）所绑定运营人员的前后变更流水，分类维度为 `change_type`（手动/批量/资产审核同步/企业变更回调），见 [[processes.oper-change-type]]。它与 [[tables.cust_change_record]] 容易混淆：后者是企业信息变更申请单及其审批状态，与运营人员归属无关；前者不承载审批，只承载归属变化轨迹。

## 需求背景

企业变更回调会间接触发运营人员调整，两条链路在时间上相邻、在企业维度上相关，因此需要明确区分「企业信息改了什么」与「运营人员换成了谁」，查询口径见 [[rules.oper-change-record-query]]。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

---END FILE---

---FILE: concepts/operator.md ---
---
type: concept
title: 运营人员/经办人
page_key: concept.operator
domain: 企业变更与运营变更
status: draft
aliases: [operator, person_id, 经办人]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_person_info
  - db:cust_oper_change_record
contract_version: "0.1"
maps_to: cust_oper_change_record.before_operator_id / after_operator_id
field_targets: [cust_oper_change_record.before_operator_id, cust_oper_change_record.after_operator_id]
adjudication: boundary
also_confused_with: [cust_oper_change_record.person_id, cust_person_info.operator_id]
---

「运营人员」与「经办人」在 [[tables.cust_oper_change_record]] 上是两组不同字段：`before_operator_*` / `after_operator_*` 指平台运营人员（被变更的对象）；`person_id` / `person_name` 指企业联系人（变更主体，即经办人）。[[tables.cust_person_info]] 的 `operator_id` 则是该联系人当前绑定的运营人冗余，属于当前态而非流水。

## 需求背景

一次运营人员调整的主体是联系人、客体是运营人员，字段命名上都带 `operator`/`person`，极易读反变更方向；本概念固定「谁被改、改成谁、由谁触发」的指代关系，配合 [[rules.oper-change-record-query]] 使用。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

---END FILE---

---FILE: rules/change-on-way-company.md ---
---
type: rule
title: 变更在途判定（企业维度）
page_key: rule.change-on-way-company
domain: 企业变更与运营变更
status: draft
aliases: [在途变更规则, changeHasBusiOnWay]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeHasBusiOnWay
contract_version: "0.1"
---

企业 [[tables.cust_company_info]] 的 `cust_status='CHANGE'` 即视为存在在途变更业务，`changeHasBusiOnWay` 返回 true。该判定决定变更入口是否可用以及页面跳转是否走运营中台变更待办页，口径见 [[calibers.company-change-on-way]]，状态来源见 [[processes.cust-company-info-status]]。

## 需求背景

变更审批在运营中台执行，平台侧需要低成本判断「企业是否有事在办」，因此选择企业生命周期状态这一结果态作为判据，而不是聚合 [[tables.cust_change_record]] 集合。与准入校验 [[rules.change-application-admission]] 互为补充：一个看企业状态，一个看准入审核状态。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeHasBusiOnWay`。

```ground:rule
name: 变更在途判定（企业维度）
content: 企业 cust_status='CHANGE' 即视为存在在途变更业务，changeHasBusiOnWay 返回 true
impact: 决定变更入口是否可用、页面跳转是否走运营中台变更待办页
field_targets:
  - cust_company_info.cust_status
evidence: code_path:CustChangeApplication.java:changeHasBusiOnWay
```

---END FILE---

---FILE: rules/change-application-admission.md ---
---
type: rule
title: 变更申请准入校验
page_key: rule.change-application-admission
domain: 企业变更与运营变更
status: draft
aliases: [changeEnable, 变更准入]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeEnable
contract_version: "0.1"
---

企业 [[tables.cust_company_info]] 的 `check_status='CUST_CHECK_CHECKING'` 时 `changeEnable` 返回 false，不允许发起变更；企业不存在时同样返回 false。口径见 [[calibers.company-change-enable]]，与在途判定 [[rules.change-on-way-company]] 共同构成变更入口的两道闸门。

## 需求背景

企业准入审核在途期间，企业主体信息仍可能被审核结果改写，此时开放变更会产生两条互相冲突的审批链路；因此变更发起前必须做准入前置校验。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeEnable`。

```ground:rule
name: 变更申请准入校验
content: 企业 check_status='CUST_CHECK_CHECKING' 时 changeEnable 返回 false，不允许发起变更
impact: 变更提交前置校验；企业不存在时同样返回 false
field_targets:
  - cust_company_info.check_status
evidence: code_path:CustChangeApplication.java:changeEnable
```

---END FILE---

---FILE: rules/change-cfg-identity-match.md ---
---
type: rule
title: 变更配置按身份维度匹配
page_key: rule.change-cfg-identity-match
domain: 企业变更与运营变更
status: draft
aliases: [变更项清单匹配, 配置匹配规则]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
---

企业类型按 `client_type` + `identify_style` + `cust_type` + `head_company` + `enable='Y'` 匹配 [[tables.cust_change_cfg]]；个人类型不叠加 `head_company`。口径见 [[calibers.change-cfg-match-dimensions]] 与 [[calibers.change-cfg-enable]]，字段语义见配置表页，变更项标识见 [[concepts.item-code]]。

## 需求背景

不同端与认证方式下可变更的内容和所需材料不同，配置以多维组合表达适用性；个人客户不存在总公司概念，若仍拼入 `head_company` 条件将匹配不到任何配置，因此按客户类型分支处理。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.list`。

```ground:rule
name: 变更配置按身份维度匹配
content: 企业类型按 client_type + identify_style + cust_type + head_company + enable='Y' 匹配；个人类型不叠加 head_company
impact: 决定不同端/认证方式/客户类型下可选的变更项清单
field_targets:
  - cust_change_cfg.client_type
  - cust_change_cfg.identify_style
  - cust_change_cfg.cust_type
  - cust_change_cfg.head_company
  - cust_change_cfg.enable
evidence: code_path:CustChangeApplication.java:list
```

---END FILE---

---FILE: rules/change-record-terminal-filter.md ---
---
type: rule
title: 变更单终态过滤
page_key: rule.change-record-terminal-filter
domain: 企业变更与运营变更
status: draft
aliases: [终态过滤, notIn 终态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

`CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 视为终态，取在途变更单时用 notIn 排除。口径见 [[calibers.change-record-terminal-status]]，状态全集见 [[processes.cust-change-record-status]]，该过滤是流程重建 [[rules.change-rebuild]] 的前置步骤。

## 需求背景

企业可以多次发起变更，历史已完结单据必须与在途单据区分开；以终态集合做反向过滤比枚举在途状态更稳妥，新增中间态时不需要改判据。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeRebuild`。

```ground:rule
name: 变更单终态过滤
content: CUST_CHECK_PASS / CUST_CHECK_REJECT 视为终态，取在途变更单时用 notIn 排除
impact: 流程重建与在途判断的基础口径
field_targets:
  - cust_change_record.status
evidence: code_path:CustChangeApplication.java:changeRebuild
```

---END FILE---

---FILE: rules/change-rebuild.md ---
---
type: rule
title: 流程重建（重新发起变更）
page_key: rule.change-rebuild
domain: 企业变更与运营变更
status: draft
aliases: [changeRebuild, 重新发起变更]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:changeRebuild
contract_version: "0.1"
---

流程重建取该企业最新一条非终态变更记录（过滤口径见 [[rules.change-record-terminal-filter]]），通过运营中台接口结束旧流程（备注：客户操作重新发起，拒绝旧流程），随后允许发起新流程；操作人须为当前企业，否则抛无权限。涉及字段见 [[tables.cust_change_record]]，终态判定见 [[processes.cust-change-record-status]] 中「重新发起」迁移与 [[calibers.change-record-terminal-status]]。

## 需求背景

客户在上一笔变更未走完时再次进入变更入口，需要「以新替旧」而不是并存两条在途流程；因此先结束旧流程，再放行新流程，保证同一企业同一时刻只有一条在途单。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.changeRebuild`。

```ground:rule
name: 流程重建（重新发起变更）
content: 取该企业最新一条非终态变更记录，通过运营中台接口结束旧流程（备注：客户操作重新发起，拒绝旧流程），随后允许发起新流程；操作人须为当前企业，否则抛无权限
impact: 同一企业可存在多次变更发起，旧单被拒结
field_targets:
  - cust_change_record.status
  - cust_change_record.oper_cust_id
  - cust_change_record.cust_id
evidence: code_path:CustChangeApplication.java:changeRebuild
```

---END FILE---

---FILE: rules/admin-phone-change-redirect.md ---
---
type: rule
title: 管理员手机号变更跳转判定
page_key: rule.admin-phone-change-redirect
domain: 企业变更与运营变更
status: draft
aliases: [getRedirectPage, 变更提交成功页跳转]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:getRedirectPage
contract_version: "0.1"
---

变更单含 `UN0012`/`UN0013`（识别口径见 [[calibers.admin-phone-change-item]]）且 `oper_cust_info` 中 `oldPersonId` 与 `personId` 对应手机号不同、且登录手机号 ≠ 新管理员手机号时，跳转变更提交成功页并回填新管理员手机/姓名；否则跳运营中台变更待办页。涉及 [[tables.cust_change_record]]、[[tables.cust_person_info]]，字段边界见 [[concepts.operator]]。

## 需求背景

管理员手机号变更后登录主体发生变化：旧管理员不应再进入变更待办，新管理员则需要看到提交成功结果页。判定必须三方比对（中台旧管理员手机号、中台新管理员手机号、当前登录手机号），避免仅凭变更项就误判。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.getRedirectPage`。

```ground:rule
name: 管理员手机号变更跳转判定
content: 变更单含 UN0012/UN0013 且 oper_cust_info 中 oldPersonId 与 personId 对应手机号不同、且登录手机号≠新管理员手机号时，跳转变更提交成功页并回填新管理员手机/姓名；否则跳运营中台变更待办页
impact: 变更管理员后旧管理员登录不再进入待办，新管理员看到提交成功页
field_targets:
  - cust_change_record.alter_type_id
  - cust_change_record.oper_cust_info
  - cust_person_info.phone
evidence: code_path:CustChangeApplication.java:getRedirectPage
```

---END FILE---

---FILE: rules/audit-callback-dispatch.md ---
---
type: rule
title: 运营中台审核回调分工
page_key: rule.audit-callback-dispatch
domain: 企业变更与运营变更
status: draft
aliases: [CustSyncEventProvider, isChangeBroadcast]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
---

`CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 回调由工作流审核执行器 `CustWorkflowAuditCommitProcessor` 处理，`CustSyncEventProvider.onEvent` 直接跳过（`isChangeBroadcast=true` 的变更广播除外）。这解释了 [[processes.cust-change-record-status]] 中两个终态迁移的 evidence 为何指向「跳过」而非写入。

## 需求背景

审批终态需要携带工作流上下文，只有执行器具备处理条件；事件提供者若重复处理会导致状态被写两次或覆盖，因此显式跳过，同时为变更广播保留独立通道。字段影响面见 [[concepts.change-status]]（变更单状态与企业准入状态分属两条线）。

## 版本演进

v0.1：首次登记，规则来自 `CustSyncEventProvider.onEvent`。

```ground:rule
name: 运营中台审核回调分工
content: CUST_CHECK_PASS / CUST_CHECK_REJECT 回调由工作流审核执行器 CustWorkflowAuditCommitProcessor 处理，CustSyncEventProvider.onEvent 直接跳过（isChangeBroadcast=true 的变更广播除外）
impact: 避免审批终态被重复处理，变更广播走独立通道
field_targets:
  - cust_change_record.status
  - cust_company_info.check_status
evidence: code_path:CustSyncEventProvider.java:onEvent
```

---END FILE---

---FILE: rules/oper-change-type-dict.md ---
---
type: rule
title: 运营人员变更类型字典
page_key: rule.oper-change-type-dict
domain: 企业变更与运营变更
status: draft
aliases: [CHANGE_TYPE_DESC, 变更类型映射]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC
  - code_path:OperChangeRecordApplication.java:toVO
contract_version: "0.1"
---

`change_type` 取值 `MANUAL`/`BATCH`/`AUTO_ASSIGN`/`AUTO_UPDATE`/`ASSET_AUDIT_SYNC`/`CUST_CHANGE_CALLBACK`，前端展示名由 `CHANGE_TYPE_DESC` 映射，未命中时回显原值。取值集合见 [[processes.oper-change-type]]，流水表见 [[tables.cust_oper_change_record]]。

## 需求背景

运营人员变更来源持续增加，字典映射必须对未知值保持降级可读（回显原值），否则新增来源在前端会显示为空；该策略保证流水列表不丢数据。

## 版本演进

v0.1：首次登记，规则来自 `OperChangeRecordApplication.CHANGE_TYPE_DESC` / `toVO`。

```ground:rule
name: 运营人员变更类型字典
content: change_type 取值 MANUAL/BATCH/AUTO_ASSIGN/AUTO_UPDATE/ASSET_AUDIT_SYNC/CUST_CHANGE_CALLBACK，前端展示名由 CHANGE_TYPE_DESC 映射，未命中时回显原值
impact: 运营人员变更流水的分类展示
field_targets:
  - cust_oper_change_record.change_type
evidence: code_path:OperChangeRecordApplication.java:CHANGE_TYPE_DESC / toVO
```

---END FILE---

---FILE: rules/oper-change-record-query.md ---
---
type: rule
title: 运营人员变更记录查询口径
page_key: rule.oper-change-record-query
domain: 企业变更与运营变更
status: draft
aliases: [queryByPersonId, 运营变更历史查询]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:OperChangeRecordApplication.java:queryByPersonId
contract_version: "0.1"
---

按 `person_id` 精确匹配、`enable='Y'`（见 [[calibers.oper-change-record-valid]]），按 `create_time` 倒序返回；`personId` 为空直接返回空列表。表见 [[tables.cust_oper_change_record]]，字段指代见 [[concepts.operator]]。

## 需求背景

联系人详情页展示运营变更历史时，只要当前绑定关系的历史轨迹，不要已失效行；空入参直接短路，避免全表扫描。倒序保证最新一次变更置顶。

## 版本演进

v0.1：首次登记，规则来自 `OperChangeRecordApplication.queryByPersonId`。

```ground:rule
name: 运营人员变更记录查询口径
content: 按 person_id 精确匹配、enable='Y'，按 create_time 倒序返回；personId 为空直接返回空列表
impact: 联系人详情页的运营变更历史列表
field_targets:
  - cust_oper_change_record.person_id
  - cust_oper_change_record.enable
  - cust_oper_change_record.create_time
evidence: code_path:OperChangeRecordApplication.java:queryByPersonId
```

---END FILE---

---FILE: rules/wechat-todo-notify.md ---
---
type: rule
title: 企微待办通知按节点与通知类型分发
page_key: rule.wechat-todo-notify
domain: 企业变更与运营变更
status: draft
aliases: [dispatchWechatNotify, 企微待办, 后补合作协议流程通知]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:BackAgreementProcessOperateListener.java:notice
  - code_path:BackAgreementProcessOperateListener.java:dispatchWechatNotify
contract_version: "0.1"
---

后补合作协议流程仅在 `taskNoticeType=2`（待办通知）时向 `taskNoticeUsers` 反查企微 `userId` 并发送 textcard 待办；其它通知类型忽略。反查不到企微用户时静默返回。

## 需求背景

流程审批待办需要触达到运营人员的企微账号，而流程侧只持有平台用户标识，因此需要一次反查；为避免非待办类通知打扰，仅对待办通知类型发送。该规则涉及 `sys_wx_user.user_id`、`tenant_project_approval.id`，与变更单链路无直接状态耦合，归属本域的外围通知能力。

## 版本演进

v0.1：首次登记，规则来自 `BackAgreementProcessOperateListener.notice` / `dispatchWechatNotify`。

```ground:rule
name: 企微待办通知按节点与通知类型分发
content: 后补合作协议流程仅在 taskNoticeType=2（待办通知）时向 taskNoticeUsers 反查企微 userId 并发送 textcard 待办；其它通知类型忽略
impact: 运营审批待办的企微触达；反查不到企微用户时静默返回
field_targets:
  - sys_wx_user.user_id
  - tenant_project_approval.id
evidence: code_path:BackAgreementProcessOperateListener.java:notice / dispatchWechatNotify
```

---END FILE---

---REVIEW: table | cust_change_record（企业变更单）---
三个问题需人工确认：
1. `scope.databases` 的物理库名在本次语义分析中未给出（仅有 `db` 标记），全部页面暂以 `unknown` 占位，需补充真实库名后统一回填。
2. 本次输入中 `reqdoc_claims` 内容被截断（仅见 `"claim":` 无正文），无法判定 `action=anchor` / `action=uncovered`，因此本批页面未产出任何双源（`code_path` + `reqdoc:slug`）锚点，也未产出 `(document_claim，未证实)` 的版本演进条目；若存在需求文档主张，需重新提供后按规则 4/5 回填。
3. `cust_change_record.alter_mode`（AlterModeEnum）与 `cust_person_info` 之外的 `act_procinst_status` 等字段仅在术语边界中被提及，未给出取值定义，暂不建页。
---END REVIEW---

---REVIEW: process | 客户变更单状态机（cust_change_record.status）---
`cust_change_record.status` 的取值 `'1'`（表默认值）、`CUSTS003`、`returnCust-<时间戳>`（13 条）均来自库表分布，代码层未见对应枚举声明。当前按「历史值/脏值」标注于 states 中（source=db_dist）。若这些取值承载未登记的业务语义（例如早期版本的退回标记），需补充来源后调整状态机与终态口径 [[caliber.change-record-terminal-status]] 的判定范围。
---END REVIEW---