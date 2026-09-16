---
type: table
title: 项目上线审批单
page_key: tenant_project_approval
domain: 微企链立项与项目审批
status: draft
anchors: [tenant_project_approval]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [project_online_approval]
---

# 项目上线审批单

上线审批主档。`wf_status` 见 [[wf_status]]。通过后 `tenantProjectApplication.effective()`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[project_online_approval]]

`id`, `enable`, `create_time`, `update_time`, `approval_no`, `flow_code`, `is_add`, `is_latest`, `sp_no`, `wf_status`

### 未分窗

仍留表页，待代码证据划入场景：`is_low_risk`, `is_online_approval`, `simple_mode`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `capital_names`, `complete_time`, `core_enterprise_names`, `db_tenant_code`, `initiate_time`, `initiator_user_id`, `initiator_user_name`, `name`, `organization_id`, `project_plan`, `project_type`, `ref_tenant_project_approval_tenant_project`, `ref_tenant_project_approval_tenant_project_approval`, `ref_tenant_project_approval_tenant_project_approval_flow_config`, `related_approval_no`, `remark`, `solution_manager_id`, `solution_manager_name`, `wf_last_operate_time`, `wf_last_operator`, `wf_last_operator_id`, `wf_procdef_key`, `whitelist_query_result`

```ground:table
table: tenant_project_approval
database: lowcode_pplatform
desc: 租户项目审批表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [project_online_approval]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    group: always
    scenes: [project_online_approval]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [project_online_approval]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [project_online_approval]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: approval_no
    type: string
    phys: varchar(64)
    desc: "审批编号"
    roles: [query]
    scenes: [project_online_approval]
  - name: flow_code
    type: string
    phys: varchar(64)
    desc: "流程编码"
    scenes: [project_online_approval]
  - name: is_add
    type: string
    phys: varchar(64)
    desc: "是否新增"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [project_online_approval]
  - name: is_latest
    type: string
    phys: varchar(64)
    desc: "是否最新"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [project_online_approval]
  - name: is_low_risk
    type: string
    phys: varchar(64)
    desc: "是否低风险项目:Y,N"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_online_approval
    type: string
    phys: varchar(64)
    desc: "是否发起上线审批：Y/N"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: simple_mode
    type: string
    phys: varchar(64)
    desc: "是否为简易模式项目/常规非低风险项目，Y/N"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: sp_no
    type: string
    phys: varchar(64)
    desc: "企微审批号"
    scenes: [project_online_approval]
  - name: wf_status
    type: string
    phys: varchar(64)
    desc: "工作流状态"
    dict: wf_status
    topk: "FINISHED|PENDING|REVOKED|RUNNING|TERMINATED"
    labels: "FINISHED:审批通过|PENDING:待发起|RUNNING:审批中|TERMINATED:审批拒绝"
    roles: [query]
    scenes: [project_online_approval]
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "GREENTOWNAT|base|boscxsbl|boscxyc|sdhsg"
  - name: capital_names
    type: string
    phys: varchar(1000)
    desc: "资金方名称(JSON格式字符串，含order字段标记顺序)"
  - name: complete_time
    type: temporal
    phys: datetime
    desc: "完成时间"
  - name: core_enterprise_names
    type: string
    phys: varchar(1000)
    desc: "核心企业名称(JSON格式字符串，含order字段标记顺序)"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "ISOLATE_TAG_GREENTOWNAT|ISOLATE_TAG_boscxsbl|ISOLATE_TAG_boscxyc|ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2|beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|spsi.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
  - name: initiate_time
    type: temporal
    phys: datetime
    desc: "发起时间"
  - name: initiator_user_id
    type: string
    phys: varchar(64)
    desc: "发起人 userId"
  - name: initiator_user_name
    type: string
    phys: varchar(64)
    desc: "发起人姓名"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: project_plan
    type: string
    phys: varchar(10240)
    desc: "项目方案描述"
  - name: project_type
    type: string
    phys: varchar(64)
    desc: "项目类型：STANDARD（标准） / REGULAR（常规）"
    topk: "REGULAR|STANDARD"
  - name: ref_tenant_project_approval_tenant_project
    type: string
    phys: varchar(128)
    desc: "关联租户项目"
  - name: ref_tenant_project_approval_tenant_project_approval
    type: string
    phys: varchar(128)
    desc: "关联原审批数据"
  - name: ref_tenant_project_approval_tenant_project_approval_flow_config
    type: string
    phys: varchar(128)
    desc: "关联租户项目流程配置"
  - name: related_approval_no
    type: string
    phys: varchar(64)
    desc: "关联审批编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: solution_manager_id
    type: string
    phys: varchar(1024)
    desc: "方案经理 userId"
  - name: solution_manager_name
    type: string
    phys: varchar(1024)
    desc: "方案经理姓名"
  - name: wf_last_operate_time
    type: temporal
    phys: datetime
    desc: "工作流最近操作时间"
  - name: wf_last_operator
    type: string
    phys: varchar(64)
    desc: "工作流最近操作人"
  - name: wf_last_operator_id
    type: string
    phys: varchar(64)
    desc: "工作流最近操作人ID"
  - name: wf_procdef_key
    type: string
    phys: varchar(64)
    desc: "工作流流程定义key"
  - name: whitelist_query_result
    type: string
    phys: varchar(2048)
    desc: "白名单查询结果(JSON，提交后锁定)"
```

```ground:relation
type: EQUI_JOIN
left: tenant_project.project_approval_id
right: tenant_project_approval.id
cardinality: many_to_one
status: proposed
evidence: code_path:ProjectApprovalApplication.java
```
