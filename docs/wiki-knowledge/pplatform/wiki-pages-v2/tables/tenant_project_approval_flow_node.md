---
type: table
title: 租户项目审批流程节点表
page_key: tenant_project_approval_flow_node
domain: 微企链立项与项目审批
status: draft
anchors: [tenant_project_approval_flow_node]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












上线审批流程的节点级记录表，一行代表某个流程中一个审批节点的操作与状态，是审批意见、节点类型与后补协议标记的落点。

```ground:table
table: tenant_project_approval_flow_node
database: lowcode_pplatform
desc: 租户项目审批流程节点表
fields:
  - name: approval_type
    type: string
    phys: varchar(64)
    desc: 审批类型
    dict: approval_type
    topk: "BACK_AGREEMENT|ONLINE_APPROVAL"
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
  - name: is_back_agreement
    type: string
    phys: varchar(64)
    desc: 是否后补合作协议
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_low_risk
    type: string
    phys: varchar(64)
    desc: 是否低风险项目
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: operate_type
    type: string
    phys: varchar(64)
    desc: 操作类型
    dict: operate_type
    topk: "back|delegate|pass|reject|revoke"
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
    topk: "base|sdhsg"
  - name: approve_comment
    type: string
    phys: varchar(256)
    desc: 审批意见
  - name: cc_user_id
    type: string
    phys: varchar(500)
    desc: 抄送相关人员userId列表(JSON数组)
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
    topk: "ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2|beehive-scf.qhhrly.cn|ning|sdhsg.beehive-scf.qhhrly.cn|spsi.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: node_code
    type: string
    phys: varchar(64)
    desc: 节点编码
    topk: "BUSINESS_MANAGER|LEGAL_PROCESS|LEGAL_REVIEW|OPERATION|PROJECT_CONFIG|PROJECT_MANAGER"
  - name: node_order
    type: number
    phys: int(10)
    desc: 审批顺序，从1开始
  - name: operate_time
    type: temporal
    phys: datetime
    desc: 操作时间
  - name: operator_user_id
    type: string
    phys: varchar(64)
    desc: 操作人 userId
  - name: operator_user_name
    type: string
    phys: varchar(64)
    desc: 操作人姓名
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_tenant_project_approval_flow_node_project_approval
    type: string
    phys: varchar(128)
    desc: 关联项目审批
  - name: ref_tenant_project_approval_flow_node_project_approval_flow
    type: string
    phys: varchar(128)
    desc: 关联项目审批流程
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: transfer_to_user_id
    type: string
    phys: varchar(64)
    desc: 被转审人id
  - name: transfer_to_user_name
    type: string
    phys: varchar(64)
    desc: 被转审人name
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

- [[tenant_project_approval_flow_credit]]：tenant_project_approval_flow_node.code → tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node（write-flow:ProjectApprovalDeskApplication.java，confirmed）
- [[tenant_project_approval_flow_file]]：tenant_project_approval_flow_node.code → tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node（write-flow:ProjectApprovalDeskApplication.java，confirmed）
- [[tenant_project_approval_flow_file]]：tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval → tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval（write-flow:ProjectApprovalDeskApplication.java，confirmed）
- [[tenant_project_approval_flow]]：tenant_project_approval_flow_node.node_code → tenant_project_approval_flow.node_code（java-eq-same:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow]]：tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow → tenant_project_approval_flow.code（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval]]：tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval → tenant_project_approval.code（java-eq:ProjectApprovalDeskApplication.java，suggested）
## 需求背景

节点操作类型决定流程状态如何推进：同意进入已通过、退回回到待审批、驳回进入已拒绝，见 [[processes/tenant_project_approval_flow_node_status]]。节点属性还参与后补合作协议的触发判断——业务经理节点同意且该节点记录 `is_back_agreement=Y` 时启动后续流程，见 [[rules/back_agreement_trigger]]，其中 `node_code` 用于识别节点身份。业务系统推送项目配置同样以节点维度做准入判断，见 [[calibers/approving_flow_node]]。

## 版本演进

当前语义分析未提供该表节点操作类型的历史变更记录。
