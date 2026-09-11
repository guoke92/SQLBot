---FILE: tables/cust_project_rel.md ---
---
type: table
title: 企业项目关联表（cust_project_rel）
page_key: table.cust_project_rel
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_rel
  - 企业项目关联表
  - 项目关联企业表
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:cust_project_rel
  - code:CustProjectController.java
  - code:ProjectReportApplication.java
  - code:ProjectReportController.java
contract_version: "0.1"
---

# 企业项目关联表（cust_project_rel）

cust_project_rel 是产融侧「企业—项目」关联关系主表，一行代表一家企业在某个项目下的角色。项目台账的关联企业清单、客户角色展示、运营对接人 A/B、置顶提示均以此为数据源；产融来源（`transaction_platform = '产融平台'`）走本地表，不走洞察平台，分流判断见 [[calibers/project-ledger-source]]，关联企业取数见 [[calibers/chanyong-related-company]]。生效状态的流转见 [[processes/cust-project-rel-status]]，客户角色的跨源语义见 [[concepts/company-type]]。

## 需求背景

项目台账需要在详情页展示关联企业清单及客户角色，并按「置顶/需关注」场景给出运营对接人离职提示（见 [[calibers/deleted-operator-hint-for-chanyong]]）。因此本表需承载：单值客户角色（弹窗中为单选项）、运营对接人 A（单值，存 operation_id 或 OP00x 编码）、运营对接人 B（多选，DB 以 JSON 数组字符串存放，读取时按 JSON 解析）、运营组别、置顶标识、开通状态与逻辑删除标识。对接人展示时需经 OperCustFacade 转姓名；置顶场景下后端需检查对接人是否为离职人员，生成 text 提示并回写。

## 版本演进

- `status` 存在历史脏数据：除 `0`（未生效）与 `1`（已生效）外，DB 中还出现带首尾空格的 ` 1 `，读取侧需容错。
- `company_type` 存在拼写变体 `PLATFORM_OPREATOR_COMPANY`（疑似历史脏数据），与枚举值 `PLATFORM_OPERATOR_COMPANY` 并存。
- `config_model` 实测取值全部为 admin，未观察到多配置模式的演进痕迹。
- `remark` 列已被复用为产品编码承载列（实测写入 ACFLOW / RVSFACTOR_PC / BEECREDIT 等 productCode），语义偏离列名。
- `ref_cust_project_rel_cust_company_info` 作为回连 cust_company_info 的关联企业 code，在 getCompaniesByProjectId 中作为过滤条件使用。

```ground:fields
table: cust_project_rel
fields:
  - name: status
    meaning: "项目关联记录状态（0=未生效/待生效，1=已生效）；由 updateRelPrjStatus 接口在满足条件时从 0 置 1"
    evidence: db
  - name: project_open_status
    meaning: "项目开通状态：OPENED=已开通 / NOT_OPEN=未开通"
    evidence: db
  - name: enable
    meaning: "逻辑删除标识：Y=有效，N=已失效（查询均以 enable='Y' 过滤）"
    evidence: code
  - name: company_type
    meaning: "客户角色（单值，只取一个）：CORE/FINANCE/SUPPLIER/DEALER/PROJECT_COMPANY/CORE_MANAGER/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY；DB 存在拼写变体 PLATFORM_OPREATOR_COMPANY（疑似历史脏数据）"
    evidence: db
  - name: op_contact_a
    meaning: "运营对接人A：存 operation_id（数字 ID 或 OP00x 编码），展示时经 OperCustFacade 转姓名"
    evidence: code
  - name: op_contact_b
    meaning: '运营对接人B（多选）：DB 以 JSON 数组字符串存储，如 ["OP002","OP003"]，空为 []；读取时按 JSON 解析'
    evidence: code
  - name: op_contact_a_group
    meaning: "运营组别（与 op_contact_a 联动的组名/组 ID）"
    evidence: db
  - name: top_flag
    meaning: "置顶/需关注标识：'1' 时后端检查运营对接人是否为离职人员，生成 text 提示并回写"
    evidence: code
  - name: remark
    meaning: "备注列；DB 实测被写入 productCode（ACFLOW/RVSFACTOR_PC/BEECREDIT 等），语义被复用为产品编码承载列"
    evidence: db
  - name: ref_cust_project_rel_cust_company_info
    meaning: "关联企业 code，用于回连 cust_company_info（getCompaniesByProjectId 中以其过滤)"
    evidence: code
  - name: config_model
    meaning: "项目配置模式，DB 实测全部为 admin"
    evidence: db
```

相关页面：[[tables/cust_project_code_record]]（同类角色字段的多值形态）、[[concepts/data-source]]（同一「数据来源」词的分域歧义）。
---END FILE---

---FILE: tables/cust_project_pushcust.md ---
---
type: table
title: 推送企业表（cust_project_pushcust）
page_key: table.cust_project_pushcust
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_pushcust
  - 推送企业表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:cust_project_pushcust
contract_version: "0.1"
---

# 推送企业表（cust_project_pushcust）

cust_project_pushcust 记录「推送企业」与其默认项目之间的跨系统跳转链路。它不承载报表指标，而是为项目台账/企业视图提供 SSO 侧的系统归属，使「推送企业的默认项目」能够从起始系统渠道跳转至目标系统渠道。相关概念歧义见 [[concepts/data-source]]。

## 需求背景

推送企业的默认项目需要在不同系统之间跳转：用户在起始系统的 SSO 渠道点击后，需要被引导到目标系统渠道。本表以「起始渠道 → 目标渠道」成对的字段承载该链路，因此在报表/台账侧只作为跳转参数来源，不参与统计口径计算（统计口径见 [[calibers/project-statistics-list-base]]）。

## 版本演进

语义分析未提供该表的历史值分布与迁移记录，字段值域仅由代码侧使用方式反推，暂无版本演进证据。

```ground:fields
table: cust_project_pushcust
fields:
  - name: "source_sso_channel / target_sso_channel"
    meaning: "SSO 起始系统渠道 → 跳转系统渠道，表征「推送企业的默认项目」的跨系统跳转链路"
    evidence: code
```
---END FILE---

---FILE: tables/cust_project_code_record.md ---
---
type: table
title: 企业项目码录入记录表（cust_project_code_record）
page_key: table.cust_project_code_record
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_code_record
  - 企业项目码输入记录表
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:cust_project_code_record
contract_version: "0.1"
---

# 企业项目码录入记录表（cust_project_code_record）

cust_project_code_record 记录企业项目码的录入过程：录入来源、录入是否成功、以及提交时企业所持有的角色集合。它是「录入环节」的事实留存，与 [[tables/cust_project_rel]]（生效后的关联关系）构成前后两段：本表记录提交时的角色快照，关联表记录生效后的单值角色。

## 需求背景

企业注册与建站流程需要对企业输入的项目码做校验与留痕，区分来源渠道（用户自助注册 / PC 建站 / 产品中心 / 产品中心-企业认证成功），并记录该次提交是否正确。提交时企业可能同时具备多个角色，因此本表以 JSON 数组形式保存角色集合，作为审计与回溯依据；而项目台账侧的客户角色展示仍取关联表的单值字段，两者的差异见 [[concepts/company-type]]。

