---FILE: tables/wechat_project_approval_apply.md ---
---
type: table
title: 企微审批申请表
page_key: wechat_project_approval_apply
domain: 微企链立项与项目审批
status: draft
aliases:
  - 微企链立项表
  - 企微审批申请
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

微企链侧（企业微信）的立项审批申请主表，一行代表一条立项审批申请。表内同时承载企微审批实例状态、数据来源、项目阶段、方案经理、运营对接人等业务属性，是模拟立项、企微同步、项目统计与阶段自动流转的共同数据底座。该表与 [[tenant_project_approval]] 通过 `sp_no` 关联，但二者在审批主体与状态口径上完全不同，参见 [[concepts/wechat_project_initiation]] 与 [[concepts/approval_status]]。

```ground:table
table: wechat_project_approval_apply
fields:
  - name: act_procinst_status
    type: unknown
    desc: '企微审批实例状态：1=审批中，2=已通过，3/4 未在代码中显式声明（DB 分布存在）'
    dict: ''
  - name: data_source
    type: unknown
    desc: '数据来源：MANUAL=模拟立项，WECHAT=真实立项（企微同步）'
    dict: ''
  - name: prd
    type: unknown
    desc: '是否投产：Y=已投产，N=未投产'
    dict: ''
  - name: ka_white_label
    type: unknown
    desc: 'KA是否贴牌：Y=是，N=否'
    dict: ''
  - name: project_phase
    type: unknown
    desc: '项目阶段：INITIATION=立项阶段，IMPLEMENTATION=实施阶段，OPERATION=持续运营，HANG=挂起；历史值 TERMINATION 归一为 HANG'
    dict: ''
  - name: sp_type
    type: unknown
    desc: '类型，项目统计默认过滤金融科技业务'
    dict: ''
  - name: system_delivery
    type: unknown
    desc: '系统交付方式：SaaS、Saas+本地化'
    dict: ''
  - name: project_type
    type: unknown
    desc: '项目类型：MAIN=主项目，SUB=子项目'
    dict: ''
  - name: op_contact
    type: unknown
    desc: '运营对接人，存储 operation_id，展示时反查姓名'
    dict: ''
  - name: solution_manager
    type: unknown
    desc: '方案经理姓名，多个以逗号分隔'
    dict: ''
  - name: solution_manager_wxid
    type: unknown
    desc: '方案经理企微 userId 列表的 JSON 数组字符串，如 ["id1","id2"]'
    dict: ''
  - name: old_solution_manager
    type: unknown
    desc: '前方案经理，姓名 CSV，由变更入口联动维护'
    dict: ''
  - name: first_settlement_time
    type: unknown
    desc: '首笔落地时间（DB 注释为首笔放款时间），审批通过后更新会联动项目阶段为持续运营'
    dict: ''
```

## 需求背景

该表服务于三类需求：其一，企微审批数据入库与导出，导出受 [[calibers/wechat_approval_export]] 硬过滤约束，导入遵循 [[rules/wechat_approval_import_update_only]]；其二，模拟立项与项目统计，统计范围由 [[calibers/project_statistics_default]] 界定，模拟立项遵循 [[rules/manual_create_project_apply]]；其三，方案经理维护与项目阶段推进，分别见 [[rules/batch_change_solution_manager_department_check]] 与 [[rules/project_phase_auto_transition]]。表内除上列字段外，还有参与关联与校验的 `sp_no`（审批编号）、`risk_control_contact`（风控对接人）、`comment`（备注）等列，本次语义分析未产出其字段级释义。

## 版本演进

项目阶段历史上存在 `TERMINATION` 取值，现已在读取路径归一为 `HANG`，取值域见 [[processes/project_phase]]；企微审批实例状态在工作流中另有 DB 分布值 3、4 未被代码常量覆盖，见 [[processes/wechat_apply_approval_status]]。

---END FILE---

---FILE: tables/tenant_project_approval.md ---
---
type: table
title: 项目上线审批表
page_key: tenant_project_approval
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批表
  - 项目审批主表
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval
  - code_path:ProjectApprovalApplication.java
  - code_path:ProjectBusinessConfigApplication.java
contract_version: "0.1"
---

产融平台侧的项目上线审批主表，一次上线审批对应一行，承载工作流状态、是否最新版本、关联项目、审批编号等。与企微侧的 [[wechat_project_approval_apply]] 分属两套审批语义，术语边界见 [[concepts/wechat_project_initiation]] 与 [[concepts/approval_status]]。

```ground:table
table: tenant_project_approval
fields:
  - name: wf_status
    type: unknown
    desc: '项目上线审批工作流状态：PENDING=待发起，RUNNING=审批中，FINISHED=审批通过，TERMINATED=审批拒绝；DB 另有 REVOKED=已撤销（代码枚举未声明）'
    dict: ''
```

## 需求背景

