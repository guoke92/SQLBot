---
type: table
title: 租户项目审批表
page_key: tenant_project_approval
belong: tables
status: draft
anchors:
- tenant_project_approval
sources:
- database_schema:lowcode_pplatform.tenant_project_approval
- code_path:ProjectApprovalApplication.java:254
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_project
- tenant_project_approval_business_info
- tenant_project_approval_flow
- tenant_project_approval_flow_comment
- tenant_project_approval_flow_config
- tenant_project_approval_flow_credit
- tenant_project_approval_flow_file
- tenant_project_approval_flow_node
- wechat_project_approval_apply
- tenant_project_approval__is_online_approval
- tenant_project_approval__project_type
- tenant_project_approval__simple_mode
- tenant_project_approval__wf_status
- tenant_project_approval__is_low_risk
- tenant_project_approval__is_latest
- tenant_project_approval__enable
- tenant_project_approval__is_add
---
# 租户项目审批表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval
database: lowcode_pplatform
desc: 租户项目审批表
inactive: false
primary_key:
- id
grain: 项目上线审批单；列表最新一笔 is_latest=Y；在途仍受 assertNoApproval 约束
name_anchors:
- solution_manager_name
- initiator_user_name
- code
- name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: approval_no
  type: string
  desc: 审批编号，格式：SX+yyyymmdd+xxx
- name: is_online_approval
  type: string
  desc: 是否发起上线审批：Y/N
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: related_approval_no
  type: string
  desc: 关联审批编号
- name: sp_no
  type: string
  desc: 立项审批编号（wechat_project_approval_apply#sp_no）
- name: solution_manager_id
  type: string
  desc: 方案经理 userId
- name: solution_manager_name
  type: string
  desc: 方案经理姓名
- name: project_type
  type: string
  desc: 项目类型：STANDARD（标准） / REGULAR（常规）
  dict:
  - STANDARD
  - REGULAR
  label:
  - 标准项目
  - 常规项目
- name: simple_mode
  type: string
  desc: 是否为简易模式项目/常规非低风险项目，Y/N
  dict:
  - N
  - Y
  label:
    N: 否
    Y: 是
- name: project_plan
  type: string
  desc: 项目方案描述
- name: initiator_user_id
  type: string
  desc: 发起人 userId
- name: initiator_user_name
  type: string
  desc: 发起人姓名
- name: initiate_time
  type: temporal
  desc: 发起时间
  written_with:
  - wf_status
  - act_procinst_id
- name: wf_procdef_key
  type: string
  desc: 工作流流程定义key
- name: wf_status
  type: string
  desc: 工作流状态
  dict:
  - RUNNING
  - FINISHED
  - TERMINATED
  - PENDING
  - REVOKED
  label:
  - 审批中
  - 审批通过
  - 审批拒绝
  - 待发起
  - 审批撤销
  written_with:
  - initiate_time
  - act_procinst_id
  - complete_time
- name: wf_last_operator_id
  type: string
  desc: 工作流最近操作人ID
- name: wf_last_operator
  type: string
  desc: 工作流最近操作人
- name: wf_last_operate_time
  type: temporal
  desc: 工作流最近操作时间
- name: is_low_risk
  type: string
  desc: 是否低风险项目:Y,N
  dict:
  - Y
  - N
  label:
  - 是否低风险项目
  - 否
- name: flow_code
  type: string
  desc: 流程配置编码（tenant_project_approval_flow_config#flow_code）
- name: is_latest
  type: string
  desc: 是否最新审批
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: core_enterprise_names
  type: string
  desc: 核心企业名称(JSON格式字符串，含order字段标记顺序)
- name: capital_names
  type: string
  desc: 资金方名称(JSON格式字符串，含order字段标记顺序)
- name: whitelist_query_result
  type: string
  desc: 白名单查询结果(JSON，提交后锁定)
- name: ref_tenant_project_approval_tenant_project
  type: string
  desc: 关联租户项目
- name: ref_tenant_project_approval_tenant_project_approval_flow_config
  type: string
  desc: 关联租户项目流程配置
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
  written_with:
  - wf_status
  - initiate_time
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: ref_tenant_project_approval_tenant_project_approval
  type: string
  desc: 关联原审批数据
- name: complete_time
  type: temporal
  desc: 完成时间
  written_with:
  - wf_status
- name: is_add
  type: string
  desc: 是否新增项目；Y=是，N=否
  dict:
  - Y
  - N
  label:
    Y: 是
    N: 否