## 版本演进

本表字段的取值来源已演进为多渠道并存（userCompanyRegister、PC_BUILD、产品中心、产品中心-企业认证成功），说明录入入口从单一注册链路扩展为多入口；角色的多值化保存形态与关联表的单值形态长期并存，未见归一化动作。

```ground:fields
table: cust_project_code_record
fields:
  - name: status
    meaning: "企业项目码输入记录是否正确状态，Y/N"
    evidence: db
  - name: type
    meaning: "企业录入码来源类型：userCompanyRegister / PC_BUILD / 产品中心 / 产品中心-企业认证成功"
    evidence: db
  - name: company_type
    meaning: '该记录提交时的企业角色集合（JSON 数组形式，如 ["CORE","SUPPLIER"]）；与 cust_project_rel.company_type 单值形态不同'
    evidence: db
```
---END FILE---

---FILE: tables/wechat_project_approval_apply.md ---
---
type: table
title: 立项审批申请表（wechat_project_approval_apply）
page_key: table.wechat_project_approval_apply
domain: 项目报表/统计/上报
status: draft
aliases:
  - wechat_project_approval_apply
  - 企微立项审批申请表
  - 项目立项统计表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
  - code:ProjectStatisticsRemindApplication.java
contract_version: "0.1"
---

# 立项审批申请表（wechat_project_approval_apply）

wechat_project_approval_apply 是「项目立项统计」主题的事实表，承载企微审批同步而来的立项单据，并叠加统计侧维护的展示列与人工可编辑列。项目阶段流转见 [[processes/project-phase]]，审批状态见 [[processes/project-approval-status]]，数据来源见 [[processes/project-data-source]]，列表基础口径见 [[calibers/project-statistics-list-base]]，审批通过口径见 [[calibers/project-ledger-approved]]。

## 需求背景

立项统计页需要按「金融科技业务 + SaaS/SaaS+本地化」范围展示、导出、下拉字典与提醒（见 [[calibers/project-statistics-list-base]]、[[calibers/missing-solution-manager-remind]]），并支持人工编辑方案经理、首笔落地时间等字段。为此本表既保留审批同步字段（sp_type、system_delivery、act_procinst_status、project_phase 等），又扩展出统计侧冗余列（statics_op_time/statics_op_user），并要求方案经理姓名与企微 userId 冗余列联动维护（见 [[rules/manager-wechat-identity-validation]]）、前方案经理前置合并（见 [[rules/old-solution-manager-merge]]）。字段变更需落历史，见 [[tables/wechat_project_approval_apply_field_history]] 与 [[rules/edit-whitelist-and-field-history]]。

## 版本演进

- `project_phase` 历史上存在 `TERMINATION` 取值，读取时归一为 `HANG`；「立项阶段」仅作为展示态，不入库。
- `data_source` 引入 `MANUAL` 以承载模拟立项（spNo 以 MN 开头），与企微同步的真实立项并存，编号规则见 [[rules/manual-project-spno]]。
- `first_settlement_time` 的编辑语义为例外：非空覆盖、null 清空，不遵循其他字符串列的 null 跳过约定；该列变更会触发阶段联动（见 [[rules/first-settlement-to-operation-phase]]）。
- 本期仅放开 `custom_field_statistics_one` 作为编辑独占列，说明自定义字段能力处于逐列开放阶段。

```ground:fields
table: wechat_project_approval_apply
fields:
  - name: sp_type
    meaning: "审批类型；统计页固定过滤 金融科技业务"
    evidence: code
  - name: system_delivery
    meaning: "系统交付类型（统计范围：SaaS / Saas+本地化）"
    evidence: code
  - name: act_procinst_status
    meaning: "企微审批流程状态：1=审批中，2=审批通过"
    evidence: code
  - name: project_type
    meaning: "项目类型：MAIN=主项目 / SUB=子项目"
    evidence: code
  - name: project_phase
    meaning: "项目阶段：IMPLEMENTATION=实施阶段 / OPERATION=持续运营 / HANG=挂起；历史值 TERMINATION 归一为 HANG；立项阶段仅作展示态不入库"
    evidence: code
  - name: ka_white_label
    meaning: "KA 是否贴牌：Y=是 / N=否"
    evidence: code
  - name: data_source
    meaning: "数据来源：MANUAL=模拟立项（spNo 以 MN 开头） / WECHAT=真实立项"
    evidence: code
  - name: product_type_arr
    meaning: '产品类型编码 JSON 数组，如 ["1","9"]；配套 product_type 存中文逗号串（冗余展示列）'
    evidence: code
  - name: solution_manager
    meaning: "方案经理姓名（多人以逗号分隔 CSV）；仅在 solution_manager_wxid 联动维护时同步写入"
    evidence: code
  - name: solution_manager_wxid
    meaning: '方案经理企微 userId 冗余列（JSON 数组字符串 ["id1","id2"]），用于按 wxid 精确过滤'
    evidence: code
  - name: old_solution_manager
    meaning: "前方案经理，姓名 CSV；变更方案经理时由 mergeOldSolutionManager 前置合并旧值"
    evidence: code
  - name: "statics_op_time / statics_op_user"
    meaning: "统计侧最新操作时间/操作人（列表展示用 updateTime/updateUser 取自该两列覆盖）"
    evidence: code
  - name: first_settlement_time
    meaning: "首笔落地时间；编辑语义例外——非空覆盖/null 清空（不遵循其他字符串列的 null 跳过约定）"
    evidence: code
  - name: custom_field_statistics_one
    meaning: "自定义字段一；本期唯一放开的编辑独占列"
    evidence: code
```
---END FILE---

---FILE: tables/wechat_project_approval_apply_field_history.md ---
---
type: table
title: 立项审批字段变更历史表（wechat_project_approval_apply_field_history）
page_key: table.wechat_project_approval_apply_field_history
domain: 项目报表/统计/上报
status: draft
aliases:
  - wechat_project_approval_apply_field_history
  - 立项字段历史表
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 立项审批字段变更历史表（wechat_project_approval_apply_field_history）

本表记录 [[tables/wechat_project_approval_apply]] 各列的人工/批量/导入变更轨迹，是「谁在什么路径下改了什么」的审计落点。它不参与列表展示与统计口径计算，但决定了同步保护与差异写库的可追溯性。

## 需求背景

立项统计的编辑保存只对白名单列做 diff 写库，并同步写入本表；企微同步 Job 在写库前需跳过已被人工写入的保护字段，避免覆盖人工结果（见 [[rules/edit-whitelist-and-field-history]]）。因此本表需要区分变更来源：页面编辑、批量变更、模拟立项、导入，四类来源对应不同的写入路径与责任方。

## 版本演进

`change_source` 当前已有 EDIT / BATCH / MANUAL_CREATE / IMPORT 四种取值，反映写入入口由单一页面编辑扩展为批量、模拟立项与导入并存；未观察到该列的更早取值形态。