该表是上线审批全链路的主记录：发起与暂存见 [[rules/online_approval_submit]]，重新发起时的复制规则见 [[rules/reinitiate_online_approval_copy]]，审批通过后驱动项目生效见 [[rules/effective_project_on_approval_finished]]，推送 AMS 见 [[rules/push_to_ams]]。审批中流程的定位口径见 [[calibers/running_latest_approval]]，下拉可选范围见 [[calibers/related_approval_no_options]]。表内另有 `is_latest`（是否最新版本）、`is_online_approval`、`enable`、`sp_no`（审批编号）、`solution_manager_id`（方案经理标识，与企微侧姓名列不同，见 [[concepts/solution_manager]]）、`project_type`、`is_low_risk` 以及自关联列 `ref_tenant_project_approval_tenant_project_approval` 等，本次语义分析未产出字段级释义。

## 版本演进

工作流状态取值由代码枚举给出 4 个值，DB 分布中另有 `REVOKED`（已撤销）未被枚举声明，状态全集与流转见 [[processes/tenant_project_approval_wf_status]]。

---END FILE---

---FILE: tables/tenant_project_approval_flow.md ---
---
type: table
title: 项目上线审批流程表
page_key: tenant_project_approval_flow
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批流程表
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval_flow
  - code_path:ProjectOnlineProcessOperateListener.java
  - code_path:ProjectBusinessConfigApplication.java
contract_version: "0.1"
---

上线审批的流程实例表，承接工作流运行期的流程级状态，是 [[tenant_project_approval]] 主记录与 [[tenant_project_approval_flow_node]] 节点记录之间的中间层。

```ground:table
table: tenant_project_approval_flow
fields:
  - name: node_status
    type: unknown
    desc: '审批流程节点状态：PENDING=待审批，APPROVING=审批中，APPROVED=已通过，REJECTED=已拒绝'
    dict: ''
```

## 需求背景

流程级状态随审批人操作（同意、退回、驳回、转审）推进，状态机见 [[processes/tenant_project_approval_flow_node_status]]。业务系统推送项目配置时，需要定位到「正在审批的节点」才落库，口径见 [[calibers/approving_flow_node]]，规则见 [[rules/business_config_push_node_check]]。表内另有 `enable` 等启停列参与口径过滤。

## 版本演进

当前语义分析未提供该表状态取值的历史变更记录。

---END FILE---

---FILE: tables/tenant_project_approval_flow_node.md ---
---
type: table
title: 项目上线审批流程节点表
page_key: tenant_project_approval_flow_node
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批节点表
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval_flow_node
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

上线审批流程的节点级记录表，一行代表某个流程中一个审批节点的操作与状态，是审批意见、节点类型与后补协议标记的落点。

```ground:table
table: tenant_project_approval_flow_node
fields:
  - name: operate_type
    type: unknown
    desc: '节点操作类型：PASS=同意，BACK=退回，REJECT=驳回，DELEGATE=转审'
    dict: ''
```

## 需求背景

节点操作类型决定流程状态如何推进：同意进入已通过、退回回到待审批、驳回进入已拒绝，见 [[processes/tenant_project_approval_flow_node_status]]。节点属性还参与后补合作协议的触发判断——业务经理节点同意且该节点记录 `is_back_agreement=Y` 时启动后续流程，见 [[rules/back_agreement_trigger]]，其中 `node_code` 用于识别节点身份。业务系统推送项目配置同样以节点维度做准入判断，见 [[calibers/approving_flow_node]]。

## 版本演进

当前语义分析未提供该表节点操作类型的历史变更记录。

---END FILE---

---FILE: tables/tenant_project_approval_flow_file.md ---
---
type: table
title: 项目上线审批流程影像文件表
page_key: tenant_project_approval_flow_file
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批影像文件表
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval_flow_file
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

上线审批流程中的影像/附件记录表，按影像分类挂载在审批流程上；重新发起审批时影像文件会随主记录一并复制，见 [[rules/reinitiate_online_approval_copy]]。

```ground:table
table: tenant_project_approval_flow_file
fields:
  - name: catg_id
    type: unknown
    desc: '影像分类 ID，代码枚举含 FBP_PROJECT_CONFIG 等，DB 另有 FBP_OA_ATTACHMENT、FBP_OA_COMMENT_FILE 未在枚举中'
    dict: ''
```

## 需求背景

影像分类用于区分商务批复报价文件、项目配置附件与 OA 附件等不同用途的文件；提交上线审批时要求必须上传商务批复报价文件，见 [[rules/online_approval_submit]]。

## 版本演进

影像分类取值呈现「代码枚举 < DB 实际分布」的缺口：`FBP_OA_ATTACHMENT`、`FBP_OA_COMMENT_FILE` 出现在数据中但未在代码枚举声明，分类枚举的完整基线待补齐。

---END FILE---

---FILE: processes/wechat_apply_approval_status.md ---
---
type: process
title: 企微立项审批状态
page_key: wechat_apply_approval_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - act_procinst_status
  - 企微审批实例状态
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

[[wechat_project_approval_apply]] 上的企微审批实例状态字段，描述单条立项申请在企微审批实例中的推进结果。它是「业务是否可以往下走」的闸门：导出只取已通过记录，统计导入跳过审批中记录。注意它与平台侧工作流状态是两套口径，不要混用，参见 [[concepts/approval_status]]。

```ground:process
name: 企微立项审批状态
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: '1'
    label: 审批中
    source: code_const
  - value: '2'
    label: 已通过
    source: code_const
  - value: '3'
    label: 未知
    source: db_dist
  - value: '4'
    label: 未知
    source: db_dist
transitions: []
```

