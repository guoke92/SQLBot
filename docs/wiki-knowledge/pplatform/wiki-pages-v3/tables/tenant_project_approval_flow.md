---
type: table
title: 上线审批节点
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
contract_version: "0.3"
belong: tables
scenes: [project_online_approval]
---

# 上线审批节点

节点状态 [[node_status]]。PENDING 在本列是「待审批」。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[project_online_approval]]

`id`, `enable`, `create_time`, `update_time`, `node_status`

### 未分窗

仍留表页，待代码证据划入场景：`is_operate`, `is_optional`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `approver_user_id`, `approver_user_name`, `db_tenant_code`, `name`, `node_code`, `node_name`, `node_order`, `organization_id`, `ref_tenant_project_approval_flow_tenant_project_approval`, `remark`

```ground:table
table: tenant_project_approval_flow
database: lowcode_pplatform
desc: 租户项目审批流程表
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
  - name: is_operate
    type: string
    phys: varchar(64)
    desc: "是否可编辑"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_optional
    type: string
    phys: varchar(64)
    desc: "是否可选节点：Y/N"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: node_status
    type: string
    phys: varchar(64)
    desc: "节点状态"
    dict: node_status
    topk: "APPROVED|APPROVING|PENDING|REJECTED"
    labels: "APPROVED:已通过|APPROVING:审批中|PENDING:待审批|REJECTED:已拒绝"
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
    topk: "base|boscxsbl|boscxyc|sdhsg"
  - name: approver_user_id
    type: string
    phys: varchar(1024)
    desc: "审批人 userId"
  - name: approver_user_name
    type: string
    phys: varchar(1024)
    desc: "审批人姓名"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "ISOLATE_TAG_boscxsbl|ISOLATE_TAG_boscxyc|ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2|beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|spsi.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: node_code
    type: string
    phys: varchar(64)
    desc: "节点编码"
    topk: "BUSINESS_MANAGER|LEGAL_PROCESS|LEGAL_REVIEW|OPERATION|PROJECT_CONFIG|PROJECT_MANAGER"
  - name: node_name
    type: string
    phys: varchar(64)
    desc: "节点名称（中文）"
  - name: node_order
    type: number
    phys: int(10)
    desc: "节点顺序，从 1 开始"
    labels: "1:开始"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: ref_tenant_project_approval_flow_tenant_project_approval
    type: string
    phys: varchar(128)
    desc: "关联项目审批"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```