```ground:fields
table: wechat_project_approval_apply_field_history
fields:
  - name: change_source
    meaning: "字段历史来源：EDIT=页面编辑 / BATCH=批量变更 / MANUAL_CREATE=模拟立项 / IMPORT=导入"
    evidence: code
```
---END FILE---

---FILE: processes/project-approval-status.md ---
---
type: process
title: 项目立项审批状态
page_key: process.project-approval-status
domain: 项目报表/统计/上报
status: draft
aliases:
  - 审批状态流转
  - act_procinst_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 项目立项审批状态

审批状态描述一条立项单据在企微审批中的进度，落在 [[tables/wechat_project_approval_apply]] 的 `act_procinst_status`。它是「审批通过口径」的判定基础（见 [[calibers/project-ledger-approved]]），也是首笔落地时间→项目阶段联动的前置条件（见 [[rules/first-settlement-to-operation-phase]]）。

## 需求背景

统计侧只消费「审批通过」这一状态：主项目名称字典、缺方案经理提醒、阶段联动均要求 `act_procinst_status = '2'`（缺方案经理提醒口径见 [[calibers/missing-solution-manager-remind]]）。「审批中」状态用于展示与人工识别，不产生统计侧副作用。状态值由企微审批同步外部写入，系统内部仅做消费，不做状态推进。

## 版本演进

当前值域为 1（审批中）、2（审批通过）两态，未观察到 3 及以上的取值或历史迁移记录；同步链路与状态机的关系尚未有写入侧代码证据，仅能确认消费点。

```ground:state_machine
name: "项目立项审批状态"
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: "1"
    label: "审批中"
    source: code_enum
  - value: "2"
    label: "审批通过"
    source: code_enum
transitions:
  - from: "1"
    event: "企微审批通过（外部同步写入）"
    to: "2"
    evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved（仅消费 2 值，非写入点）"
```

相关：[[processes/project-data-source]]、[[processes/project-phase]]。
---END FILE---

---FILE: processes/project-phase.md ---
---
type: process
title: 项目阶段（立项统计）
page_key: process.project-phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目阶段流转
  - project_phase
  - projectPhase
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
---

# 项目阶段（立项统计）

项目阶段落在 [[tables/wechat_project_approval_apply]] 的 `project_phase`，用于表达立项单据当前处于实施、持续运营还是挂起。它与项目台账维度的「项目状态 project_status」不是同一概念，二者的分域说明见 [[concepts/project-phase]]。

## 需求背景

统计侧需要区分「实施阶段」与「持续运营」以支持运营口径统计；当审批已通过且首笔落地时间被更新为非空时，系统自动把阶段推进到 OPERATION（见 [[rules/first-settlement-to-operation-phase]]）。该联动在编辑保存、导入、开发用导入三条写入路径均生效。挂起（HANG）作为人工/历史状态存在，任何非 OPERATION 阶段在满足条件时都会被覆盖为 OPERATION。

## 版本演进

历史值 `TERMINATION`（终止）在读取时被归一为 `HANG`，说明阶段值域曾发生收敛；「立项阶段」只作为展示态存在，不入库。归一逻辑由 normalizeLegacyProjectPhaseCode 承担。

```ground:state_machine
name: "项目阶段（项目立项统计）"
field: wechat_project_approval_apply.project_phase
states:
  - value: "IMPLEMENTATION"
    label: "实施阶段"
    source: code_enum
  - value: "OPERATION"
    label: "持续运营"
    source: code_enum
  - value: "HANG"
    label: "挂起"
    source: code_enum
  - value: "TERMINATION"
    label: "终止（历史值，读取时归一为 HANG）"
    source: code_enum
transitions:
  - from: "IMPLEMENTATION"
    event: "审批通过 + 首笔落地时间被更新为非空 + 当前阶段非 OPERATION"
    to: "OPERATION"
    evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
  - from: "HANG"
    event: "同上（任何非 OPERATION 阶段均被覆盖）"
    to: "OPERATION"
    evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
  - from: "TERMINATION"
    event: "读取归一化 normalizeLegacyProjectPhaseCode"
    to: "HANG"
    evidence: "code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode"
```
---END FILE---

---FILE: processes/project-data-source.md ---
---
type: process
title: 模拟立项/真实立项数据来源
page_key: process.project-data-source
domain: 项目报表/统计/上报
status: draft
aliases:
  - data_source
  - 模拟立项
  - 真实立项
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
---

# 模拟立项/真实立项数据来源

`data_source` 描述 [[tables/wechat_project_approval_apply]] 中一条立项单据的产生方式：由企微同步而来的真实立项，或由后端手工/开发用导入产生的模拟立项。它决定编号形态（spNo 是否以 MN 开头）与数据可信度，详见 [[rules/manual-project-spno]]。

## 需求背景

为支持统计页在无真实企微审批数据时的演示与联调，系统允许手工新增模拟立项：字段与真实立项一致，但数据来源标记为 MANUAL，编号由后端按固定表达式生成，列表与导出按 spNo 前缀识别。真实立项保持 WECHAT 取值。「数据来源」这一中文词在项目台账侧另有 source 语义（产融/讯易链），两者的分域见 [[concepts/data-source]]。

## 版本演进

MANUAL 来源为演示/联调场景引入，其编号规则由 generateManualSpNo 固定表达式承载；开发用导入链路（buildManualEntityForInsert）可批量插入模拟立项空白编号行，说明模拟能力已从单条手工新增扩展到批量导入。

```ground:state_machine
name: "模拟立项/真实立项数据来源"
field: wechat_project_approval_apply.data_source
states:
  - value: "MANUAL"
    label: "模拟立项（spNo 以 MN 开头）"
    source: code_enum
  - value: "WECHAT"
    label: "真实立项"
    source: code_enum
transitions:
  - from: "无"
    event: "manualCreate / 开发用导入空白编号行"
    to: "MANUAL"
    evidence: "code_path:ProjectStatisticsApplication.java:manualCreate + ProjectStatisticsDevImportApplication.java:buildManualEntityForInsert"
```
---END FILE---

---FILE: processes/cust-project-rel-status.md ---
---
type: process
title: 企业项目关联生效状态
page_key: process.cust-project-rel-status
domain: 项目报表/统计/上报
status: draft
aliases:
  - cust_project_rel.status
  - 关联生效状态
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustProjectController.java
  - db:cust_project_rel
contract_version: "0.1"
---

# 企业项目关联生效状态

该状态落在 [[tables/cust_project_rel]] 的 `status`，表示某企业在某项目下的关联关系是否已生效。它影响关联企业清单是否进入生效口径，与逻辑删除标识 `enable` 是两套独立过滤条件。

## 需求背景

企业关联项目在满足业务前置条件（产品为 ACFLOW/ORDER，且该角色下不存在已生效项目）时，由 updateRelPrjStatus 接口把 status 从 0 置为 1，写库值取 `EnableEnum.Y.getDictKey()`。查询侧普遍叠加 `enable = 'Y'` 过滤（如 [[calibers/chanyong-related-company]]），因此「已删除」与「未生效」需分别判断。