## 需求背景

状态 `2`（已通过）是企微审批导出与项目阶段推进的前置条件：导出固定取已通过且来源为企微的记录，见 [[calibers/wechat_approval_export]] 与 [[rules/wechat_approval_export_hard_filter]]；统计导入时审批中的记录会被跳过，见 [[calibers/approving_apply_records]]；首笔落地时间在审批通过后更新会联动项目阶段，见 [[rules/project_phase_auto_transition]]。

## 版本演进

代码常量仅显式声明 1、2 两个取值，而 DB 分布中存在 3、4，语义未知，未在代码中出现对应分支。

---END FILE---

---FILE: processes/tenant_project_approval_wf_status.md ---
---
type: process
title: 项目上线审批工作流状态
page_key: tenant_project_approval_wf_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - wf_status
  - 上线审批工作流状态
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

[[tenant_project_approval]] 上的工作流状态，描述一次上线审批从草稿待发起，到审批中，再到终态（通过或拒绝）的推进。它是重新发起、项目生效、AMS 推送等一系列动作的触发条件。

```ground:process
name: 项目上线审批工作流状态
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 审批通过
    source: code_enum
  - value: TERMINATED
    label: 审批拒绝
    source: code_enum
  - value: REVOKED
    label: 已撤销
    source: db_dist
transitions:
  - from: PENDING
    event: 启动工作流
    to: RUNNING
    evidence: code_path:ProjectApprovalApplication.java:startWorkflowAndUpdateStatus
  - from: RUNNING
    event: 审批通过
    to: FINISHED
    evidence: code_path:ProjectApprovalApplication.java:handleFlowAndNodeStatus
  - from: RUNNING
    event: 审批拒绝/驳回
    to: TERMINATED
    evidence: code_path:ProjectApprovalApplication.java:handleFlowAndNodeStatus
```

## 需求背景

暂存不启动工作流、提交才生成审批编号并启动，见 [[rules/online_approval_submit]]；重新发起时新审批以 `PENDING` 起步并置 `is_latest=Y`，见 [[rules/reinitiate_online_approval_copy]]；终态 `FINISHED` 触发项目生效与下游推送，见 [[rules/effective_project_on_approval_finished]] 与 [[rules/push_to_ams]]；仅 `RUNNING` 且为最新版本的审批会被业务系统定位到，见 [[calibers/running_latest_approval]]。

## 版本演进

代码枚举声明了 PENDING/RUNNING/FINISHED/TERMINATED 四个值，DB 分布中另有 `REVOKED`（已撤销）未被枚举覆盖，该状态的产生入口与后续处理在本次分析中未见证据。

---END FILE---

---FILE: processes/tenant_project_approval_flow_node_status.md ---
---
type: process
title: 审批流程节点状态
page_key: tenant_project_approval_flow_node_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - node_status
  - 节点状态
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval_flow
  - code_path:ProjectOnlineProcessOperateListener.java
contract_version: "0.1"
---

[[tenant_project_approval_flow]] 上的节点状态，随审批人在节点上的操作（同意、退回、驳回）推进，并由监听器统一解析落库。它与 [[tenant_project_approval_flow_node]] 的节点操作类型配合使用：操作类型是「做了什么」，节点状态是「节点现在处于什么状态」。

```ground:process
name: 审批流程节点状态
field: tenant_project_approval_flow.node_status
states:
  - value: PENDING
    label: 待审批
    source: code_enum
  - value: APPROVING
    label: 审批中
    source: code_enum
  - value: APPROVED
    label: 已通过
    source: code_enum
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: PENDING
    event: 节点激活
    to: APPROVING
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
  - from: APPROVING
    event: 同意
    to: APPROVED
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
  - from: APPROVING
    event: 退回
    to: PENDING
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
  - from: APPROVING
    event: 驳回
    to: REJECTED
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
```

## 需求背景

节点是否处于 `APPROVING` 是业务系统推送项目配置能否落库的判定条件，见 [[calibers/approving_flow_node]] 与 [[rules/business_config_push_node_check]]；节点上的操作类型见 [[tenant_project_approval_flow_node]] 的 `operate_type`。

## 版本演进

当前语义分析未提供该状态取值的历史变更记录。

---END FILE---

---FILE: processes/project_phase.md ---
---
type: process
title: 项目阶段
page_key: project_phase
domain: 微企链立项与项目审批
status: draft
aliases:
  - project_phase
  - 项目阶段流转
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

[[wechat_project_approval_apply]] 上的项目阶段字段，描述立项项目从立项、实施到持续运营的生命周期位置，并包含一个挂起态。阶段推进主要由业务事件驱动：审批通过后首笔落地时间被更新即自动进入持续运营。

```ground:process
name: 项目阶段
field: wechat_project_approval_apply.project_phase
states:
  - value: INITIATION
    label: 立项阶段
    source: code_const
  - value: IMPLEMENTATION
    label: 实施阶段
    source: code_const
  - value: OPERATION
    label: 持续运营
    source: code_const
  - value: HANG
    label: 挂起
    source: code_const
transitions:
  - from: 任何
    event: 审批通过后首笔落地时间更新
    to: OPERATION
    evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - from: TERMINATION
    event: 遗留值转换
    to: HANG
    evidence: code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode
```

