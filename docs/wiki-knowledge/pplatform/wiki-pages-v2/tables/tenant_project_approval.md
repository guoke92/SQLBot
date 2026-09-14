---
type: table
title: 租户项目审批表
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
contract_version: "0.1"
belong: tables
---












`tenant_project_approval` 承载项目正式上线的审批工作流状态（`wf_status`），是 [[project_approval_wf_status]] 状态机的落库表，审批通过的终态会驱动 [[tenant_project]] 的 `project_status` 流转。当前语义分析仅覆盖 `wf_status` 字段，其余字段未提供。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目上线必须先发起审批，正式发起前可暂存（PENDING 保持），审批完成/终止分别落到 FINISHED/TERMINATED。

## 版本演进
语义分析未记录该表的版本演进。

```ground:table
table: tenant_project_approval
database: lowcode_pplatform
desc: 租户项目审批表
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: is_add
    type: string
    phys: varchar(64)
    desc: 是否新增项目；Y=是，N=否
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_latest
    type: string
    phys: varchar(64)
    desc: 是否最新审批
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_low_risk
    type: string
    phys: varchar(64)
    desc: 是否低风险项目:Y,N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_online_approval
    type: string
    phys: varchar(64)
    desc: 是否发起上线审批：Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: project_type
    type: string
    phys: varchar(64)
    desc: 项目类型：STANDARD（标准） / REGULAR（常规）
    dict: project_type
    topk: "REGULAR|STANDARD"
  - name: simple_mode
    type: string
    phys: varchar(64)
    desc: 是否为简易模式项目/常规非低风险项目，Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: wf_status
    type: string
    phys: varchar(64)
    desc: 工作流状态
    dict: wf_status
    topk: "FINISHED|PENDING|REVOKED|RUNNING|TERMINATED"
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "GREENTOWNAT|base|boscxsbl|boscxyc|sdhsg"
  - name: approval_no
    type: string
    phys: varchar(64)
    desc: 审批编号，格式：SX+yyyymmdd+xxx
  - name: capital_names
    type: string
    phys: varchar(1000)
    desc: 资金方名称(JSON格式字符串，含order字段标记顺序)
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: complete_time
    type: temporal
    phys: datetime
    desc: 完成时间
  - name: core_enterprise_names
    type: string
    phys: varchar(1000)
    desc: 核心企业名称(JSON格式字符串，含order字段标记顺序)
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "ISOLATE_TAG_GREENTOWNAT|ISOLATE_TAG_boscxsbl|ISOLATE_TAG_boscxyc|ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2|beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|spsi.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
  - name: flow_code
    type: string
    phys: varchar(64)
    desc: 流程配置编码（tenant_project_approval_flow_config#flow_code）
  - name: initiate_time
    type: temporal
    phys: datetime
    desc: 发起时间
  - name: initiator_user_id
    type: string
    phys: varchar(64)
    desc: 发起人 userId
  - name: initiator_user_name
    type: string
    phys: varchar(64)
    desc: 发起人姓名
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_plan
    type: string
    phys: varchar(10240)
    desc: 项目方案描述
  - name: ref_tenant_project_approval_tenant_project
    type: string
    phys: varchar(128)
    desc: 关联租户项目
  - name: ref_tenant_project_approval_tenant_project_approval
    type: string
    phys: varchar(128)
    desc: 关联原审批数据
  - name: ref_tenant_project_approval_tenant_project_approval_flow_config
    type: string
    phys: varchar(128)
    desc: 关联租户项目流程配置
  - name: related_approval_no
    type: string
    phys: varchar(64)
    desc: 关联审批编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: solution_manager_id
    type: string
    phys: varchar(1024)
    desc: 方案经理 userId
  - name: solution_manager_name
    type: string
    phys: varchar(1024)
    desc: 方案经理姓名
  - name: sp_no
    type: string
    phys: varchar(64)
    desc: 立项审批编号（wechat_project_approval_apply#sp_no）
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: wf_last_operate_time
    type: temporal
    phys: datetime
    desc: 工作流最近操作时间
  - name: wf_last_operator
    type: string
    phys: varchar(64)
    desc: 工作流最近操作人
  - name: wf_last_operator_id
    type: string
    phys: varchar(64)
    desc: 工作流最近操作人ID
  - name: wf_procdef_key
    type: string
    phys: varchar(64)
    desc: 工作流流程定义key
  - name: whitelist_query_result
    type: string
    phys: varchar(2048)
    desc: 白名单查询结果(JSON，提交后锁定)
```

## 关联表

- [[tenant_project_approval_business_info]]：tenant_project_approval.code → tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow_config]]：tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config → tenant_project_approval_flow_config.code（ref-convention:TenantProjectApprovalDO.java，suggested）
- [[tenant_project_approval_flow_config]]：tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config → tenant_project_approval_flow_config.id（db-index:ref_-naming，suggested）
- [[tenant_project_approval_flow_credit]]：tenant_project_approval.code → tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow_node]]：tenant_project_approval.code → tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval（java-eq:ProjectApprovalDeskApplication.java，suggested）
- [[tenant_project_approval_flow]]：tenant_project_approval.code → tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval（ref-convention:TenantProjectApprovalFlowDO.java，suggested）
- [[tenant_project]]：tenant_project_approval.id → tenant_project.project_approval_id（write-flow:ProjectApprovalApplication.java，confirmed）
- [[tenant_project]]：tenant_project_approval.ref_tenant_project_approval_tenant_project → tenant_project.code（ref-convention:TenantProjectApprovalDO.java，suggested）
- [[tenant_project]]：tenant_project_approval.ref_tenant_project_approval_tenant_project → tenant_project.id（db-index:ref_-naming，suggested）