## 版本演进

DB 中出现带首尾空格的 ` 1 ` 值，属历史脏数据，读取与比较需容错；未见从 1 回退到 0 的迁移路径证据。

```ground:state_machine
name: "企业项目关联生效状态"
field: cust_project_rel.status
states:
  - value: "0"
    label: "未生效"
    source: db_dist
  - value: "1"
    label: "已生效"
    source: db_dist
  - value: "' 1 '"
    label: "已生效（历史脏数据，带首尾空格）"
    source: db_dist
transitions:
  - from: "0"
    event: "调用 updateRelPrjStatus，且产品为 ACFLOW/ORDER 且该角色下无生效项目时"
    to: "1"
    evidence: "code_path:CustProjectController.java:updateRelPrjStatus（set status = EnableEnum.Y.getDictKey()）"
```
---END FILE---

---FILE: calibers/chanyong-related-company.md ---
---
type: caliber
title: 产融侧关联企业口径
page_key: caliber.chanyong-related-company
domain: 项目报表/统计/上报
status: draft
aliases:
  - 关联企业查询口径
  - getCompaniesByProjectId
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
contract_version: "0.1"
---

# 产融侧关联企业口径

项目台账查询关联企业时，当来源判定为产融（见 [[calibers/project-ledger-source]]），不再调用洞察平台，而是直接读本地 [[tables/cust_project_rel]]，并以项目 ID + 有效标识过滤，通过 `ref_cust_project_rel_cust_company_info` 回连 cust_company_info 取企业信息。

## 需求背景

关联企业列表需要与项目口径保持一致：产融来源的项目只认本地关联表，避免与讯易链/洞察平台的数据混流。角色维度在该路径下保持原值不做跨源转换（对比 [[calibers/company-type-cross-source-mapping]]）。

## 版本演进

本口径以 `enable = 'Y'` 作为有效过滤，说明逻辑删除已成为本表的默认过滤约定；未观察到该口径的历史版本差异。

```ground:caliber
name: "产融侧关联企业口径"
predicate: "cust_project_rel.enable = 'Y' AND cust_project_rel.project_id = :projectId"
scope: "项目台账→关联企业查询（source='产融' 时走本地表，不走洞察平台）"
evidence: "code_path:ProjectReportApplication.java:getCompaniesByProjectId"
```
---END FILE---

---FILE: calibers/project-statistics-list-base.md ---
---
type: caliber
title: 项目立项统计列表基础口径
page_key: caliber.project-statistics-list-base
domain: 项目报表/统计/上报
status: draft
aliases:
  - 立项统计基础口径
  - 金融科技业务 SaaS 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 项目立项统计列表基础口径

立项统计页的列表、导出、下拉字典与提醒都以同一组过滤条件为底座：审批类型固定为「金融科技业务」，系统交付类型限定在 SaaS / Saas+本地化。该底座作用在 [[tables/wechat_project_approval_apply]] 上，是全站统计范围的第一道收口。

## 需求背景

业务上只统计金融科技业务线且以 SaaS 形态交付的立项，避免把其他审批类型与本地化-only 交付混入统计。审批通过与否在此之上另行叠加（见 [[calibers/project-ledger-approved]]）；缺方案经理提醒同样复用该底座（见 [[calibers/missing-solution-manager-remind]]）。字段取值定义见 [[tables/wechat_project_approval_apply]]。

## 版本演进

`saaS / Saas+本地化` 的并列取值说明交付形态至少经历一次扩充（从纯 SaaS 到含本地化的混合交付）；sp_type 的过滤值以中文字面量写死在查询中，尚无字典化证据。

```ground:caliber
name: "项目立项统计列表基础口径"
predicate: "wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.system_delivery IN ('SaaS','Saas+本地化')"
scope: "项目立项统计页列表/导出/字典/提醒"
evidence: "code_path:ProjectStatisticsApplication.java:buildPageWrapper + ProjectStatisticsApplication.java:listDistinctMainProjectNamesFinTechSaasApproved"
```
---END FILE---

---FILE: calibers/project-ledger-approved.md ---
---
type: caliber
title: 项目台账审批通过口径
page_key: caliber.project-ledger-approved
domain: 项目报表/统计/上报
status: draft
aliases:
  - 审批通过口径
  - act_procinst_status=2
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 项目台账审批通过口径

以 `act_procinst_status = '2'` 作为「审批通过」的统一判定。该条件既用于生成主项目名称字典，也作为首笔落地时间触发项目阶段联动的必要前置。状态定义见 [[processes/project-approval-status]]。

## 需求背景

只有已通过企微审批的立项才允许进入统计口径与自动化流转：主项目名称下拉只列通过审批的主项目；若单据未通过审批，即使首笔落地时间被更新也不触发阶段变更（见 [[rules/first-settlement-to-operation-phase]]）。该口径与基础统计口径（[[calibers/project-statistics-list-base]]）叠加使用。

## 版本演进

审批状态当前只消费 1/2 两值，口径判定固定取 2；未见对「审批中」「驳回」等状态的独立统计口径。

```ground:caliber
name: "项目台账审批通过口径"
predicate: "wechat_project_approval_apply.act_procinst_status = '2'"
scope: "主项目名称字典；首笔落地时间→项目阶段联动的触发前置"
evidence: "code_path:ProjectStatisticsApplication.java:listDistinctMainProjectNamesFinTechSaasApproved + ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
```
---END FILE---

---FILE: calibers/missing-solution-manager-remind.md ---
---
type: caliber
title: 缺方案经理提醒口径
page_key: caliber.missing-solution-manager-remind
domain: 项目报表/统计/上报
status: draft
aliases:
  - 缺方案经理提醒
  - remindMissingSolutionManager
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsRemindApplication.java
contract_version: "0.1"
---

# 缺方案经理提醒口径

每个统计日扫描已审批通过、交付形态在统计范围内、申请时间不早于固定起始日、且尚未维护方案经理的立项，形成企微提醒清单。它是 [[calibers/project-statistics-list-base]] 与 [[calibers/project-ledger-approved]] 的叠加，再补上「方案经理为空」与有效标识两个条件。

## 需求背景

为避免立项通过后长期无人跟进方案，系统每日 10:00 通过企微推送缺方案经理的项目，并支持通过 Nacos 开关 `project.statistics.missing.planmgr.remind.enable` 关闭。方案经理本身的落库需满足企微部门归属校验（见 [[rules/manager-wechat-identity-validation]]），字段定义见 [[tables/wechat_project_approval_apply]]。

## 版本演进

固定起始日的存在说明提醒只覆盖某时间点之后申请的项目，属口径引入时的历史边界；开关化的 Nacos 配置表明该提醒曾因打扰或数据质量原因需要可关闭。

```ground:caliber
name: "缺方案经理提醒口径"
predicate: "sp_type='金融科技业务' AND system_delivery IN ('SaaS','Saas+本地化') AND act_procinst_status='2' AND apply_start_time >= 固定起始日 AND enable='Y' AND solution_manager 为空"
scope: "每日 10:00 企微提醒（可通过 Nacos project.statistics.missing.planmgr.remind.enable 关闭）"
evidence: "code_path:ProjectStatisticsApplication.java:listApprovedMissingSolutionManagerForRemind + ProjectStatisticsRemindApplication.java:remindMissingSolutionManager"
```
---END FILE---