## 需求背景

阶段自动流转的完整条件（审批已通过、首笔落地时间被更新、当前阶段不是持续运营）见 [[rules/project_phase_auto_transition]]，其前置状态判定依赖 [[wechat_apply_approval_status]]；首笔落地时间字段语义见 [[wechat_project_approval_apply]]。

## 版本演进

历史值 `TERMINATION` 在读取路径被归一为 `HANG`，属于遗留数据兼容；正常写入路径已不再产出该值。

---END FILE---

---FILE: calibers/wechat_approval_export.md ---
---
type: caliber
title: 企微审批导出硬过滤
page_key: wechat_approval_export
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微审批导出范围
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
contract_version: "0.1"
---

导出企微审批申请信息的固定数据范围：只导出已通过且来源为企微同步的记录。该过滤由后端硬编码，前端查询条件无法改写，用于把「审批中的申请」和「手工模拟立项」排除在导出结果之外。

```ground:caliber
name: 企微审批导出硬过滤
predicate: wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.data_source = 'WECHAT'
scope: 导出企微审批申请信息
evidence: code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
```

## 需求背景

对应的固化规则见 [[rules/wechat_approval_export_hard_filter]]。口径依赖的两个字段取值见 [[processes/wechat_apply_approval_status]] 与 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: calibers/approving_apply_records.md ---
---
type: caliber
title: 审批中记录
page_key: approving_apply_records
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微审批中记录
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:validateAndApply
contract_version: "0.1"
---

项目立项统计导入时用于识别并跳过「企微审批中」记录的口径：状态为审批中的申请不进入统计导入。

```ground:caliber
name: 审批中记录
predicate: wechat_project_approval_apply.act_procinst_status = '1'
scope: 项目立项统计导入跳过审批中记录
evidence: code_path:ProjectStatisticsApplication.java:validateAndApply
```

## 需求背景

