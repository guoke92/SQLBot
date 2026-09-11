---FILE: tables/wechat_project_approval_apply.md ---
---
type: table
title: 企微立项审批申请表
page_key: table/wechat_project_approval_apply
domain: 微企链立项与项目审批
status: draft
aliases:
  - wechat_project_approval_apply
  - 企微立项审批申请
  - 立项申请表
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
  - code_path:ProjectStatisticsApplication.java
  - code_path:ProjectApprovalApplication.java#listProjectSpNo
contract_version: "0.1"
---

企微立项审批申请是「微企链立项与项目审批」主题的第一段事实：企微侧立项审批通过后同步进来的记录，既是项目统计的底座，又是上线审批发起时被引用的立项编号来源。本表同时容纳真实立项（企微同步）与模拟立项（人工创建）两类数据，二者靠 `data_source` 区分，导出链路只认真实立项。

本表的字段语义高度依赖代码解释：`sp_no` 是唯一索引与跨系统引用键，对接人系列列存的是运营人员 `operation_id` 而非姓名，产品类型同时保留了编码数组与中文 CSV 两份表达，`system_delivery` 则是一列被复用的历史遗留列。详细口径见 [[calibers/wechat-approval-export-scope]]、[[calibers/project-sp-no-options]]、[[calibers/project-sp-no-proposers]]，状态流转见 [[processes/project-phase]] 与 [[processes/wechat-approval-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，因此本章暂无已证实的业务需求来源；本表所有主张均来自表结构注释与代码字面。

## 版本演进

- 本表字段存在明显的「历史值归一」痕迹：`project_phase` 的 `TERMINATION` 为历史值，读取时归一为挂起（见 [[processes/project-phase]]）。
- `system_delivery` 的 DB 注释为「系统交付方式」，但统计页用它做交付范围过滤、导出时该列又被 `product_type_arr` 的中文覆盖写入，属被复用列，详见 [[concepts/system-delivery-reuse]]、[[rules/export-system-delivery-overwrite]]。
- `statics_op_time` / `statics_op_user` 在列表与详情展示时覆盖 `update_time` / `update_user`，见 [[rules/statics-op-display-override]]。

```ground:table
table: wechat_project_approval_apply
fields:
  - name: sp_no
    meaning: 企微审批编号，表唯一索引（UNI）；企微导入仅按 sp_no 匹配既有记录（只更新不新增），项目上线审批侧按它回写 tenant_project.wechat_audit_no
    evidence: db
  - name: act_procinst_status
    meaning: 企微审批实例当前状态；本层代码仅声明字面 '2'＝审批通过（导出与立项编号下拉固定过滤 '2'），'1'/'3'/'4' 无代码标签
    evidence: code
  - name: act_procinst_id
    meaning: 流程实例ID
    evidence: db
  - name: act_procinst_no
    meaning: 流程申请编号
    evidence: db
  - name: act_procinst_date
    meaning: 审批结束时间
    evidence: db
  - name: sp_pass_time
    meaning: 立项审批通过时间；立项编号下拉按该列倒序
    evidence: code
  - name: data_source
    meaning: 数据来源：WECHAT＝企微同步（真实立项），MANUAL＝模拟立项；导出固定只取 WECHAT
    evidence: code
  - name: prd
    meaning: 是否投产：库内 Y＝已投产、N＝未投产；导出转中文，导入接受『已投产/未投产』或 '/'（写 NULL）
    evidence: code
  - name: solution_manager
    meaning: 方案经理姓名（多人逗号分隔 CSV），由企微 userId 反查得到
    evidence: code
  - name: solution_manager_wxid
    meaning: 方案经理企微 userId 的 JSON 数组字符串（形如 ["340","2742"]），与 solution_manager 联动维护
    evidence: code
  - name: old_solution_manager
    meaning: 前方案经理（历史姓名集合，变更时由 mergeOldSolutionManager 合并前置）
    evidence: code
  - name: bussiness_manager
    meaning: 业务经理姓名（列名拼写为 bussiness）；统计侧由单个企微 userId 反查姓名落库
    evidence: code
  - name: project_manager
    meaning: 项目经理姓名
    evidence: db
  - name: op_contact
    meaning: 运营对接人，存运营人员 operation_id（不是姓名、不是 sys_user id、不是企微 userId）
    evidence: code
  - name: op_contact_group
    meaning: 运营组别，随 op_contact 的 operation_id 反查刷新
    evidence: code
  - name: archives_contact
    meaning: 档案对接人，存 operation_id
    evidence: code
  - name: archives_contact_group
    meaning: 档案组别，随档案对接人 operation_id 刷新
    evidence: code
  - name: risk_control_contact
    meaning: 风控对接人，存 operation_id
    evidence: code
  - name: risk_control_contact_group
    meaning: 风控对接人组别，随风控对接人 operation_id 刷新
    evidence: code
  - name: project_type
    meaning: 本表内为主项目(MAIN)/子项目(SUB)；与 tenant_project_approval.project_type（标准/常规项目）同名不同域
    evidence: code
  - name: product_type
    meaning: 产品类型中文名 CSV（由 product_type_arr 编码翻译）
    evidence: code
  - name: product_type_arr
    meaning: 产品类型编码 JSON 数组，筛选用 LIKE '%"code"%'（先经枚举白名单校验）
    evidence: code
  - name: system_delivery
    meaning: DB 注释为『系统交付方式』，但统计页用它做交付范围过滤（SaaS/Saas+本地化），导出时该列又被 product_type_arr 的中文覆盖写入，属被复用列
    evidence: code
  - name: project_phase
    meaning: 项目阶段：IMPLEMENTATION(实施阶段)/持续运营/挂起；TERMINATION 为历史值读时归一为挂起；『立项阶段』仅用于展示与导入校验、不落库
    evidence: code
  - name: ka_white_label
    meaning: KA 是否贴牌：库内 Y/N，展示与导入模板为『是/否』
    evidence: code
  - name: first_settlement_time
    meaning: 首笔落地时间（DB 注释写『首笔放款时间』）；审批通过后由空变非空会联动项目阶段置为持续运营
    evidence: code
  - name: apply_start_time
    meaning: 发起立项时间；统计页默认排序键，也是方案经理缺失提醒的过滤起点
    evidence: code
  - name: statics_op_time
    meaning: 项目统计更新时间；列表/详情展示时覆盖 update_time
    evidence: code
  - name: statics_op_user
    meaning: 项目统计更新用户；展示时覆盖 update_user
    evidence: code
  - name: custom_field_statistics_one
    meaning: 自定义字段一(统计用)；统计页唯一可编辑列（EDITABLE_FIELDS）
    evidence: code
  - name: custom_field_one
    meaning: 自定义字段一（企微导入可维护，长度校验 500）
    evidence: code
  - name: comment
    meaning: 备注；企微导入上限 200 字，项目立项统计导入上限 500 字
    evidence: code
  - name: project_exception_remark
    meaning: 项目异常备注（统计导入 ≤500 字）
    evidence: code
  - name: capital_org_full_name
    meaning: 资方全称
    evidence: db
  - name: capital_branch_name
    meaning: 资方分支行
    evidence: db
  - name: enterprise_full_name
    meaning: 企业全称
    evidence: db
  - name: business_center
    meaning: 业务中心；统计导入未填时可按业务经理企微部门推导
    evidence: code
  - name: project_focus_level
    meaning: 项目投入关注度
    evidence: db
  - name: project_id
    meaning: 关联的项目 id
    evidence: db
  - name: sp_type
    meaning: 业务类型；统计口径固定 sp_type='金融科技业务'
    evidence: code
  - name: enable
    meaning: 逻辑删除标识（Y/N）
    evidence: db
```

---END FILE---

---FILE: tables/tenant_project_approval.md ---
---
type: table
title: 租户项目上线审批表
page_key: table/tenant_project_approval
domain: 微企链立项与项目审批
status: draft
aliases:
  - tenant_project_approval
  - 上线审批表
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:tenant_project_approval
  - code_path:ProjectApprovalApplication.java
  - code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate
  - code_path:ProjectApprovalDeskApplication.java
contract_version: "0.1"
---

本表承载「项目上线审批」的每次发起实例：一个项目可以有多次审批，靠 `is_latest` 选出当前最新一次，靠 `ref_tenant_project_approval_tenant_project_approval` 串起重新发起的历史链。审批分为新增项目发起与历史项目发起两类（`is_add`），并区分是否为上线审批（`is_online_approval`）。

它与 [[tables/wechat_project_approval_apply]] 的耦合点是 `sp_no`：上线审批发起时引用企微立项审批编号，并在正式首次提交时回写 `tenant_project.wechat_audit_no`（见 [[rules/approval-no-writeback-on-submit]]、[[concepts/sp-no-bridge]]）。工作流状态与节点状态的完整流转见 [[processes/project-approval-workflow-status]]、[[processes/project-approval-node-status]]，终态对租户项目的副作用见 [[processes/tenant-project-status]]。

注意本表的 `project_type`（STANDARD/REGULAR）与立项申请表同名不同域，见 [[concepts/project-type-domain-split]]。按项目取最新审批的口径见 [[calibers/latest-approval-lookup]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源；本表主张均出自代码字面与字段语义。

## 版本演进

- DB 中存在 `wf_status='REVOKED'`（已撤销），代码枚举基线未声明该值，见 [[processes/project-approval-workflow-status]]。
- `project_type` 决定 `flow_code` 与是否推送 AMS，见 [[rules/project-type-drives-flow-and-ams]]。
- `is_low_risk` 由法务经办节点填写并回写主表供 AMS 推送判定，见 [[rules/is-low-risk-writeback]]。

```ground:table
table: tenant_project_approval
fields:
  - name: wf_status
    meaning: 上线审批工作流状态（PENDING/RUNNING/FINISHED/TERMINATED；DB 另有 REVOKED）
    evidence: code
  - name: is_latest
    meaning: 是否该项目当前最新审批；重新发起时把原审批置 N、新审批置 Y
    evidence: code
  - name: is_add
    meaning: 是否随新增项目创建的审批（Y＝新增项目发起，N＝历史项目发起）
    evidence: code
  - name: is_online_approval
    meaning: 是否发起上线审批；关联审批编号下拉只取 Y
    evidence: code
  - name: sp_no
    meaning: 关联的企微立项审批编号，正式首次提交时回写 tenant_project.wechat_audit_no
    evidence: code
  - name: approval_no
    meaning: 上线审批业务编号（平台业务编号服务生成）
    evidence: code
  - name: related_approval_no
    meaning: 关联审批编号；is_online_approval=Y 时被清空为空串
    evidence: code
  - name: is_low_risk
    meaning: 法务经办节点填写的『是否低风险』，回写主表供 AMS 推送判定
    evidence: code
  - name: project_type
    meaning: 上线审批项目类型：STANDARD(标准项目)/REGULAR(常规项目)，决定 flow_code 与是否推送 AMS
    evidence: code
  - name: ref_tenant_project_approval_tenant_project
    meaning: 关联的租户项目 code（非主键 id）
    evidence: code
  - name: ref_tenant_project_approval_tenant_project_approval
    meaning: 重新发起/历史复制时的源审批 code；为空表示首次发起
    evidence: code
  - name: solution_manager_id
    meaning: 方案经理 id 的 JSON 数组字符串（详情接口解析为 List 返回）
    evidence: code
  - name: solution_manager_name
    meaning: 方案经理姓名 JSON 数组字符串
    evidence: code
  - name: initiator_user_id
    meaning: 审批发起人 sys_user id；拒绝/退回通知只发给该人
    evidence: code
  - name: initiate_time
    meaning: 发起时间；工作流启动成功时写入
    evidence: code
  - name: complete_time
    meaning: 完成时间；wf_status∈{FINISHED,TERMINATED} 时写入
    evidence: code
  - name: wf_procdef_key
    meaning: 工作流流程定义 key
    evidence: code
  - name: act_procinst_id
    meaning: 工作流流程实例 id
    evidence: code
```

---END FILE---

---FILE: tables/wechat_project_approval_flow_file.md ---
---
type: table
title: 企微立项审批流程附件表
page_key: table/wechat_project_approval_flow_file
domain: 微企链立项与项目审批
status: draft
aliases:
  - wechat_project_approval_flow_file
  - 审批节点附件表
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_flow_file
contract_version: "0.1"
---

本表存放在企微立项审批各节点上产生的附件。本次语义分析只给出了一个字段的证据，即附件分类 `catg_id`，因此本页仅覆盖该列，不对本表的其余结构做任何推断。

`catg_id` 的关键事实是：DB 实际出现的取值（`FBP_OA_ATTACHMENT`、`FBP_OA_COMMENT_FILE`）超出了代码基线的枚举覆盖范围，属于「代码枚举未覆盖 DB 实际分布」的一类，阅读附件分类时不能只依赖代码枚举。与审批主流程的关系参见 [[tables/wechat_project_approval_apply]]、[[processes/wechat-approval-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- `catg_id` 的代码基线枚举未覆盖 DB 实际分布值，属于待收敛的枚举缺口，见文末 REVIEW。

```ground:table
table: wechat_project_approval_flow_file
fields:
  - name: catg_id
    meaning: 审批节点附件分类；DB 实际出现 FBP_OA_ATTACHMENT/FBP_OA_COMMENT_FILE（代码基线枚举未覆盖）
    evidence: db
```

---END FILE---

---FILE: processes/project-approval-workflow-status.md ---
---
type: process
title: 项目上线审批工作流状态机
page_key: process/tenant_project_approval_wf_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批 wf_status
  - tenant_project_approval.wf_status
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#createInitialApproval
  - code_path:ProjectApprovalApplication.java#submit
  - code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus
  - code_path:ProjectApprovalApplication.java#handleFlowAndNodeStatus
  - code_path:ProjectApprovalApplication.java#doCreateApproval
  - code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate
  - db:tenant_project_approval
contract_version: "0.1"
---

工作流状态描述的是「一次上线审批单据」的生命周期，字段落在 [[tables/tenant_project_approval]] 的 `wf_status` 上。它从「由项目创建逻辑预生成的草稿」开始，经发起后进入审批中，最终收敛到完成（通过）或终止（驳回/退回结束）；重新发起会以复制的方式开出一条新记录并把旧的置为非最新，因此状态机是沿记录序列而非沿单条记录循环的。

两个需要特别留意的点：一是状态写入与工作流引擎启动是两步，引擎启动失败会降级停留在待发起（见 [[rules/workflow-start-failure-degrade]]）；二是 DB 分布中存在代码枚举基线没有的 `REVOKED`。

节点粒度的状态请见 [[processes/project-approval-node-status]]，终态对租户项目状态的影响见 [[processes/tenant-project-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- `REVOKED`（已撤销）仅来自 DB 实际分布，代码枚举基线未声明，属待补枚举。
- 重新发起路径的前置校验要求记录为最新（`is_latest=Y`），否则抛出异常，见 [[rules/is-latest-uniqueness]]。

```ground:process
name: 项目上线审批工作流状态机
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起/草稿
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 审批完成（通过）
    source: code_enum
  - value: TERMINATED
    label: 审批终止（驳回/退回结束）
    source: code_enum
  - value: REVOKED
    label: 已撤销（代码枚举基线未声明，DB 实际存在）
    source: db_dist
transitions:
  - from: "—"
    event: 项目创建后生成审批记录（isAdd=Y+挡板开+产品白名单）
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#createInitialApproval"
  - from: PENDING
    event: submit(isDraft=N) 业务落库
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#submit（copySubmitFields 中 setWfStatus(PENDING)）"
  - from: PENDING
    event: 工作流启动成功 startWorkflowAndUpdateStatus
    to: RUNNING
    evidence: "code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus"
  - from: PENDING
    event: 工作流启动异常（降级，仅记 ERROR）
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus（catch 分支）"
  - from: RUNNING
    event: 流程结束通知 approveResult=pass
    to: FINISHED
    evidence: "code_path:ProjectApprovalApplication.java#handleFlowAndNodeStatus + ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: RUNNING
    event: 流程结束通知 approveResult=reject/back
    to: TERMINATED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: FINISHED
    event: 重新发起 createApproval（复制原审批）
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#doCreateApproval"
  - from: PENDING
    event: 非最新记录再次重新发起
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#doCreateApproval（is_latest≠Y 抛异常前置校验）"
```

---END FILE---

---FILE: processes/project-approval-node-status.md ---
---
type: process
title: 上线审批节点状态机
page_key: process/tenant_project_approval_flow_node_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批节点状态
  - tenant_project_approval_flow.node_status
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate
  - code_path:ProjectApprovalDeskApplication.java#doBack
  - code_path:ProjectApprovalDeskApplication.java#doReject
  - code_path:ProjectApprovalDeskApplication.java#doTransfer
contract_version: "0.1"
---

节点状态是工作流状态的下钻粒度：单据级状态（[[processes/project-approval-workflow-status]]）表达整条审批走到哪一步，节点状态表达某个人手上的待办被推到什么程度。入库位置为 `tenant_project_approval_flow.node_status`（该表本次未提供字段级语义，见文末 REVIEW）。

值得注意的是三种「非终态写法」：工作台退回 `back` 后节点回到审批中；转审 `transfer` 后节点名不变、状态仍为审批中；流程级 `back` 会使节点落到已拒绝。工作台侧的三个动作也是「拒绝/退回通知只发给发起人」这条规则的触发源（见 [[rules/reject-notify-initiator]]）。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 撤回/退回与驳回在节点状态上表现不同（前者回审批中、后者落已拒绝），该差异属既有行为，本次无文档主张可佐证其历史。

```ground:process
name: 上线审批节点状态机
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
    event: 待抢/待办通知（taskNoticeType 1/2）
    to: APPROVING
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 任务办理完成 approveResult=pass
    to: APPROVED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 任务办理完成 approveResult=back
    to: PENDING
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 流程结束 approveResult=reject/back
    to: REJECTED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 工作台退回 back
    to: APPROVING
    evidence: "code_path:ProjectApprovalDeskApplication.java#doBack（updateFlowNodeStatus APPROVING）"
  - from: APPROVING
    event: 工作台驳回 reject
    to: REJECTED
    evidence: "code_path:ProjectApprovalDeskApplication.java#doReject"
  - from: APPROVING
    event: 工作台转审 transfer（节点名不变）
    to: APPROVING
    evidence: "code_path:ProjectApprovalDeskApplication.java#doTransfer"
```

---END FILE---

---FILE: processes/project-phase.md ---
---
type: process
title: 项目阶段状态机
page_key: process/wechat_project_approval_apply_project_phase
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目阶段
  - project_phase
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
  - code_path:ProjectStatisticsApplication.java#applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - code_path:ProjectStatisticsApplication.java#normalizeLegacyProjectPhaseCode
  - code_path:ProjectStatisticsApplication.java#manualCreate
contract_version: "0.1"
---

项目阶段落在 [[tables/wechat_project_approval_apply]] 的 `project_phase` 上，它表达的是项目在「实施—持续运营—挂起」之间的所处位置。驱动阶段变化的关键事件不是审批本身，而是审批通过之后首笔落地时间的第一次写入：由空变非空时把阶段推进到持续运营（见 [[rules/phase-auto-operation-on-first-settlement]]）。

本状态机有两个易错点：其一，`TERMINATION` 是历史值，读取时需要归一为挂起；其二，「立项阶段」只是一个展示与导入校验用的字面，不落库（见 [[rules/project-phase-import-restriction]]）。另外两个常量 `PROJECT_PHASE_OPERATION`、`PROJECT_PHASE_HANG` 的字面值未在本层给出，本页只按常量名登记。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- `TERMINATION` → 挂起的读时归一，属历史值收敛，见 [[rules/legacy-termination-normalize]]。

```ground:process
name: 项目阶段
field: wechat_project_approval_apply.project_phase
states:
  - value: IMPLEMENTATION
    label: 实施阶段（代码字面）
    source: code_enum
  - value: PROJECT_PHASE_OPERATION
    label: 持续运营（常量，字面值未在本层给出）
    source: code_enum
  - value: PROJECT_PHASE_HANG
    label: 挂起（常量，字面值未在本层给出）
    source: code_enum
  - value: TERMINATION
    label: 历史值，读取时归一为挂起（代码字面）
    source: code_enum
  - value: 立项阶段
    label: 仅展示/导入校验用，不落库（审批通过后不允许导入）
    source: code_enum
transitions:
  - from: 任意
    event: act_procinst_status='2' 且首笔落地时间由空变非空且当前非持续运营
    to: PROJECT_PHASE_OPERATION
    evidence: "code_path:ProjectStatisticsApplication.java#applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved"
  - from: TERMINATION
    event: 读取归一化
    to: PROJECT_PHASE_HANG
    evidence: "code_path:ProjectStatisticsApplication.java#normalizeLegacyProjectPhaseCode"
  - from: 任意
    event: 模拟立项创建（固定写 IMPLEMENTATION）
    to: IMPLEMENTATION
    evidence: "code_path:ProjectStatisticsApplication.java#manualCreate"
```

---END FILE---

---FILE: processes/tenant-project-status.md ---
---
type: process
title: 租户项目状态机
page_key: process/tenant_project_project_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - 租户项目状态
  - tenant_project.project_status
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#effectiveProjectOnApprovalFinished
  - code_path:ProjectApprovalApplication.java#invalidateHistoricalProjectOnSubmit
contract_version: "0.1"
---

租户项目状态是上线审批的下游结果：审批走到终态通过时，对应租户项目被置为已生效；非新增项目正式发起上线审批时，历史项目被置为已失效。也就是说，同一个项目在「重新走一遍上线审批」的过程中会先失效、通过后再生效。

本状态机所依附的表 `tenant_project` 未在本次语义分析中给出字段级证据，其表名字面也未在 DB 实测中出现，因此本页状态与流转按 DO `TenantProjectDO` 与系统文档标注，仅作结构登记，不作为字段级契约使用。上游见 [[processes/project-approval-workflow-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 失效路径 `invalidateHistoricalProjectOnSubmit` 在本次给出的代码切片内未见调用点，需核实调用方（见文末 REVIEW）。
- 枚举名拼写 `ProjectStatusEnum.INVLIAD`（已失效）按代码原样登记，疑为历史拼写。

```ground:process
name: 租户项目状态（表名字面未在本层 DB 实测出现，按 DO TenantProjectDO/系统文档标注）
field: tenant_project.project_status
states:
  - value: ProjectStatusEnum.EFFECTIVE
    label: 已生效
    source: code_enum
  - value: ProjectStatusEnum.INVLIAD
    label: 已失效（代码枚举拼写如此）
    source: code_enum
transitions:
  - from: "—"
    event: 上线审批终态通过 effectiveProjectOnApprovalFinished → tenantProjectApplication.effective
    to: ProjectStatusEnum.EFFECTIVE
    evidence: "code_path:ProjectApprovalApplication.java#effectiveProjectOnApprovalFinished"
  - from: ProjectStatusEnum.EFFECTIVE/ProjectStatusEnum.INVLIAD
    event: 非新增项目正式发起上线审批 invalidateHistoricalProjectOnSubmit → tenantProjectApplication.invalid
    to: ProjectStatusEnum.INVLIAD
    evidence: "code_path:ProjectApprovalApplication.java#invalidateHistoricalProjectOnSubmit（注意：该方法在当前给出的代码切片内未见调用点，需核实调用方）"
```

---END FILE---

---FILE: processes/wechat-approval-status.md ---
---
type: process
title: 企微立项审批实例状态
page_key: process/wechat_project_approval_apply_act_procinst_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - act_procinst_status
  - 企微审批实例状态
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
  - code_path:ProjectApprovalApplication.java#listProjectSpNo
contract_version: "0.1"
---

严格来说这不是一个由本系统驱动的状态机，而是对企微侧审批实例状态的镜像登记：[[tables/wechat_project_approval_apply]] 的 `act_procinst_status` 保存的是从企微同步过来的实例状态。本系统代码只声明并使用了其中一个字面值——`'2'` 表示审批通过，导出链路与立项审批编号下拉都固定过滤 `'2'`（见 [[calibers/wechat-approval-export-scope]]、[[calibers/project-sp-no-options]]）。

其余取值 `'1'`、`'3'`、`'4'` 仅出现在 DB 分布中，代码里没有对应的字面或标签，因此它们的业务含义在本层不可判定，任何针对它们的解释都属于推测。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该列的状态语义长期只用到 `'2'`，其余取值缺少代码标签，属待补语义（见文末 REVIEW）。

```ground:process
name: 企微立项审批状态
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: "1"
    label: 代码未声明（DB 分布值）
    source: db_dist
  - value: "2"
    label: 审批通过（代码固定过滤字面 '2'）
    source: code_enum
  - value: "3"
    label: 代码未声明（DB 分布值）
    source: db_dist
  - value: "4"
    label: 代码未声明（DB 分布值）
    source: db_dist
transitions: []
```

---END FILE---

---FILE: calibers/wechat-approval-export-scope.md ---
---
type: caliber
title: 企微立项审批导出范围
page_key: caliber/wechat-approval-export-scope
domain: 微企链立项与项目审批
status: draft
aliases:
  - 导出固定过滤
  - exportWechatApprovalInfo 口径
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
---

导出接口的取数范围由两个固定条件决定：审批实例状态必须是通过（`'2'`），数据来源必须是企微同步（`WECHAT`）。这一条同时排除了两类数据——未通过的立项审批，以及人工创建的模拟立项。

实现上的关键点是：固定条件写在动态条件之后，且前端入参不可改写，也就是说用户在前端选什么都没法把模拟立项或未通过审批带出来。相关字段语义见 [[tables/wechat_project_approval_apply]]，模拟立项与真实立项的区分见 [[concepts/data-source-real-vs-manual]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 企微立项审批导出范围
predicate: "wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.data_source = 'WECHAT'"
scope: 导出接口 /cust-web/wechatApproval/export，固定过滤写在动态条件之后，前端入参不可改写
evidence: "code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo"
```

---END FILE---

---FILE: calibers/project-sp-no-options.md ---
---
type: caliber
title: 立项审批编号下拉范围
page_key: caliber/project-sp-no-options
domain: 微企链立项与项目审批
status: draft
aliases:
  - 立项审批编号下拉
  - listProjectSpNo 口径
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#listProjectSpNo
contract_version: "0.1"
---

上线审批发起页的「立项审批编号」下拉只能看到两类记录：审批已通过（`act_procinst_status='2'`）且未被逻辑删除（`enable='Y'`）。排序键是 `sp_pass_time` 倒序，即最近通过的排在最前。

这条口径决定了上线审批可以引用哪些立项（见 [[concepts/sp-no-bridge]]），与导出范围的区别在于它额外收紧了 `enable`，见 [[calibers/wechat-approval-export-scope]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 立项审批编号下拉范围
predicate: "wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.enable = 'Y'"
scope: 上线审批发起页『立项审批编号』下拉
evidence: "code_path:ProjectApprovalApplication.java#listProjectSpNo"
```

---END FILE---

---FILE: calibers/project-sp-no-proposers.md ---
---
type: caliber
title: 立项审批编号取关联人员
page_key: caliber/project-sp-no-proposers
domain: 微企链立项与项目审批
status: draft
aliases:
  - getProposerByApprovalNo 口径
  - 按 spNo 反查人员
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#getProposerByApprovalNo
contract_version: "0.1"
---

当用户在发起页选定了立项审批编号后，系统按该编号反查这条立项上的方案经理、业务经理与运营人，用于带出审批参与人。取数条件是 `sp_no` 等值匹配且记录未逻辑删除。

这条口径保证了「一个 sp_no 只对应一条立项」，因为 `sp_no` 本身是唯一索引；人员字段的存储形态（姓名 CSV、企微 userId JSON 数组、运营人员 operation_id）各不相同，见 [[concepts/solution-manager-identity]]、[[concepts/operation-id-contact-reference]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 立项审批编号取关联人员
predicate: "wechat_project_approval_apply.sp_no = ? AND enable = 'Y'"
scope: 按 spNo 反查方案经理/业务经理/运营人
evidence: "code_path:ProjectApprovalApplication.java#getProposerByApprovalNo"
```

---END FILE---

---FILE: calibers/latest-approval-lookup.md ---
---
type: caliber
title: 项目最新有效上线审批
page_key: caliber/latest-approval-lookup
domain: 微企链立项与项目审批
status: draft
aliases:
  - findLatestApprovalByProjectCode 口径
  - is_latest 取数口径
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#findLatestApprovalByProjectCode
contract_version: "0.1"
---

按项目查「当前该看哪一次上线审批」时，条件是未逻辑删除且被标记为最新（`is_latest='Y'`）。分页之后还会后置填充 `approvalIsAdd` / `approvalWfStatus`，用于控制列表按钮的显隐——也就是说按钮能不能点，取决于这条口径选出来的那条审批的状态，而不是历史审批的状态。

`is_latest` 的维护规则见 [[rules/is-latest-uniqueness]]，字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 项目最新有效上线审批
predicate: "tenant_project_approval.enable = 'Y' AND tenant_project_approval.is_latest = 'Y'"
scope: 按项目 code 取最新审批；分页后置填充 approvalIsAdd/approvalWfStatus 控制按钮显隐
evidence: "code_path:ProjectApprovalApplication.java#findLatestApprovalByProjectCode"
```

---END FILE---

---FILE: concepts/operation-id-contact-reference.md ---
---
type: concept
title: 对接人引用体系（operation_id）
page_key: concept/operation-id-contact-reference
domain: 微企链立项与项目审批
status: draft
aliases:
  - 运营对接人
  - op_contact 语义
  - operation_id 对接人
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.op_contact
  - wechat_project_approval_apply.archives_contact
  - wechat_project_approval_apply.risk_control_contact
field_targets:
  - table: wechat_project_approval_apply
    field: op_contact
  - table: wechat_project_approval_apply
    field: op_contact_group
  - table: wechat_project_approval_apply
    field: archives_contact
  - table: wechat_project_approval_apply
    field: archives_contact_group
  - table: wechat_project_approval_apply
    field: risk_control_contact
  - table: wechat_project_approval_apply
    field: risk_control_contact_group
adjudication: 三个对接人列（运营/档案/风控）在库内存放的是运营人员 operation_id，既不是姓名、也不是 sys_user id、也不是企微 userId；对应的 *_group 列随各自对接人的 operation_id 反查刷新，属于派生冗余列，不应手工写入。
also_confused_with:
  - wechat_project_approval_apply.solution_manager_wxid（企微 userId，另一套标识体系）
  - wechat_project_approval_apply.solution_manager（姓名 CSV）
  - tenant_project_approval.initiator_user_id（sys_user id）
---

「对接人」在本主题里存在三套并行的人员标识：企微 userId（`solution_manager_wxid`）、sys_user id（`tenant_project_approval.initiator_user_id`）、以及运营人员 `operation_id`（`op_contact` 家族）。这三套互不通用，写统计导入或做人员匹配时最容易在此处串号。

对接人列的第二个特征是「成对出现」：每个 contact 列都配一个 group 列，group 由 contact 反查刷新而非独立录入（见 [[rules/op-contact-group-refresh]]）。因此当 contact 被改而 group 未刷新时，数据即处于不一致状态。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[concepts/solution-manager-identity]]、[[rules/op-contact-group-refresh]]。

---END FILE---

---FILE: concepts/project-type-domain-split.md ---
---
type: concept
title: project_type 同名异域
page_key: concept/project-type-domain-split
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目类型歧义
  - project_type 同名不同域
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.project_type
  - tenant_project_approval.project_type
field_targets:
  - table: wechat_project_approval_apply
    field: project_type
  - table: tenant_project_approval
    field: project_type
adjudication: 两表的 project_type 列名相同但取值域完全不同：立项申请表中是主项目(MAIN)/子项目(SUB)，上线审批表中是标准项目(STANDARD)/常规项目(REGULAR)。跨表引用 project_type 时必须显式带上表名。
also_confused_with:
  - tenant_project_approval.project_type 决定 flow_code 与 AMS 推送，立项表的 project_type 不承担该职责
---

这是本主题里最容易写错的同名列：两个核心表都叫 `project_type`，但一个描述项目结构层级（主/子），另一个描述上线审批的流程类型（标准/常规），并且后者还承担了决定工作流定义与是否推送 AMS 的职责（见 [[rules/project-type-drives-flow-and-ams]]）。

在 SQL、接口参数、前端字典任意一层省略表名限定都可能造成误用；本概念仅做歧义标注，不改变任何一列的取值域。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[tables/tenant_project_approval]]。

---END FILE---

---FILE: concepts/sp-no-bridge.md ---
---
type: concept
title: sp_no 立项—上线审批桥接键
page_key: concept/sp-no-bridge
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微审批编号
  - wechat_audit_no
  - 立项编号回写
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
  - code_path:ProjectApprovalApplication.java
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.sp_no
  - tenant_project_approval.sp_no
  - tenant_project.wechat_audit_no
field_targets:
  - table: wechat_project_approval_apply
    field: sp_no
  - table: tenant_project_approval
    field: sp_no
adjudication: sp_no 是企微立项审批的业务编号，在立项申请表上是唯一索引；上线审批表以它引用立项，并在正式首次提交时把它回写到 tenant_project.wechat_audit_no。同一编号在三处出现，指向的是同一次企微立项审批。
also_confused_with:
  - tenant_project_approval.approval_no（上线审批业务编号，平台业务编号服务生成，与 sp_no 不同源）
  - tenant_project_approval.related_approval_no（关联审批编号）
---

`sp_no` 把「企微侧」与「平台侧」串起来：企微同步以它为匹配键做只更新不新增的 upsert（见 [[rules/wechat-import-match-by-sp-no]]），平台发起上线审批时以它引用立项并回写租户项目（见 [[rules/approval-no-writeback-on-submit]]），可用编号范围由 [[calibers/project-sp-no-options]] 决定。

它与 `approval_no` 的区别必须分清：后者是上线审批自己的业务编号，由平台业务编号服务生成，与企微无关。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[tables/tenant_project_approval]]。

---END FILE---

---FILE: concepts/product-type-coding.md ---
---
type: concept
title: 产品类型双表示（编码数组与中文 CSV）
page_key: concept/product-type-coding
domain: 微企链立项与项目审批
status: draft
aliases:
  - product_type_arr
  - 产品类型编码
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.product_type_arr
  - wechat_project_approval_apply.product_type
field_targets:
  - table: wechat_project_approval_apply
    field: product_type_arr
  - table: wechat_project_approval_apply
    field: product_type
adjudication: 同一份产品类型信息在本表存两份——product_type_arr 是编码 JSON 数组（用于筛选），product_type 是中文名 CSV（由编码翻译而来，用于展示）。两者是一对翻译关系，不是两个独立的业务字段。
also_confused_with:
  - wechat_project_approval_apply.system_delivery（导出时会被产品类型中文覆盖写入的复用列，见 concepts/system-delivery-reuse）
---

筛选走编码、展示走中文，是本主题里「一物两存」的典型。筛选实现用 JSON 字符串的 `LIKE '%"code"%'` 匹配编码数组，并且会先做一次枚举白名单校验再拼条件（见 [[rules/product-type-arr-like-filter]]）。

由于导出流程还会把中文产品类型写进 `system_delivery` 列（见 [[rules/export-system-delivery-overwrite]]），在排查导出的产品类型列时要注意这一层覆盖关系。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[concepts/system-delivery-reuse]]。

---END FILE---

---FILE: concepts/solution-manager-identity.md ---
---
type: concept
title: 方案经理身份联动（姓名 CSV / 企微 userId / 历史值）
page_key: concept/solution-manager-identity
domain: 微企链立项与项目审批
status: draft
aliases:
  - 方案经理标识
  - old_solution_manager
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.solution_manager
  - wechat_project_approval_apply.solution_manager_wxid
  - wechat_project_approval_apply.old_solution_manager
  - tenant_project_approval.solution_manager_id
  - tenant_project_approval.solution_manager_name
field_targets:
  - table: wechat_project_approval_apply
    field: solution_manager
  - table: wechat_project_approval_apply
    field: solution_manager_wxid
  - table: wechat_project_approval_apply
    field: old_solution_manager
  - table: tenant_project_approval
    field: solution_manager_id
  - table: tenant_project_approval
    field: solution_manager_name
adjudication: 方案经理在库内是多值：姓名以逗号分隔 CSV 存放（solution_manager / solution_manager_name），身份以 JSON 数组字符串存放（solution_manager_wxid / solution_manager_id），姓名由企微 userId 反查得到；变更时旧姓名由 mergeOldSolutionManager 合并进 old_solution_manager。姓名与 id 必须联动维护，不可单独更新。
also_confused_with:
  - wechat_project_approval_apply.op_contact（存 operation_id，另一套标识）
  - tenant_project_approval.initiator_user_id（sys_user id，单值）
---

方案经理字段家族体现了「先有 id、后反查姓名」的落库顺序：写库时先确定企微 userId 数组，再由 userId 反查姓名组成 CSV。`old_solution_manager` 保留了历史姓名的合并结果，用于回答「这个人曾经是不是方案经理」。

由此推导出一条运维事实：方案经理缺失是可以被检测出来的，统计页有基于 `apply_start_time` 的缺失提醒（见 [[rules/solution-manager-missing-reminder]]）。身份体系的全景见 [[concepts/operation-id-contact-reference]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该概念的历史变更记录。

相关页面：[[tables/wechat_project_approval_apply]]、[[tables/tenant_project_approval]]。

---END FILE---

---FILE: concepts/data-source-real-vs-manual.md ---
---
type: concept
title: 真实立项与模拟立项（data_source）
page_key: concept/data-source-real-vs-manual
domain: 微企链立项与项目审批
status: draft
aliases:
  - 模拟立项
  - WECHAT/MANUAL
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
  - code_path:ProjectStatisticsApplication.java#manualCreate
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.data_source
field_targets:
  - table: wechat_project_approval_apply
    field: data_source
adjudication: data_source='WECHAT' 表示由企微同步来的真实立项，'MANUAL' 表示人工创建的模拟立项（模拟立项创建时项目阶段固定写 IMPLEMENTATION）。导出链路固定只取 WECHAT，模拟立项不会被导出。
also_confused_with:
  - act_procinst_status（审批实例状态，与数据来源是两个维度）
---

同一张立项申请表里混着两类业务性质不同的数据，区分它们的唯一依据就是 `data_source`。模拟立项的用途是让统计与流程可以在缺少真实企微审批的情况下先跑起来，但它并不代表真实业务事实。

判断影响面时要把这条与导出范围连起来看：[[calibers/wechat-approval-export-scope]] 固定过滤 `WECHAT`，因此任何「导出里没有某条立项」的问题，先要确认它是不是模拟数据。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 模拟立项创建固定写 `IMPLEMENTATION`，见 [[processes/project-phase]]。

相关页面：[[tables/wechat_project_approval_apply]]、[[calibers/wechat-approval-export-scope]]。

---END FILE---

---FILE: concepts/system-delivery-reuse.md ---
---
type: concept
title: system_delivery 复用列
page_key: concept/system-delivery-reuse
domain: 微企链立项与项目审批
status: draft
aliases:
  - 系统交付方式
  - system_delivery
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.system_delivery
field_targets:
  - table: wechat_project_approval_apply
    field: system_delivery
adjudication: 该列 DB 注释为『系统交付方式』，但在统计页被用作交付范围过滤（SaaS/Saas+本地化），在导出时又被 product_type_arr 的中文覆盖写入。一列承担三种语义，读该列前必须先确认上下文。
also_confused_with:
  - wechat_project_approval_apply.product_type（产品类型中文 CSV，导出会写到 system_delivery）
---

这是一条典型的「列语义漂移」：注释、统计过滤、导出写入三者说法不一致。因为导出会覆盖写入，所以从导出文件里看到的 `system_delivery` 未必是统计页过滤所依据的那个值。

处理此类字段的原则是先锁定读它的代码路径（统计过滤 vs 导出），再判断取值含义；不要依赖 DB 注释（见 [[rules/export-system-delivery-overwrite]]）。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该列被复用的现状属历史遗留，本次无文档主张可佐证其变更时间。

相关页面：[[tables/wechat_project_approval_apply]]、[[concepts/product-type-coding]]。

---END FILE---

---FILE: rules/wechat-import-match-by-sp-no.md ---
---
type: rule
title: 企微导入按 sp_no 匹配既有记录
page_key: rule/wechat-import-match-by-sp-no
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微导入只更新不新增
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
contract_version: "0.1"
---

企微同步写入立项申请时，匹配键只有一个：`sp_no`。匹配到既有记录就更新，匹配不到不会新增。因此企微侧产生的数据能否进入本系统，取决于对应的 `sp_no` 记录是否已经存在。

这条规则解释了为什么 `sp_no` 是唯一索引，也解释了「企微明明审批通过了但平台查不到」的一类问题的排查方向。相关桥接关系见 [[concepts/sp-no-bridge]]，字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 企微导入按 sp_no 匹配既有记录
subject: wechat_project_approval_apply.sp_no
evidence: db
source_meaning: 企微审批编号，表唯一索引（UNI）；企微导入仅按 sp_no 匹配既有记录（只更新不新增），项目上线审批侧按它回写 tenant_project.wechat_audit_no
```

---END FILE---

---FILE: rules/approval-no-writeback-on-submit.md ---
---
type: rule
title: 正式首次提交回写 wechat_audit_no
page_key: rule/approval-no-writeback-on-submit
domain: 微企链立项与项目审批
status: draft
aliases:
  - 立项编号回写租户项目
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
  - db:tenant_project_approval
contract_version: "0.1"
---

上线审批单据上填写的 `sp_no` 会在「正式首次提交」时被回写到 `tenant_project.wechat_audit_no`，把项目与企微立项审批正式绑定。触发条件是首次提交且非草稿，草稿保存不会产生回写。

这里的「首次」由 `ref_tenant_project_approval_tenant_project_approval` 是否为空界定：为空表示首次发起（见 [[tables/tenant_project_approval]]）。桥接键的全局含义见 [[concepts/sp-no-bridge]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 正式首次提交回写 wechat_audit_no
subject: tenant_project_approval.sp_no
evidence: code
source_meaning: 关联的企微立项审批编号，正式首次提交时回写 tenant_project.wechat_audit_no
```

---END FILE---

---FILE: rules/online-approval-clears-related-no.md ---
---
type: rule
title: 上线审批清空关联审批编号
page_key: rule/online-approval-clears-related-no
domain: 微企链立项与项目审批
status: draft
aliases:
  - related_approval_no 清空
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

当单据是上线审批（`is_online_approval='Y'`）时，`related_approval_no` 会被清空为空串，而不是置 NULL。这意味着「没有关联审批」在本表中存在两种可能的物理表达（空串与 NULL），读数据时应按空值统一处理。

配套的口径是：关联审批编号下拉只取 `is_online_approval='Y'` 的记录。字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 上线审批清空关联审批编号
subject: tenant_project_approval.related_approval_no
evidence: code
source_meaning: 关联审批编号；is_online_approval=Y 时被清空为空串
```

---END FILE---

---FILE: rules/is-latest-uniqueness.md ---
---
type: rule
title: is_latest 唯一最新维护
page_key: rule/is-latest-uniqueness
domain: 微企链立项与项目审批
status: draft
aliases:
  - 重新发起置非最新
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#doCreateApproval
contract_version: "0.1"
---

同一项目可以有多条上线审批记录，但只允许一条是最新：重新发起时把原审批置 `N`、新审批置 `Y`。并且只有最新记录才允许再次重新发起，否则前置校验直接抛异常（见 [[processes/project-approval-workflow-status]] 中 PENDING 的自环transition）。

取用最新审批的口径见 [[calibers/latest-approval-lookup]]，字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: is_latest 唯一最新维护
subject: tenant_project_approval.is_latest
evidence: code
source_meaning: 是否该项目当前最新审批；重新发起时把原审批置 N、新审批置 Y
```

---END FILE---

---FILE: rules/reject-notify-initiator.md ---
---
type: rule
title: 拒绝与退回通知只发发起人
page_key: rule/reject-notify-initiator
domain: 微企链立项与项目审批
status: draft
aliases:
  - 通知只发给 initiator_user_id
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalDeskApplication.java#doReject
  - code_path:ProjectApprovalDeskApplication.java#doBack
contract_version: "0.1"
---

审批被拒绝或退回时，通知的接收人是单据上的审批发起人（`initiator_user_id`，存的是 sys_user id），不包含方案经理、也不包含当前处理人。若发起人已离职或 id 失效，通知会静默丢失，排查「审批被退了但没人收到通知」时应先看这一列。

通知触发点对应工作台的驳回/退回动作，节点状态变化见 [[processes/project-approval-node-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 拒绝与退回通知只发发起人
subject: tenant_project_approval.initiator_user_id
evidence: code
source_meaning: 审批发起人 sys_user id；拒绝/退回通知只发给该人
```

---END FILE---

---FILE: rules/workflow-start-failure-degrade.md ---
---
type: rule
title: 工作流启动失败降级停留在待发起
page_key: rule/workflow-start-failure-degrade
domain: 微企链立项与项目审批
status: draft
aliases:
  - 启动异常仅记 ERROR
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus
contract_version: "0.1"
---

业务落库与工作流引擎启动是两步：先落库（此时状态为待发起），再启动工作流并把状态改为审批中。若引擎启动抛异常，系统只记 ERROR 日志并保持待发起，不阻塞业务代码，也不回滚业务落库——结果就是一条「看起来提交成功但流程没走起来」的单据。

对应的自环transition见 [[processes/project-approval-workflow-status]]；`initiate_time` 只在启动成功时写入，可作为判断是否真的启动过的旁证。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 工作流启动失败降级停留在待发起
subject: tenant_project_approval.wf_status
evidence: code
source_meaning: 上线审批工作流状态（PENDING/RUNNING/FINISHED/TERMINATED；DB 另有 REVOKED）
```

---END FILE---

---FILE: rules/project-type-drives-flow-and-ams.md ---
---
type: rule
title: 上线审批项目类型决定流程与 AMS 推送
page_key: rule/project-type-drives-flow-and-ams
domain: 微企链立项与项目审批
status: draft
aliases:
  - STANDARD/REGULAR 决定 flow_code
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

上线审批表的 `project_type` 有两个受其影响的后果：一是决定 `wf_procdef_key`（走哪套工作流定义），二是决定是否推送 AMS。因此它不是纯展示字段，改值会直接改变流程走向与外部系统联动。

该列与立项申请表的同名列语义不同，见 [[concepts/project-type-domain-split]]；字段语义见 [[tables/tenant_project_approval]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 上线审批项目类型决定流程与 AMS 推送
subject: tenant_project_approval.project_type
evidence: code
source_meaning: 上线审批项目类型：STANDARD(标准项目)/REGULAR(常规项目)，决定 flow_code 与是否推送 AMS
```

---END FILE---

---FILE: rules/is-low-risk-writeback.md ---
---
type: rule
title: 低风险标记由法务节点填写并回写
page_key: rule/is-low-risk-writeback
domain: 微企链立项与项目审批
status: draft
aliases:
  - is_low_risk 回写
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
---

`is_low_risk` 不是发起时填写的字段，而是在法务经办节点上产生，并回写到主表供 AMS 推送判定使用。也就是说该值存在「填写前未知」的中间态，AMS 推送逻辑必须能容忍它尚未确定的情况。

字段语义见 [[tables/tenant_project_approval]]，与项目类型共同影响 AMS 的规则见 [[rules/project-type-drives-flow-and-ams]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 低风险标记由法务节点填写并回写
subject: tenant_project_approval.is_low_risk
evidence: code
source_meaning: 法务经办节点填写的『是否低风险』，回写主表供 AMS 推送判定
```

---END FILE---

---FILE: rules/statistics-only-editable-field.md ---
---
type: rule
title: 统计页唯一可编辑列
page_key: rule/statistics-only-editable-field
domain: 微企链立项与项目审批
status: draft
aliases:
  - EDITABLE_FIELDS
  - custom_field_statistics_one
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

项目统计页面上只有一列是可编辑的：`custom_field_statistics_one`（自定义字段一(统计用)）。其余列一律只读展示，包括与它名字相近的 `custom_field_one`——后者是企微导入路径维护的字段，不是统计页字段。

这种「同名兄弟字段分属不同写入路径」的设计是本表最容易误改的地方，字段对照见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 统计页唯一可编辑列
subject: wechat_project_approval_apply.custom_field_statistics_one
evidence: code
source_meaning: 自定义字段一(统计用)；统计页唯一可编辑列（EDITABLE_FIELDS）
```

---END FILE---

---FILE: rules/sp-type-fintech-scope.md ---
---
type: rule
title: 统计口径固定金融科技业务
page_key: rule/sp-type-fintech-scope
domain: 微企链立项与项目审批
status: draft
aliases:
  - sp_type 固定取值
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

项目统计的取数范围被固定为业务类型等于「金融科技业务」，即 `sp_type='金融科技业务'`。该条件不由前端控制，属于统计口径的一部分。

因此统计页显示的项目数与导出范围（见 [[calibers/wechat-approval-export-scope]]）并不等价：两者过滤的是不同维度。字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 统计口径固定金融科技业务
subject: wechat_project_approval_apply.sp_type
evidence: code
source_meaning: 业务类型；统计口径固定 sp_type='金融科技业务'
```

---END FILE---

---FILE: rules/import-length-limits.md ---
---
type: rule
title: 文本字段长度上限
page_key: rule/import-length-limits
domain: 微企链立项与项目审批
status: draft
aliases:
  - 备注长度限制
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:WechatProjectApprovalApplication.java
contract_version: "0.1"
---

同一列在不同导入路径下的长度上限并不相同：`comment`（备注）企微导入上限 200 字、项目立项统计导入上限 500 字；`custom_field_one` 长度校验 500；`project_exception_remark` 统计导入 ≤500 字。

这意味着「同一条备注为什么在另一条路径上被拒」是预期行为，排查时应先确认走的是哪条导入链路。字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 文本字段长度上限
subject: wechat_project_approval_apply.comment
evidence: code
source_meaning: 备注；企微导入上限 200 字，项目立项统计导入上限 500 字
```

---END FILE---

---FILE: rules/product-type-arr-like-filter.md ---
---
type: rule
title: 产品类型编码数组的 LIKE 筛选与白名单校验
page_key: rule/product-type-arr-like-filter
domain: 微企链立项与项目审批
status: draft
aliases:
  - product_type_arr LIKE 筛选
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

由于产品类型以 JSON 数组字符串存放，筛选无法用等值匹配，只能用 `LIKE '%"code"%'` 在数组文本里找编码。为避免注入与脏值，拼接前会先经过枚举白名单校验。

运维上要注意两点：该匹配是子串匹配，编码之间存在包含关系时可能误命中；白名单外的编码无法被筛出。字段的双表示见 [[concepts/product-type-coding]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 产品类型编码数组的 LIKE 筛选与白名单校验
subject: wechat_project_approval_apply.product_type_arr
evidence: code
source_meaning: 产品类型编码 JSON 数组，筛选用 LIKE '%"code"%'（先经枚举白名单校验）
```

---END FILE---

---FILE: rules/export-system-delivery-overwrite.md ---
---
type: rule
title: 导出时 system_delivery 被产品类型覆盖
page_key: rule/export-system-delivery-overwrite
domain: 微企链立项与项目审批
status: draft
aliases:
  - 导出覆盖交付方式列
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
---

在导出流程中，`system_delivery` 这一列会被 `product_type_arr` 翻译出的中文覆盖写入。也就是说导出文件里这一列的内容并非库内该列的原值，而是产品类型的中文。

这条规则与统计页把该列当交付范围过滤的用法直接冲突，是全主题最容易误读的一处，概念层面的说明见 [[concepts/system-delivery-reuse]]、[[concepts/product-type-coding]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该覆盖行为属历史遗留复用，本次无文档主张可佐证其引入时间。

```ground:rule
rule: 导出时 system_delivery 被产品类型覆盖
subject: wechat_project_approval_apply.system_delivery
evidence: code
source_meaning: DB 注释为『系统交付方式』，但统计页用它做交付范围过滤（SaaS/Saas+本地化），导出时该列又被 product_type_arr 的中文覆盖写入，属被复用列
```

---END FILE---

---FILE: rules/phase-auto-operation-on-first-settlement.md ---
---
type: rule
title: 首笔落地时间首次写入联动项目阶段
page_key: rule/phase-auto-operation-on-first-settlement
domain: 微企链立项与项目审批
status: draft
aliases:
  - 持续运营自动置位
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java#applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
contract_version: "0.1"
---

当企微审批已通过（`act_procinst_status='2'`）、`first_settlement_time` 由空变非空、且当前阶段不是持续运营时，系统自动把项目阶段置为持续运营。三个条件缺一不可：审批未通过的记录即使填了首笔落地时间也不会推进阶段。

注意该字段 DB 注释写的是「首笔放款时间」，与业务口径「首笔落地时间」措辞不同。完整状态流转见 [[processes/project-phase]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 首笔落地时间首次写入联动项目阶段
subject: wechat_project_approval_apply.first_settlement_time
evidence: code
source_meaning: 首笔落地时间（DB 注释写『首笔放款时间』）；审批通过后由空变非空会联动项目阶段置为持续运营
```

---END FILE---

---FILE: rules/legacy-termination-normalize.md ---
---
type: rule
title: TERMINATION 读时归一为挂起
page_key: rule/legacy-termination-normalize
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目阶段历史值归一
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java#normalizeLegacyProjectPhaseCode
contract_version: "0.1"
---

项目阶段的历史值 `TERMINATION` 不会被改库，而是在读取时被归一为「挂起」。因此库内与界面上的取值可能不一致，写筛选条件时若按 `TERMINATION` 直接查库、按挂起查界面，会得到不同结果。

字段语义见 [[tables/wechat_project_approval_apply]]，完整状态集见 [[processes/project-phase]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该归一化本身即为历史值收敛措施，说明 `TERMINATION` 属旧状态命名。

```ground:rule
rule: TERMINATION 读时归一为挂起
subject: wechat_project_approval_apply.project_phase
evidence: code
source_meaning: 项目阶段：IMPLEMENTATION(实施阶段)/持续运营/挂起；TERMINATION 为历史值读时归一为挂起；『立项阶段』仅用于展示与导入校验、不落库
```

---END FILE---

---FILE: rules/project-phase-import-restriction.md ---
---
type: rule
title: 立项阶段不落库且审批通过后不可导入
page_key: rule/project-phase-import-restriction
domain: 微企链立项与项目审批
status: draft
aliases:
  - 立项阶段导入校验
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

「立项阶段」不是库内状态，它只用于展示与导入校验，落库时会被忽略；并且当企微审批已通过后，导入不允许再写「立项阶段」。也就是说导入模板接受的取值范围与库内实际存储的项目阶段并不是同一个集合。

这一点直接决定了导入校验报错与库内取值对不上时应当以库内为准，见 [[processes/project-phase]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 立项阶段不落库且审批通过后不可导入
subject: wechat_project_approval_apply.project_phase
evidence: code
source_meaning: 项目阶段：IMPLEMENTATION(实施阶段)/持续运营/挂起；TERMINATION 为历史值读时归一为挂起；『立项阶段』仅用于展示与导入校验、不落库
```

---END FILE---

---FILE: rules/op-contact-group-refresh.md ---
---
type: rule
title: 对接人组别随 operation_id 反查刷新
page_key: rule/op-contact-group-refresh
domain: 微企链立项与项目审批
status: draft
aliases:
  - op_contact_group 联动
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

运营/档案/风控三组对接人列各配一个组别列，组别不是独立录入的，而是随对应对接人的 `operation_id` 反查刷新得到。因此组别列是派生数据：只要 contact 改了而 group 没跟着刷新，两者就会不一致。

排查「组别和对接人对不上」时，首先要确认是否存在绕过刷新逻辑的写入路径。标识体系说明见 [[concepts/operation-id-contact-reference]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 对接人组别随 operation_id 反查刷新
subject: wechat_project_approval_apply.op_contact_group
evidence: code
source_meaning: 运营组别，随 op_contact 的 operation_id 反查刷新
```

---END FILE---

---FILE: rules/statics-op-display-override.md ---
---
type: rule
title: 展示用统计操作时间覆盖更新时间
page_key: rule/statics-op-display-override
domain: 微企链立项与项目审批
status: draft
aliases:
  - statics_op_time 展示覆盖
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

列表与详情展示的「更新时间/更新人」并非直接取 `update_time` / `update_user`，而是被 `statics_op_time` / `statics_op_user`（项目统计更新时间与更新用户）覆盖。因此界面上的更新时间反映的是统计操作，而不是记录行级变更。

阅读审计信息时须注意这一层覆盖，字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 展示用统计操作时间覆盖更新时间
subject: wechat_project_approval_apply.statics_op_time
evidence: code
source_meaning: 项目统计更新时间；列表/详情展示时覆盖 update_time
```

---END FILE---

---REVIEW: caliber | 上线审批在途校验---
语义分析中该口径的 `predicate` 在 `tenant_project_approval.wf_status IN ('PENDING','RUNNING') AND t` 处被截断，且 `scope` 与 `evidence` 两个字段完全缺失。由于锚点字段值必须逐字来自语义分析、禁止补全发明，本口径暂不产出 caliber 页；待补全 predicate 全文与 evidence 后再落页。
---END REVIEW---

---REVIEW: table | 物理库名缺失---
本次语义分析给出了表名与字段级证据，但未给出任何物理库名（schema/database）。所有 table/process/caliber/rule 页面的 `scope.databases` 因此填写占位值「未在语义分析中给出物理库名」，待补充后统一回填。
---END REVIEW---

---REVIEW: table | tenant_project_approval_flow 与 tenant_project 缺字段级证据---
`processes/project-approval-node-status` 引用的 `tenant_project_approval_flow.node_status`、以及 `processes/tenant-project-status` 引用的 `tenant_project.project_status` 只有状态枚举与代码路径证据，没有字段级 field_semantics。因此本次未为这两张表产出 table 页，仅在对应 process 页按状态机登记；其中 `tenant_project` 的表名字面在 DB 实测中也未出现，其状态机按 DO `TenantProjectDO`/系统文档标注。
---END REVIEW---

---REVIEW: 字段语义 | act_procinst_status 的 1/3/4 无代码标签---
`wechat_project_approval_apply.act_procinst_status` 的 `'1'`/`'3'`/`'4'` 仅出现在 DB 分布中，本层代码未声明其含义（代码只用字面 `'2'`＝审批通过）。这些取值的业务标签属待确认语义，不应据 DB 分布反推。
---END REVIEW---

---REVIEW: enum | project_phase 常量字面值缺失---
`PROJECT_PHASE_OPERATION`（持续运营）与 `PROJECT_PHASE_HANG`（挂起）在本层只给出常量名，未给出字面值；`wechat_project_approval_flow_file.catg_id` 的 `FBP_OA_ATTACHMENT`/`FBP_OA_COMMENT_FILE` 也超出代码基线枚举覆盖范围。三处均需补枚举全集后再收敛。
---END REVIEW---

---REVIEW: 规则 | invalidateHistoricalProjectOnSubmit 无调用点---
`ProjectApprovalApplication.java#invalidateHistoricalProjectOnSubmit` 在当前给出的代码切片内未见调用点，租户项目「失效」路径的实际触发时机待核实；本主题内 [[processes/tenant-project-status]] 仅按可见证据登记该transition，不作调用链断言。
---END REVIEW---