---FILE: calibers/deleted-operator-hint-for-chanyong.md ---
---
type: caliber
title: 产融项目运营人员离职提示口径
page_key: caliber.deleted-operator-hint-for-chanyong
domain: 项目报表/统计/上报
status: draft
aliases:
  - 离职提示口径
  - checkDeletedOperatorsForCompanies
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
contract_version: "0.1"
---

# 产融项目运营人员离职提示口径

当产融来源的项目被标记为置顶/需关注时，系统挑出该项目下角色为核心（CORE）与金融（FINANCE）且有效的关联记录，检查其运营对接人是否已离职，并把提示文本回写到台账 text 字段。

## 需求背景

置顶项目需要重点跟进，若对接人已离职则必须提示，避免出现无人响应的项目。角色限定为 CORE/FINANCE，说明仅这两类角色的对接人被视为关键联系人；离职判定使用统一的人员口径（见 [[calibers/deleted-operator]]）。相关字段定义见 [[tables/cust_project_rel]]。

## 版本演进

提示能力以 `top_flag = '1'` 为触发条件，属「需关注」场景的扩展能力；未观察到提示范围从 CORE/FINANCE 进一步扩大的证据。

```ground:caliber
name: "产融项目运营人员离职提示口径"
predicate: "cust_project_rel.project_id = :projectId AND top_flag = '1' AND company_type IN ('CORE','FINANCE') AND enable = 'Y'"
scope: "项目台账 text 字段生成（产融来源）"
evidence: "code_path:ProjectReportController.java:checkDeletedOperatorsForCompanies"
```
---END FILE---

---FILE: calibers/deleted-operator.md ---
---
type: caliber
title: 已离职运营人员口径
page_key: caliber.deleted-operator
domain: 项目报表/统计/上报
status: draft
aliases:
  - 离职人员判定口径
  - getDeletedOperatorIds
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
  - code:CustProjectController.java
contract_version: "0.1"
---

# 已离职运营人员口径

运营对接人、查验对接人、风控对接人的离职校验统一取 `operation_user.deleted = 'Y' AND enable = 'Y'` 判定，作为提示文本与联系人有效性判断的唯一依据。它是 [[calibers/deleted-operator-hint-for-chanyong]] 的底层判定。

## 需求背景

对接人以 ID 或编码存放于关联表（见 [[tables/cust_project_rel]]），姓名需回查人员数据；离职状态同时出现在 deleted 与 enable 两列，业务上以二者同时成立为「已离职且记录有效」。项目台账与客户项目两处控制器都实现同一判定，保证口径一致。

## 版本演进

同一判定在 ProjectReportController 与 CustProjectController 中各自实现（getDeletedOperatorIds），属重复实现，未见抽取为公共服务的演进证据。

```ground:caliber
name: "已离职运营人员口径"
predicate: "operation_user.deleted = 'Y' AND operation_user.enable = 'Y'"
scope: "所有运营对接人/查验对接人/风控对接人的离职校验与提示文本生成"
evidence: "code_path:ProjectReportController.java:getDeletedOperatorIds + CustProjectController.java:getDeletedOperatorIds"
```
---END FILE---

---FILE: calibers/project-ledger-source.md ---
---
type: caliber
title: 项目台账 source 判定口径
page_key: caliber.project-ledger-source
domain: 项目报表/统计/上报
status: draft
aliases:
  - source 判定
  - 产融/讯易链分流
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
contract_version: "0.1"
---

# 项目台账 source 判定口径

项目台账的 source 由交易平台列直接判定：`transaction_platform = '产融平台'` 即为产融，否则归为讯易链。该判定决定详情、导出、关联企业查询是读本地表还是调洞察平台。

## 需求背景

产融与讯易链两套系统的企业、角色数据模型不同，因此必须在入口处分流：产融走本地关联表（见 [[calibers/chanyong-related-company]]），讯易链走洞察平台并需做角色与认证状态的跨源映射（见 [[calibers/company-type-cross-source-mapping]]、[[calibers/cust-build-status-xyc-mapping]]）。该词与立项统计侧的「数据来源」同名异义，见 [[concepts/data-source]]。

## 版本演进

以白名单式判定（等于产融平台则产融，否则讯易链）意味着新增交易平台会被默认归入讯易链，属需要关注的隐式默认；未观察到判定条件的其他版本。

```ground:caliber
name: "项目台账 source 判定口径"
predicate: "transaction_platform = '产融平台' → source='产融'；否则 source='讯易链'"
scope: "详情/导出/关联企业查询的本地表 vs 洞察平台分流"
evidence: "code_path:ProjectReportApplication.java:exportProjectReport（source 判定段）"
```
---END FILE---

---FILE: calibers/cust-build-status-xyc-mapping.md ---
---
type: caliber
title: custBuildStatus 讯易链映射口径
page_key: caliber.cust-build-status-xyc-mapping
domain: 项目报表/统计/上报
status: draft
aliases:
  - 认证状态映射
  - convertCustBuildStatusToChinese
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
contract_version: "0.1"
---

# custBuildStatus 讯易链映射口径

项目企业报表在讯易链来源下，需要把洞察平台的认证状态码翻译为中文展示：CUSTS003→认证成功，CUSTS005→待客户认证，CUSTS002/CUSTS001/CUSTS006→待审核，CUSTS004→审核拒绝。

## 需求背景

认证状态由外部系统以编码返回，报表侧需统一为中文文案供业务阅读。该映射只在讯易链分支使用（来源判定见 [[calibers/project-ledger-source]]）；多个编码归并为「待审核」说明外部状态机比展示态更细，报表侧做了收敛。

## 版本演进

CUSTS001/CUSTS002/CUSTS006 三码合并为「待审核」，属展示层收敛；未观察到映射表的更早版本或反向映射。

```ground:caliber
name: "custBuildStatus 讯易链映射口径"
predicate: "CUSTS003→认证成功；CUSTS005→待客户认证；CUSTS002/CUSTS001/CUSTS006→待审核；CUSTS004→审核拒绝"
scope: "项目企业报表认证状态中文展示"
evidence: "code_path:ProjectReportApplication.java:convertCustBuildStatusToChinese"
```
---END FILE---

---FILE: calibers/company-type-cross-source-mapping.md ---
---
type: caliber
title: companyType 跨源映射口径
page_key: caliber.company-type-cross-source-mapping
domain: 项目报表/统计/上报
status: draft
aliases:
  - 角色跨源映射
  - processCompanyTypeBySource
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
contract_version: "0.1"
---

# companyType 跨源映射口径

项目企业报表的 companyType 查询参数需按来源转换：讯易链侧把 CORE 映射为 ce（XycCompanyType.CE）、FINANCE 映射为 cpt（XycCompanyType.CPT）；产融侧保持原值不变（见 [[calibers/project-ledger-source]]）。