该口径与导出口径互补：导出取已通过（2），统计导入跳过审批中（1）。状态取值见 [[processes/wechat_apply_approval_status]]，所在表见 [[wechat_project_approval_apply]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: calibers/project_statistics_default.md ---
---
type: caliber
title: 项目统计默认范围
page_key: project_statistics_default
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目统计默认过滤
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:buildPageWrapper
contract_version: "0.1"
---

项目立项统计列表与导出默认生效的数据范围：只统计金融科技业务类型、且系统交付方式为 SaaS 或 Saas+本地化 的项目。

```ground:caliber
name: 项目统计默认范围
predicate: wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.system_delivery IN ('SaaS','Saas+本地化')
scope: 项目立项统计列表/导出
evidence: code_path:ProjectStatisticsApplication.java:buildPageWrapper
```

## 需求背景

默认范围作用于 [[wechat_project_approval_apply]] 的统计查询构建环节，字段语义见该表页的 `sp_type` 与 `system_delivery`。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: calibers/related_approval_no_options.md ---
---
type: caliber
title: 关联审批编号下拉
page_key: related_approval_no_options
domain: 微企链立项与项目审批
status: draft
aliases:
  - 关联审批编号可选范围
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:listRelatedApprovalNo
contract_version: "0.1"
---

「关联审批编号」下拉的可选范围：仅列出处于审批中或审批通过、且为线上审批、且记录启用的上线审批。

```ground:caliber
name: 关联审批编号下拉
predicate: tenant_project_approval.wf_status IN ('RUNNING','FINISHED') AND tenant_project_approval.is_online_approval = 'Y' AND tenant_project_approval.enable = 'Y'
scope: 关联审批编号下拉
evidence: code_path:ProjectApprovalApplication.java:listRelatedApprovalNo
```

## 需求背景

该口径限定可被关联的审批编号只能是「进行中」或「已完成」的线上审批，见 [[tenant_project_approval]] 与 [[processes/tenant_project_approval_wf_status]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: calibers/selectable_projects_for_online_approval.md ---
---
type: caliber
title: 可发起上线审批的项目
page_key: selectable_projects_for_online_approval
domain: 微企链立项与项目审批
status: draft
aliases:
  - 历史项目发起上线审批可选范围
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:listApprovalSelectableProjects
contract_version: "0.1"
---

历史项目发起上线审批时，可选项目的范围口径：项目状态为生效或失效、且记录启用。

```ground:caliber
name: 可发起上线审批的项目
predicate: tenant_project.project_status IN ('EFFECTIVE','INVLIAD') AND tenant_project.enable = 'Y'
scope: 历史项目发起上线审批可选项目
evidence: code_path:ProjectApprovalApplication.java:listApprovalSelectableProjects
```

## 需求背景

该口径作用于 `tenant_project` 表（本次语义分析未产出其字段级释义，见文末 REVIEW），命中后进入上线审批发起流程，见 [[rules/online_approval_submit]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: calibers/running_latest_approval.md ---
---
type: caliber
title: 正在审批的最新流程
page_key: running_latest_approval
domain: 微企链立项与项目审批
status: draft
aliases:
  - 审批中最新流程定位
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectBusinessConfigApplication.java:findRunningApproval
contract_version: "0.1"
---

业务系统推送项目配置时，用于定位「当前正在生效的那一次上线审批」的口径：状态为审批中、且为最新版本、且启用。

```ground:caliber
name: 正在审批的最新流程
predicate: tenant_project_approval.wf_status = 'RUNNING' AND tenant_project_approval.is_latest = 'Y' AND tenant_project_approval.enable = 'Y'
scope: 业务系统推送项目配置时定位审批中流程
evidence: code_path:ProjectBusinessConfigApplication.java:findRunningApproval
```

## 需求背景

重新发起审批时原记录 `is_latest` 置 N、新记录置 Y，因此「最新版本」是区分多次审批的关键维度，见 [[rules/reinitiate_online_approval_copy]]；该口径与节点口径 [[calibers/approving_flow_node]] 联合决定推送是否落库，见 [[rules/business_config_push_node_check]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: calibers/approving_flow_node.md ---
---
type: caliber
title: 正在审批的节点
page_key: approving_flow_node
domain: 微企链立项与项目审批
status: draft
aliases:
  - 审批中节点定位
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectBusinessConfigApplication.java:findApprovingFlow
contract_version: "0.1"
---

业务系统推送项目配置时，用于定位「当前审批中节点」的口径：节点状态为审批中且节点启用。

```ground:caliber
name: 正在审批的节点
predicate: tenant_project_approval_flow.node_status = 'APPROVING' AND tenant_project_approval_flow.enable = 'Y'
scope: 业务系统推送项目配置时定位当前节点
evidence: code_path:ProjectBusinessConfigApplication.java:findApprovingFlow
```

## 需求背景

节点状态取值见 [[processes/tenant_project_approval_flow_node_status]]，所在表见 [[tenant_project_approval_flow]]；只有该口径命中且节点类型为方案经理或项目配置时，推送才会落库，见 [[rules/business_config_push_node_check]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。

---END FILE---

---FILE: concepts/wechat_project_initiation.md ---
---
type: concept
title: 微企链立项
page_key: wechat_project_initiation
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
    - tenant_project
sources:
  - db:wechat_project_approval_apply
  - db:tenant_project_approval
contract_version: "0.1"
maps_to: wechat_project_approval_apply
field_targets:
  - wechat_project_approval_apply.sp_no
  - tenant_project_approval.sp_no
adjudication: boundary
also_confused_with:
  - tenant_project_approval
---

「微企链立项」在业务口语中指企微（企业微信）侧提交的项目立项审批申请，落库在 [[wechat_project_approval_apply]]，与产融平台的「项目上线审批」是两个不同概念。

## 需求背景

两者通过 `sp_no`（审批编号）关联，但表不同、状态字段不同、审批主体不同：微企链立项关注企微审批实例是否通过，项目上线审批关注平台工作流是否走完。术语混用会直接导致口径取错——例如把企微审批状态当作工作流状态过滤，参见 [[concepts/approval_status]]。微企链立项侧的数据来源区分手工模拟与企微同步，见 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

---END FILE---

---FILE: concepts/solution_manager.md ---
---
type: concept
title: 方案经理
page_key: solution_manager
domain: 微企链立项与项目审批
status: draft
aliases:
  - solution_manager
  - solution_manager_wxid
oid: 1
scope:
  databases:
    - wechat_project
    - tenant_project
sources:
  - db:wechat_project_approval_apply
  - db:tenant_project_approval
  - code_path:ProjectStatisticsApplication.java:validateBatchChangePlanMgrRows
contract_version: "0.1"
maps_to: wechat_project_approval_apply.solution_manager
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
  - tenant_project_approval.solution_manager_id
adjudication: synonym
also_confused_with:
  - tenant_project_approval.solution_manager_id
---

「方案经理」在企微侧是姓名与企微 ID 双存储：姓名列用于页面展示与逗号分隔的多值场景，企微 ID 列用于企微通知；变更时前方案经理被联动记录到 `old_solution_manager`。

## 需求背景

批量变更方案经理需要校验新方案经理是否属于「SaaS方案部」人员名单，并写入字段历史，见 [[rules/batch_change_solution_manager_department_check]]；模拟立项时方案经理固定为当前登录用户，见 [[rules/manual_create_project_apply]]。注意平台侧审批表使用 `solution_manager_id`，与企微侧姓名列不是同一语义，需按表区分。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

---END FILE---

---FILE: concepts/op_contact.md ---
---
type: concept
title: 运营对接人
page_key: op_contact
domain: 微企链立项与项目审批
status: draft
aliases:
  - op_contact
  - operation_id
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java:validateAndImportData
contract_version: "0.1"
maps_to: wechat_project_approval_apply.op_contact
field_targets:
  - wechat_project_approval_apply.op_contact
adjudication: synonym
also_confused_with: []
---

「运营对接人」在库中以 `operation_id` 形式存储，页面展示时反查姓名，因此同一个业务概念在存储值与展示值上写法不同。

## 需求背景

企微审批导入时，运营对接人（连同风控对接人）在校验通过并更新后，至少一列有值即触发下游同步，见 [[rules/wechat_approval_import_update_only]]。字段所在表见 [[wechat_project_approval_apply]]。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

---END FILE---

---FILE: concepts/data_source.md ---
---
type: concept
title: 数据来源
page_key: data_source
domain: 微企链立项与项目审批
status: draft
aliases:
  - data_source
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:ProjectStatisticsApplication.java:manualCreate
contract_version: "0.1"
maps_to: wechat_project_approval_apply.data_source
field_targets:
  - wechat_project_approval_apply.data_source
adjudication: synonym
also_confused_with: []
---

「数据来源」区分一条立项申请是手工模拟产生还是由企微同步产生：MANUAL 表示模拟立项，WECHAT 表示真实立项。

## 需求背景

模拟立项时该字段被强制写为 MANUAL 并由后端生成审批编号，见 [[rules/manual_create_project_apply]]；企微审批导出要求该字段为 WECHAT，见 [[calibers/wechat_approval_export]]。因此该字段是判断「这条记录是否属于真实企微业务」的首要标志。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

---END FILE---

---FILE: concepts/approval_status.md ---
---
type: concept
title: 审批状态
page_key: approval_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - act_procinst_status
  - wf_status
oid: 1
scope:
  databases:
    - wechat_project
    - tenant_project
sources:
  - db:wechat_project_approval_apply
  - db:tenant_project_approval
contract_version: "0.1"
maps_to: wechat_project_approval_apply.act_procinst_status
field_targets:
  - wechat_project_approval_apply.act_procinst_status
  - tenant_project_approval.wf_status
  - tenant_project_approval_flow.node_status
adjudication: boundary
also_confused_with:
  - tenant_project_approval.wf_status
---

「审批状态」是一个被多套状态字段共享的模糊叫法，必须按表拆开理解：`act_procinst_status` 是企微审批实例状态（数值型 1/2），`wf_status` 是产融平台项目上线审批工作流状态（枚举字符串），`node_status` 是流程节点状态。

## 需求背景

三者取值域与流转规则都不同，参见 [[processes/wechat_apply_approval_status]]、[[processes/tenant_project_approval_wf_status]] 与 [[processes/tenant_project_approval_flow_node_status]]。混用的典型后果是把「企微已通过」当成「平台审批通过」，从而错误触发导出、统计或项目生效逻辑。为减少歧义，页面与规则中应始终写明具体字段名。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

---END FILE---

---FILE: rules/wechat_approval_export_hard_filter.md ---
---
type: rule
title: 企微审批导出硬过滤
page_key: wechat_approval_export_hard_filter
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
contract_version: "0.1"
---

企微审批数据导出时被固化的过滤条件，属于不可被前端查询条件改写的硬约束。

```ground:rule
name: 企微审批导出硬过滤
content: 导出企微审批申请时，固定过滤 act_procinst_status=2 且 data_source=WECHAT，前端查询条件不能改写该过滤。
impact: 确保只导出已通过的企微同步记录。
field_targets:
  - wechat_project_approval_apply.act_procinst_status
  - wechat_project_approval_apply.data_source
evidence: code_path:WechatProjectApprovalApplication.java:exportWechatApprovalInfo
```

## 需求背景

与之对应的数据范围口径见 [[calibers/wechat_approval_export]]；两个过滤字段的取值含义见 [[processes/wechat_apply_approval_status]] 与 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/wechat_approval_import_update_only.md ---
---
type: rule
title: 企微审批导入仅更新
page_key: wechat_approval_import_update_only
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:WechatProjectApprovalApplication.java:validateAndImportData
contract_version: "0.1"
---

企微审批申请的导入校验与写入规则，决定了导入只做更新、不做新增，以及触发下游同步的条件。

```ground:rule
name: 企微审批导入仅更新
content: 导入企微审批申请时仅允许更新已存在的审批编号，不允许新增；为空不更新，"/"置空；审批编号重复、不存在、对接人不存在、字段超长等任一校验失败则整批不更新；更新后运营对接人A或风控对接人A至少一列有值则触发下游同步。
impact: 保证企微审批数据质量并触发下游项目配置同步。
field_targets:
  - wechat_project_approval_apply.sp_no
  - wechat_project_approval_apply.prd
  - wechat_project_approval_apply.op_contact
  - wechat_project_approval_apply.risk_control_contact
  - wechat_project_approval_apply.comment
evidence: code_path:WechatProjectApprovalApplication.java:validateAndImportData
```

## 需求背景

导入以 `sp_no` 为唯一匹配键，因此审批编号必须已存在；更新涉及是否投产、运营对接人、风控对接人与备注等列，其中对接人列语义见 [[concepts/op_contact]]。整批失败的设计避免了部分更新造成的数据不一致。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/online_approval_submit.md ---
---
type: rule
title: 项目上线审批提交规则
page_key: online_approval_submit
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:submit
contract_version: "0.1"
---

区分「暂存」与「提交」两种动作的准入规则：暂存只落库，提交才校验并启动工作流。

```ground:rule
name: 项目上线审批提交规则
content: isDraft=Y 暂存仅落库不启动工作流；isDraft=N 提交时校验审批流程节点（除方案配置外审批人必填）、必须上传商务批复报价文件，生成审批编号后启动工作流。
impact: 保证上线审批数据完整并驱动工作流。
field_targets:
  - tenant_project_approval.wf_status
  - tenant_project_approval.sp_no
evidence: code_path:ProjectApprovalApplication.java:submit
```

## 需求背景

提交成功后审批进入 `PENDING` 并由启动工作流推进到 `RUNNING`，见 [[processes/tenant_project_approval_wf_status]]；必传的商务批复报价文件属于影像分类范围，见 [[tenant_project_approval_flow_file]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/reinitiate_online_approval_copy.md ---
---
type: rule
title: 重新发起上线审批复制规则
page_key: reinitiate_online_approval_copy
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:doCreateApproval
contract_version: "0.1"
---

重新发起上线审批时，对原审批记录的复制与版本切换规则。

```ground:rule
name: 重新发起上线审批复制规则
content: 重新发起时复制原审批主记录、业务信息、流程配置和影像文件，原审批 is_latest 置 N，新审批 is_latest=Y，wf_status=PENDING。
impact: 保留历史审批版本并生成新草稿。
field_targets:
  - tenant_project_approval.is_latest
  - tenant_project_approval.wf_status
  - tenant_project_approval.ref_tenant_project_approval_tenant_project_approval
evidence: code_path:ProjectApprovalApplication.java:doCreateApproval
```

## 需求背景

该规则是「正在审批的最新流程」口径成立的前提——只有最新版本才会被业务系统推送逻辑定位到，见 [[calibers/running_latest_approval]]；新审批从 `PENDING` 起步，见 [[processes/tenant_project_approval_wf_status]]；复制范围包含影像文件，见 [[tenant_project_approval_flow_file]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/effective_project_on_approval_finished.md ---
---
type: rule
title: 审批通过生效项目
page_key: effective_project_on_approval_finished
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished
contract_version: "0.1"
---

上线审批走到终态后自动把关联项目置为生效，实现项目生效的自动化。

```ground:rule
name: 审批通过生效项目
content: 上线审批终态为 FINISHED 时，将审批关联的项目置为已生效（effective），并推送业务系统。
impact: 项目生效自动化。
field_targets:
  - tenant_project.project_status
  - tenant_project_approval.wf_status
evidence: code_path:ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished
```

## 需求背景

触发条件是工作流状态进入 `FINISHED`，见 [[processes/tenant_project_approval_wf_status]]；生效后项目状态发生变化，会影响「可发起上线审批的项目」口径，见 [[calibers/selectable_projects_for_online_approval]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/back_agreement_trigger.md ---
---
type: rule
title: 后补合作协议触发规则
page_key: back_agreement_trigger
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:isStartBackAgreement
contract_version: "0.1"
---

由审批节点属性触发的后补合作协议工作流启动规则。

```ground:rule
name: 后补合作协议触发规则
content: 业务经理节点同意且该节点记录 is_back_agreement=Y 时，启动后补合作协议工作流。
impact: 自动发起后补协议流程。
field_targets:
  - tenant_project_approval_flow_node.is_back_agreement
  - tenant_project_approval_flow_node.node_code
evidence: code_path:ProjectApprovalApplication.java:isStartBackAgreement
```

## 需求背景

判断依赖节点身份（`node_code` 标识业务经理节点）与节点上的后补协议标记，节点表见 [[tenant_project_approval_flow_node]]，节点操作见 [[processes/tenant_project_approval_flow_node_status]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/push_to_ams.md ---
---
type: rule
title: 推送AMS规则
page_key: push_to_ams
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:isPushToAms
contract_version: "0.1"
---

审批通过后是否向下游 AMS 系统推送审批信息的判定规则。

```ground:rule
name: 推送AMS规则
content: 审批通过后，若项目类型为标准项目，或项目类型为常规项目且 is_low_risk=Y，则推送审批信息至 AMS。
impact: 下游 AMS 系统同步审批结果。
field_targets:
  - tenant_project_approval.project_type
  - tenant_project_approval.is_low_risk
evidence: code_path:ProjectApprovalApplication.java:isPushToAms
```

## 需求背景

触发前置于工作流状态进入 `FINISHED`，见 [[processes/tenant_project_approval_wf_status]]；判定依赖项目类型与低风险标记，所在表见 [[tenant_project_approval]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/batch_change_solution_manager_department_check.md ---
---
type: rule
title: 方案经理批量变更部门校验
page_key: batch_change_solution_manager_department_check
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:validateBatchChangePlanMgrRows
contract_version: "0.1"
---

批量变更方案经理时的归属校验与留痕规则。

```ground:rule
name: 方案经理批量变更部门校验
content: 批量变更方案经理时，新方案经理姓名必须在「SaaS方案部」人员名单内，spNo 必须存在，变更写入字段历史（source=BATCH）。
impact: 保证方案经理归属正确。
field_targets:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.sp_no
evidence: code_path:ProjectStatisticsApplication.java:validateBatchChangePlanMgrRows
```

## 需求背景

方案经理在企微侧为姓名多值列并配套企微 ID 列，见 [[concepts/solution_manager]]；变更同时会维护前方案经理列，字段释义见 [[wechat_project_approval_apply]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/manual_create_project_apply.md ---
---
type: rule
title: 模拟立项规则
page_key: manual_create_project_apply
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:manualCreate
contract_version: "0.1"
---

手工创建（模拟）立项数据时的编号生成、来源标记与责任人赋值规则。

```ground:rule
name: 模拟立项规则
content: 模拟立项 spNo 由后端生成（MN-yyyyMMdd-XXXX），dataSource 强制 MANUAL，方案经理固定为当前登录用户，写 MANUAL_CREATE 字段历史。
impact: 支持手工创建测试或补录立项数据。
field_targets:
  - wechat_project_approval_apply.sp_no
  - wechat_project_approval_apply.data_source
  - wechat_project_approval_apply.solution_manager
evidence: code_path:ProjectStatisticsApplication.java:manualCreate
```

## 需求背景

模拟立项产生的记录不会被企微审批导出命中，因为它不满足导出硬过滤中的来源条件，见 [[calibers/wechat_approval_export]] 与 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---FILE: rules/project_phase_auto_transition.md ---
---
type: rule
title: 项目阶段自动流转规则
page_key: project_phase_auto_transition
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
contract_version: "0.1"
---

项目阶段随业务进展自动推进的规则：审批通过后首笔落地时间被更新即进入持续运营。

```ground:rule
name: 项目阶段自动流转规则
content: 审批通过后，若首笔落地时间被更新且项目阶段不是持续运营，则自动将项目阶段置为 OPERATION（持续运营）。
impact: 项目阶段随业务进展自动推进。
field_targets:
  - wechat_project_approval_apply.project_phase
  - wechat_project_approval_apply.first_settlement_time
  - wechat_project_approval_apply.act_procinst_status
evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
```

## 需求背景

触发条件中的「审批已通过」即企微审批实例状态为已通过，见 [[processes/wechat_apply_approval_status]]；阶段取值与遗留值归一见 [[processes/project_phase]]；首笔落地时间字段语义见 [[wechat_project_approval_apply]]。

## 版本演进

规则随项目阶段取值域收敛而稳定：历史值 `TERMINATION` 已归一为 `HANG`，因此本规则只需排除「已是持续运营」的情形。

---END FILE---

---FILE: rules/business_config_push_node_check.md ---
---
type: rule
title: 业务系统推送项目配置节点校验
page_key: business_config_push_node_check
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectBusinessConfigApplication.java:savePush
contract_version: "0.1"
---

业务系统推送项目运营配置时的准入校验：只有流程与节点都处于「正确的位置」才落库。

```ground:rule
name: 业务系统推送项目配置节点校验
content: 业务系统推送项目运营配置时，仅当项目存在 wf_status=RUNNING 且 is_latest=Y 的上线审批，且当前节点为方案经理（PROJECT_MANAGER）或项目配置（PROJECT_CONFIG）且 node_status=APPROVING 时才落库更新；其他节点静默成功不落库。
impact: 控制项目配置推送时机，避免无效更新。
field_targets:
  - tenant_project_approval.wf_status
  - tenant_project_approval.is_latest
  - tenant_project_approval_flow.node_code
  - tenant_project_approval_flow.node_status
evidence: code_path:ProjectBusinessConfigApplication.java:savePush
```

## 需求背景

两个前置口径分别为 [[calibers/running_latest_approval]] 与 [[calibers/approving_flow_node]]；「最新版本」由重新发起规则维护，见 [[rules/reinitiate_online_approval_copy]]；节点状态流转见 [[processes/tenant_project_approval_flow_node_status]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。

---END FILE---

---REVIEW: frontmatter | scope.databases 物理库名---
语义分析未给出各表的物理库名，本批页面按表名前缀暂写为 `wechat_project`（`wechat_project_*`）与 `tenant_project`（`tenant_project_*`）。
该项为推断值而非证据值，需在拿到真实库名（如分库/多 schema 配置）后统一回填。
---END REVIEW---

---REVIEW: table | tenant_project---
`tenant_project` 在多个口径与规则中被引用（`project_status`、`enable`，以及「审批通过生效项目」规则的目标字段），但本次语义分析未产出其字段级释义，故未生成 table 页。
建议补充该表的字段语义后再产出 `tables/tenant_project.md`。
---END REVIEW---

---REVIEW: enum | 企微审批实例状态值域---
`wechat_project_approval_apply.act_procinst_status` 的代码常量只声明 1=审批中、2=已通过，DB 分布中另有 3、4，业务含义未知，且未见代码分支处理。
在确认 3、4 的来源（企微接口返回码？撤销/终止态？）之前，不应写入任何页面作为可比对取值。
---END REVIEW---

---REVIEW: enum | 工作流状态 REVOKED 与影像分类缺口---
`tenant_project_approval.wf_status` 的 DB 分布含 `REVOKED`（已撤销）而代码枚举未声明；`tenant_project_approval_flow_file.catg_id` 的 DB 分布含 `FBP_OA_ATTACHMENT`、`FBP_OA_COMMENT_FILE` 而代码枚举未声明。
本次语义分析的 enum_audit 内容被截断，无法完成逐值比对，故未产出 enums/ 页面；待 enum_audit 完整后按「写值点 + DB 分布」为准补齐枚举页并复核。
---END REVIEW---