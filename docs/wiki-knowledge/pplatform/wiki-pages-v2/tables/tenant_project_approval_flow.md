---
type: table
title: 租户项目审批流程表
page_key: tenant_project_approval_flow
domain: 微企链立项与项目审批
status: draft
anchors: [tenant_project_approval_flow]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












上线审批的流程实例表，承接工作流运行期的流程级状态，是 [[tenant_project_approval]] 主记录与 [[tenant_project_approval_flow_node]] 节点记录之间的中间层。

```ground:table
table: tenant_project_approval_flow
database: lowcode_pplatform
desc: 租户项目审批流程表
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
  - name: is_operate
    type: string
    phys: varchar(64)
    desc: 是否可编辑
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_optional
    type: string
    phys: varchar(64)
    desc: 是否可选节点：Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: node_status
    type: string
    phys: varchar(64)
    desc: 节点状态
    dict: node_status
    topk: "APPROVED|APPROVING|PENDING|REJECTED"
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
    topk: "base|boscxsbl|boscxyc|sdhsg"
  - name: approver_user_id
    type: string
    phys: varchar(1024)
    desc: 审批人 userId
  - name: approver_user_name
    type: string
    phys: varchar(1024)
    desc: 审批人姓名
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
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
    topk: "ISOLATE_TAG_boscxsbl|ISOLATE_TAG_boscxyc|ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2|beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|spsi.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: node_code
    type: string
    phys: varchar(64)
    desc: 节点编码
    topk: "BUSINESS_MANAGER|LEGAL_PROCESS|LEGAL_REVIEW|OPERATION|PROJECT_CONFIG|PROJECT_MANAGER"
  - name: node_name
    type: string
    phys: varchar(64)
    desc: 节点名称（中文）
  - name: node_order
    type: number
    phys: int(10)
    desc: 节点顺序，从 1 开始
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_tenant_project_approval_flow_tenant_project_approval
    type: string
    phys: varchar(128)
    desc: 关联项目审批
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
```

## 关联表

- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow.code → tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow.node_code → tenant_project_approval_flow_node.node_code（java-eq-same:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval]]：tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval → tenant_project_approval.code（ref-convention:TenantProjectApprovalFlowDO.java，suggested）
- [[tenant_project_approval]]：tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval → tenant_project_approval.id（db-index:ref_-naming，suggested）
## 需求背景

流程级状态随审批人操作（同意、退回、驳回、转审）推进，状态机见 [[processes/tenant_project_approval_flow_node_status]]。业务系统推送项目配置时，需要定位到「正在审批的节点」才落库，口径见 [[calibers/approving_flow_node]]，规则见 [[rules/business_config_push_node_check]]。表内另有 `enable` 等启停列参与口径过滤。

## 版本演进

当前语义分析未提供该表状态取值的历史变更记录。