## 需求背景

两套系统的角色编码体系不同，报表查询必须在进入各分支前完成转换，否则会出现「查得到产融、查不到讯易链」的错配。角色本身的多值/单值差异见 [[concepts/company-type]]，产融关联表字段定义见 [[tables/cust_project_rel]]。

## 版本演进

目前只对 CORE/FINANCE 两个角色建立了跨源映射，其余角色在报表查询中退化为不筛选（置 'a'），属映射覆盖不全的过渡状态。

```ground:caliber
name: "companyType 跨源映射口径"
predicate: "讯易链：CORE→ce（XycCompanyType.CE），FINANCE→cpt（XycCompanyType.CPT）；产融保持原值"
scope: "项目企业报表 companyType 查询参数转换"
evidence: "code_path:ProjectReportController.java:processCompanyTypeBySource"
```
---END FILE---

---FILE: concepts/data-source.md ---
---
type: concept
title: 数据来源 / source
page_key: concept.data-source
domain: 项目报表/统计/上报
status: draft
aliases:
  - source
  - dataSource
  - transaction_platform
  - data_source
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportApplication.java
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
maps_to: "项目台账侧 source ∈ {产融, 讯易链}；项目立项统计侧 data_source ∈ {MANUAL, WECHAT}；两者语义不同，同名不同域"
also_confused_with:
  - "productCode（ACFLOW/RVSFACTOR_PC 等存放在 cust_project_rel.remark）"
adjudication: boundary
boundary: "项目台账 source 决定「读本地表 vs 调洞察平台」；项目立项统计 data_source 决定「是否企微同步生成的立项」。二者不可互换。"
---

# 数据来源 / source

「数据来源」在本主题下是一个被两个域共用的词：项目台账域用它决定取数通道，立项统计域用它决定单据的产生方式。任何报表/统计/上报的字段说明中见到 source、dataSource、data_source、transaction_platform，必须先判断落在哪个域。

## 需求背景

- 项目台账域：以 transaction_platform 是否等于「产融平台」判定 source，产融走本地关联表，讯易链走洞察平台，判定与分流见 [[calibers/project-ledger-source]]。
- 立项统计域：以 data_source 区分 MANUAL（模拟立项，spNo 以 MN 开头）与 WECHAT（真实立项），见 [[processes/project-data-source]]、[[tables/wechat_project_approval_apply]]、[[rules/manual-project-spno]]。

两者共用「数据来源」这一中文表述，但一个描述「数据从哪个系统来」，另一个描述「单据由谁生成」，因此必须按表/页面域区分，不能合并为一个枚举。

## 版本演进

立项统计域的 data_source 是在模拟立项能力引入后出现的（MANUAL 值），项目台账域的 source 则是更早的渠道分流判定；两域长期并行，未做术语拆名。

配套歧义：productCode（ACFLOW/RVSFACTOR_PC/BEECREDIT 等）实际被写入 [[tables/cust_project_rel]] 的 remark 列，容易与「来源/产品」两词混淆。
---END FILE---

---FILE: concepts/company-type.md ---
---
type: concept
title: 客户角色 / 企业角色（companyType）
page_key: concept.company-type
domain: 项目报表/统计/上报
status: draft
aliases:
  - companyType
  - company_type
  - companyTypeZh
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
  - db:cust_project_rel
  - db:cust_project_code_record
contract_version: "0.1"
maps_to: "cust_project_rel.company_type（单值）：CORE/FINANCE/SUPPLIER/DEALER/PROJECT_COMPANY/CORE_MANAGER/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY；跨源映射：产融 CORE↔讯易链 ce，产融 FINANCE↔讯易链 cpt"
also_confused_with:
  - "cust_project_code_record.company_type（JSON 数组，多角色集合）"
adjudication: boundary
boundary: "关联表为单角色（弹窗「客户角色」单选项）；录入码记录表为受限多角色集合；转换只允许 CORE/FINANCE 两值参与跨源映射，其它角色在报表查询中退化为不筛选（置 'a'）。"
---

# 客户角色 / 企业角色（companyType）

companyType / company_type 在本主题中出现三种形态，混用会导致取数错误：关联表的单值角色、录入码记录表的多值角色集合、以及讯易链侧的短码（ce/cpt）。

## 需求背景

项目台账的关联企业弹窗中，客户角色为单选项，因此 [[tables/cust_project_rel]] 以单值存放；企业项目码录入时企业可能同时具备多个角色，因此 [[tables/cust_project_code_record]] 以 JSON 数组保存提交时的角色集合。报表查询侧需要按来源做角色编码转换，只对 CORE/FINANCE 建立了映射，其余角色退化为不筛选，转换口径见 [[calibers/company-type-cross-source-mapping]]。

关联表还存在拼写变体 PLATFORM_OPREATOR_COMPANY（疑似历史脏数据），比较与展示时需容错。

## 版本演进

角色枚举随业务扩展（新增 PROJECT_COMPANY、CORE_MANAGER、CORPORATION_COMPANY、PLATFORM_OPERATOR_COMPANY 等），但跨源映射仍只覆盖 CORE/FINANCE 两值；录入码记录表的多值形态与关联表的单值形态长期并存，未见统一模型。
---END FILE---

---FILE: concepts/project-phase.md ---
---
type: concept
title: 项目阶段（projectPhase）
page_key: concept.project-phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - projectPhase
  - project_phase
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
maps_to: "IMPLEMENTATION=实施阶段 / OPERATION=持续运营 / HANG=挂起 /（读时归一）TERMINATION→HANG"
also_confused_with:
  - "项目状态 project_status（项目台账：1=已生效，非 1=未生效）"
adjudication: boundary
boundary: "project_status 属项目台账维度（tenant_project），project_phase 属立项统计维度（wechat_project_approval_apply）。"
---

# 项目阶段（projectPhase）

「项目阶段」与「项目状态」都容易被简称为「项目状态」，但分属两个域：前者描述立项单据处于实施/运营/挂起，后者描述项目台账上项目是否已生效。

## 需求背景

- project_phase 作用于立项统计域（[[tables/wechat_project_approval_apply]]），是运营口径与自动流转的核心字段，流转规则见 [[processes/project-phase]]、[[rules/first-settlement-to-operation-phase]]。
- project_status 作用于项目台账域（tenant_project），取值为 1=已生效、非 1=未生效，用于台账列表与导出，不能与阶段值混用。

在报表/上报口径撰写时，出现「已生效/未生效」应指向 project_status；出现「实施/运营/挂起」应指向 project_phase。

## 版本演进

project_phase 的历史值 TERMINATION 已在读取时归一为 HANG，值域收敛为三态；项目台账的 project_status 保持二元语义，两者未做合并。
---END FILE---

---FILE: concepts/captcha.md ---
---
type: concept
title: 是否需要验证码（需求文档串入）
page_key: concept.captcha
domain: 项目报表/统计/上报
status: draft
aliases:
  - captcha
  - 行为验证码
oid: 1
scope:
  databases:
    - unknown
sources:
  - reqdoc:SSO验证码登录改造技术设计
