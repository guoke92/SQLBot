---
type: table
title: 租户项目审批流程节点表
page_key: tenant_project_approval_flow_node
domain: 基线
status: draft
anchors: [tenant_project_approval_flow_node]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目审批流程节点表

（基线页：33 字段，行数估计 895。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_flow_node
database: lowcode_pplatform
desc: 租户项目审批流程节点表
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
    topk: base|sdhsg
  - name: approval_type
    type: string
    phys: varchar(64)
    desc: 审批类型
    topk: BACK_AGREEMENT|ONLINE_APPROVAL
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
    topk: 114|1207485686830276611|1447805269378883586|1480444461854887938
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 刘倍材|刘宁|刘艳霞|吴东洋
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_gy|ISOLATE_TAG_szbank|LN1|LN2
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: is_back_agreement
    type: string
    phys: varchar(64)
    desc: 是否后补合作协议
    topk: N|Y
  - name: is_low_risk
    type: string
    phys: varchar(64)
    desc: 是否低风险项目
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: node_code
    type: string
    phys: varchar(64)
    desc: 节点编码
    topk: BUSINESS_MANAGER|LEGAL_PROCESS|LEGAL_REVIEW|OPERATION
  - name: node_order
    type: number
    phys: int(10)
    desc: 审批顺序，从1开始
    topk: 1|10|11|12
  - name: operate_time
    type: temporal
    phys: datetime
    desc: 操作时间
  - name: operate_type
    type: string
    phys: varchar(64)
    desc: 操作类型
    topk: back|delegate|pass|reject
  - name: operator_user_id
    type: string
    phys: varchar(64)
    desc: 操作人 userId
    topk: 114|1207485686830276611|1447805269378883586|1480444461854887938
  - name: operator_user_name
    type: string
    phys: varchar(64)
    desc: 操作人姓名
    topk: 刘倍材|刘宁|刘艳霞|吴东洋
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
    topk: 1207485686830276611|1364399217692581890|1480444461854887938|1525044710953656322
  - name: transfer_to_user_name
    type: string
    phys: varchar(64)
    desc: 被转审人name
    topk: 侯叔彤|刘倍材|刘宁|吴东洋
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 114|1207485686830276611|1447805269378883586|1480444461854887938
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 刘倍材|刘宁|刘艳霞|吴东洋
```

## 关联表

- [[tenant_project_approval]]：tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval → tenant_project_approval.code（java-eq:ProjectApprovalDeskApplication.java，suggested）
- [[tenant_project_approval_flow]]：tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow → tenant_project_approval_flow.code（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow_credit]]：tenant_project_approval_flow_node.code → tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node（write-flow:ProjectApprovalDeskApplication.java，confirmed）
- [[tenant_project_approval_flow_file]]：tenant_project_approval_flow_node.code → tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node（write-flow:ProjectApprovalDeskApplication.java，confirmed）