default_filter:
  predicate: tenant_project_approval.enable = 'Y'
  trust: confirmed
  evidence: code_path:ProjectApprovalApplication.java:254
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project.code
right: tenant_project_approval.ref_tenant_project_approval_tenant_project
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:253
source: l1_code
join_role: identity
priority: primary
authenticity_note: 审批按项目 code 关联，不是 tenant_project.id。最新一笔再加 is_latest=Y。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.id
right: tenant_project.project_approval_id
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:405
source: l1_code
join_role: identity
priority: secondary
name_evidence:
  match: family_suffix
  stem: project_approval
  comment: 项目线上审批ID
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 创建审批后回写项目上的审批主键。主查询走 code=ref。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1003
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_business_info_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 102
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 业务推送信息按审批 code。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:571
source: l1_code
join_role: identity
priority: primary
authenticity_note: 流程节点按审批单 code，不是审批 id。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_comment.ref_tenant_project_approval_flow_comment_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1730
source: l1_code
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_comment_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 22
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 备注 ref 存 approval.getCode()。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1551
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_credit_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 141
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 授信按审批 code。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1753
source: l1_code
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_file_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 112
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 文件 ref 存 approval.getCode()。
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ProjectOnlineProcessOperateListener.java:355
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_flow_node_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 127
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 节点操作留痕按审批 code。
```

```ground:relation
type: EQUI_JOIN
left: wechat_project_approval_apply.sp_no
right: tenant_project_approval.sp_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
source: comment_fk
join_role: business_code
priority: primary
name_evidence:
  match: comment_fk
  stem: wechat_project_approval_apply
  comment: 立项审批编号（wechat_project_approval_apply#sp_no）
evidence: database_schema:tenant_project_approval.sp_no#comment_fk:wechat_project_approval_apply#sp_no
authenticity_note: live_validate:fk_like; approval.sp_no ⊆ wechat.apply.sp_no (R→L=1.0);
  comment_fk + UAT 2026-09-23
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_config.flow_code
right: tenant_project_approval.flow_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
source: comment_fk
join_role: business_code
priority: primary
name_evidence:
  match: comment_fk
  stem: tenant_project_approval_flow_config
  comment: 流程配置编码（tenant_project_approval_flow_config#flow_code）
evidence: database_schema:tenant_project_approval.flow_code#comment_fk:tenant_project_approval_flow_config#flow_code
authenticity_note: comment_fk 保留；UAT empty_endpoint (tenant_project_approval.flow_code
  全 NULL)。 配置侧有 NO_ONLINE/STANDARD/REGULAR；有数据后再升 confirmed。
```
```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_config.code
right: tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: full_sweep:code_ref UAT empty
source: full_sweep
join_role: business_code
priority: secondary
authenticity_note: code:ref-convention
```
```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval.ref_tenant_project_approval_tenant_project_approval
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live_fk_like self_ref R→L=1
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 原审批自引用
```

## 页面链接

### 关联表

- [[tables/tenant_project]]
- [[tables/tenant_project_approval_business_info]]
- [[tables/tenant_project_approval_flow]]
- [[tables/tenant_project_approval_flow_comment]]
- [[tables/tenant_project_approval_flow_config]]
- [[tables/tenant_project_approval_flow_credit]]
- [[tables/tenant_project_approval_flow_file]]
- [[tables/tenant_project_approval_flow_node]]
- [[tables/wechat_project_approval_apply]]

### 概念

- [[concepts/approval_whitelist]]
- [[concepts/online_approval_wf]]
- [[concepts/project_status_vs_approval]]
- [[concepts/tenant_project_code_join]]
- [[concepts/wechat_apply_term]]

### 字典

- [[dicts/tenant_project_approval__is_online_approval]]（`tenant_project_approval.is_online_approval`）
- [[dicts/tenant_project_approval__project_type]]（`tenant_project_approval.project_type`）
- [[dicts/tenant_project_approval__simple_mode]]（`tenant_project_approval.simple_mode`）
- [[dicts/tenant_project_approval__wf_status]]（`tenant_project_approval.wf_status`）
- [[dicts/tenant_project_approval__is_low_risk]]（`tenant_project_approval.is_low_risk`）
- [[dicts/tenant_project_approval__is_latest]]（`tenant_project_approval.is_latest`）
- [[dicts/tenant_project_approval__enable]]（`tenant_project_approval.enable`）
- [[dicts/tenant_project_approval__is_add]]（`tenant_project_approval.is_add`）