contract_version: "0.1"
maps_to: "SSO 登录域字段，与项目报表/统计/上报主题无关"
also_confused_with: []
adjudication: boundary
boundary: "需求文档 reqdoc:SSO验证码登录改造技术设计 对本主题无结构性贡献，仅在 cust_project_rel / tenant_project 表字段附录处与本主题交叉，不作为字段值来源。"
---

# 是否需要验证码（需求文档串入）

「是否需要验证码 / captcha / 行为验证码」属于 SSO 登录域的字段，语义上与本主题（项目报表/统计/上报）无交集。

## 需求背景

该词出现在需求文档 reqdoc:SSO验证码登录改造技术设计中，仅在 cust_project_rel / tenant_project 的表字段附录处与本主题发生文本交叉。本主题的任何字段说明、口径、规则都不得以该文档作为字段值来源；如遇引用，应按登录域归档。

## 版本演进

无本主题内的版本演进；该术语的存在仅为避免跨主题混引。相关表见 [[tables/cust_project_rel]]。
---END FILE---

---FILE: rules/first-settlement-to-operation-phase.md ---
---
type: rule
title: 首笔落地时间变更联动项目阶段为持续运营
page_key: rule.first-settlement-to-operation-phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - 首笔落地联动
  - applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
---

# 首笔落地时间变更联动项目阶段为持续运营

当立项已审批通过、且首笔落地时间被更新为新的非空值时，系统自动把项目阶段置为 OPERATION（持续运营）。这是立项统计侧唯一的自动阶段推进规则。

## 需求背景

业务上「首笔落地」意味着项目从实施进入持续运营，因此不需要人工改阶段。规则设定了三重前置：审批通过（见 [[calibers/project-ledger-approved]]）、新值非空、当前阶段非 OPERATION（避免重复写）。首笔落地时间被清空为 null 时**不**触发，这与该列「非空覆盖 / null 清空」的编辑例外语义相配套（见 [[tables/wechat_project_approval_apply]]）。规则在编辑保存、导入、开发用导入三条写入路径均生效，状态定义见 [[processes/project-phase]]。

## 版本演进

规则在正式链路与开发用导入链路各有一份实现（ProjectStatisticsApplication 与 ProjectStatisticsDevImportApplication），属双实现；「非 OPERATION 才覆盖」的保护条件表明该规则曾考虑过阶段被回退/挂起后的重入场景。

```ground:rule
name: "首笔落地时间变更联动项目阶段为持续运营"
content: "当 act_procinst_status='2' 且首笔落地时间发生变化且新值非空且当前项目阶段非 OPERATION 时，自动将 project_phase 置为 OPERATION。首笔落地时间清空（null）场景不触发。"
impact: "编辑保存 / 导入 / 开发用导入 三条写入路径均生效"
field_targets:
  - "wechat_project_approval_apply.project_phase"
  - "wechat_project_approval_apply.first_settlement_time"
evidence: "code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved + code_path:ProjectStatisticsDevImportApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
```
---END FILE---

---FILE: rules/edit-whitelist-and-field-history.md ---
---
type: rule
title: 编辑白名单与字段历史保护
page_key: rule.edit-whitelist-and-field-history
domain: 项目报表/统计/上报
status: draft
aliases:
  - 白名单编辑
  - 同步保护字段
  - writeChangedColumns
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 编辑白名单与字段历史保护

立项统计的编辑保存并非整行覆写：只有白名单列参与 diff 比较与写库，并同步落一条字段历史；被人工写过的「同步保护字段」在企微同步写库前会被跳过。

## 需求背景

立项单据部分字段来自企微同步，部分是统计侧人工维护。若同步 Job 直接覆写整行，会冲掉人工修改；若编辑保存直接整行更新，又会制造大量无意义变化。因此采用双向约束：编辑侧限定白名单 + 差异写库，同步侧过滤保护字段。字段历史来源枚举见 [[tables/wechat_project_approval_apply_field_history]]，涉及的表为 [[tables/wechat_project_approval_apply]]。

## 版本演进

历史来源目前覆盖 EDIT/BATCH/MANUAL_CREATE/IMPORT 四类，说明批量变更、模拟立项与导入链路已陆续纳入同一审计机制；保护字段集以「已被人工写入」为动态判定，属后期补强的防覆盖设计。

```ground:rule
name: "编辑白名单与字段历史保护"
content: "编辑保存只对 EDITABLE_JAVA_FIELDS 白名单中的列做 diff 写库，并写入 wechat_project_approval_field_history（source=EDIT/BATCH/MANUAL_CREATE/IMPORT）；已被人工写入的「同步保护字段集」对应列，企微同步 Job 在写库前需过滤跳过。"
impact: "保护人工修改不被企微同步覆盖；未命中差异的列不落库不写历史"
field_targets:
  - "wechat_project_approval_apply.*（白名单列）"
  - "wechat_project_approval_field_history.*"
evidence: "code_path:ProjectStatisticsApplication.java:update + writeChangedColumns"
```
---END FILE---

---FILE: rules/manager-wechat-identity-validation.md ---
---
type: rule
title: 方案经理/业务经理企微身份校验
page_key: rule.manager-wechat-identity-validation
domain: 项目报表/统计/上报
status: draft
aliases:
  - 部门归属校验
  - validateImportManagerDeptMembership
  - changeOnePlanMgr
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 方案经理/业务经理企微身份校验

方案经理与业务经理的姓名不能随意填写：必须能在企微通讯录中找到，且分别归属指定部门（方案经理归属「Saas方案部」，业务经理归属「客户营销」部，部门名由 Nacos 配置）。校验通过后由企微 userId 反查姓名并落库。

## 需求背景

立项统计需要按人检索与提醒，因此经理字段必须与企微身份对齐。落库时同时维护 solution_manager（姓名 CSV）与 solution_manager_wxid（userId JSON 数组冗余列），后者用于按 wxid 精确过滤（见 [[tables/wechat_project_approval_apply]]）。规则作用于编辑保存、批量变更方案经理、导入、模拟立项四条路径；经理变更还会触发前方案经理合并（见 [[rules/old-solution-manager-merge]]）。

## 版本演进

部门名通过 Nacos 配置（wechat.org.dept.name.saas.solution、wechat.org.dept.name.customer.marketing）而非硬编码，说明组织调整已可通过配置适配；userId 冗余列的引入是为支持按人精确过滤的后期增强。

```ground:rule
name: "方案经理/业务经理企微身份校验"
content: "方案经理姓名须在企微通讯录存在且属于「Saas方案部」（Nacos wechat.org.dept.name.saas.solution）；业务经理姓名须属于「客户营销」部（wechat.org.dept.name.customer.marketing）。落库时由企微 userId 反查姓名 CSV，并同步维护 solution_manager_wxid 冗余列。"
impact: "编辑保存、批量变更方案经理、导入、模拟立项"
field_targets:
  - "wechat_project_approval_apply.solution_manager"
  - "wechat_project_approval_apply.solution_manager_wxid"
  - "wechat_project_approval_apply.bussiness_manager"
  - "wechat_project_approval_apply.business_center"
evidence: "code_path:ProjectStatisticsApplication.java:validateImportManagerDeptMembership + ProjectStatisticsApplication.java:changeOnePlanMgr"
```
---END FILE---

---FILE: rules/old-solution-manager-merge.md ---
---
type: rule
title: 前方案经理联动合并
page_key: rule.old-solution-manager-merge
domain: 项目报表/统计/上报
status: draft
aliases:
  - old_solution_manager 合并
  - mergeOldSolutionManager
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:SysWxOrgCacheService
contract_version: "0.1"
---

# 前方案经理联动合并

方案经理发生变更时，系统把「既不在原前方案经理列表中、也不在当前方案经理中」的姓名前置合并进 old_solution_manager，从而保留历史责任人痕迹。

## 需求背景

项目交接过程中需要知道此前的方案经理是谁，因此 old_solution_manager 以姓名 CSV 累积保存（字段定义见 [[tables/wechat_project_approval_apply]]）。合并策略保证不重复、不并入现任；导入路径为例外：当前方案经理列有值且与库中不一致时，直接以导入值为准。变更本身受企微身份校验约束（见 [[rules/manager-wechat-identity-validation]]）。

## 版本演进

导入路径的「以导入值为准」例外说明该列在批量数据迁移场景下需要人工可控；合并逻辑被抽到 SysWxOrgCacheService.mergeOldSolutionManager，属从应用层下沉到缓存/组织服务层的演进。

```ground:rule
name: "前方案经理联动合并"
content: "方案经理变更时，将「既不在 existingOld、也不在 curr」的姓名前置合并入 old_solution_manager；导入路径下，若前方案经理列有值且与库中不一致，则直接以导入值为准。"
impact: "编辑保存、批量变更、导入、开发用导入"
field_targets:
  - "wechat_project_approval_apply.old_solution_manager"
evidence: "code_path:ProjectStatisticsApplication.java:update（oldSmInput 三段处理段） + SysWxOrgCacheService.mergeOldSolutionManager"
```
---END FILE---

---FILE: rules/manual-project-spno.md ---
---
type: rule
title: 模拟立项编号规则
page_key: rule.manual-project-spno
domain: 项目报表/统计/上报
status: draft
aliases:
  - MN 编号规则
  - generateManualSpNo
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsDevImportApplication.java
contract_version: "0.1"
---

# 模拟立项编号规则

模拟立项的 spNo 由后端按固定表达式生成，形如 MN-yyyyMMdd-XXXX，并强制 data_source = MANUAL；入参若已以 MN 开头则直接视为模拟立项编号。

## 需求背景

模拟立项用于演示与联调（见 [[processes/project-data-source]]），必须以编号前缀与真实立项区分，列表与导出按 spNo 前缀 MN 识别。编号表达式 `MN-%T{yyyyMMdd}#S4#` 中的 S4 表示四位顺序号，保证同日多单不重号。字段定义见 [[tables/wechat_project_approval_apply]]，落库路径受编辑白名单与历史保护约束（见 [[rules/edit-whitelist-and-field-history]]）。

## 版本演进

开发用导入（isManualSpNo）与手工新增共用同一前缀判定，说明模拟立项能力已从单条手工新增扩展为可批量注入；data_source 的写入被规则强制，不依赖调用方传值。

```ground:rule
name: "模拟立项编号规则"
content: "spNo 由后端生成，编号表达式 MN-%T{yyyyMMdd}#S4#（MN-yyyyMMdd-XXXX）；入参若已以 MN 开头则视为模拟立项编号；data_source 强制 MANUAL；列表与导出按 spNo 前缀 MN 识别。"
impact: "模拟立项手工新增与开发用导入"
field_targets:
  - "wechat_project_approval_apply.sp_no"
  - "wechat_project_approval_apply.data_source"
evidence: "code_path:ProjectStatisticsApplication.java:generateManualSpNo + ProjectStatisticsDevImportApplication.java:isManualSpNo"
```
---END FILE---

---FILE: rules/import-update-only.md ---
---
type: rule
title: 导入仅支持更新（正式链路）
page_key: rule.import-update-only
domain: 项目报表/统计/上报
status: draft
aliases:
  - 导入更新规则
  - 正式导入链路
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 导入仅支持更新（正式链路）

正式导入链路不对不存在的单据做新增，只按 spNo 匹配库中已存在的记录做更新。该限制把「新建」收口在企微同步与模拟立项两条路径上，避免导入制造脏数据。

## 需求背景

立项单据的主键语义来自企微审批（spNo），导入主要用于批量维护统计侧字段（方案经理、前方案经理、首笔落地时间等）。若允许导入新增，将出现无审批来源的立项，破坏审批通过口径（见 [[calibers/project-ledger-approved]]）。导入涉及的字段写入同样受白名单与字段历史约束（见 [[rules/edit-whitelist-and-field-history]]），批量变更来源记为 IMPORT（见 [[tables/wechat_project_approval_apply_field_history]]）。

## 版本演进

正式链路限定「仅更新」，而开发用导入链路另有建单能力（见 [[processes/project-data-source]]），二者按环境分离；该规则的完整约束内容在语义分析中被截断，影响面待补证。

```ground:rule
name: "导入仅支持更新（正式链路）"
content: "项目立项统计正式导入以 spNo 匹配库中已存在记"
impact: "待补证（语义分析中该规则内容被截断）"
field_targets:
  - "wechat_project_approval_apply.sp_no"
evidence: "code_path:ProjectStatisticsApplication.java（导入链路，语义分析未给出方法名）"
```
---END FILE---

---REVIEW: rule | 导入仅支持更新（正式链路）---
语义分析中该规则的 content 在「以 spNo 匹配库中已存在记」处被截断，impact 与 evidence 的方法名均未给出。上页 ground:rule 块只能逐字保留已给出的片段，其余字段以「待补证」标注，不得据此推断新增/更新判定细节或参与其它口径。
建议补证：导入链路的匹配条件、未匹配行的处理方式（跳过/报错/统计）、与开发用导入 `buildManualEntityForInsert` 的边界。
---END REVIEW---

---REVIEW: table | cust_project_rel---
三处需要人工确认的字段语义：
1. `remark` 被写入 productCode（ACFLOW/RVSFACTOR_PC/BEECREDIT），语义已被复用；是否新建独立列或建立映射表，需产品确认。
2. `company_type` 存在拼写变体 `PLATFORM_OPREATOR_COMPANY`，是否为可清洗的历史脏数据、清洗窗口与影响面未知。
3. `status` 出现带首尾空格的 ` 1 `，与 `'1'`、`1` 的读取兼容策略未在证据中给出。
---END REVIEW---

---REVIEW: tables | 全局（物理库名缺失）---
语义分析未提供任何表的物理库名，因此本次所有 table 页的 `scope.databases` 统一填 `unknown`，未做推断。待补证：cust_project_rel / cust_project_pushcust / cust_project_code_record / wechat_project_approval_apply / wechat_project_approval_apply_field_history 各自所属的物理库（生产/预发是否分库同表）。
---END REVIEW---