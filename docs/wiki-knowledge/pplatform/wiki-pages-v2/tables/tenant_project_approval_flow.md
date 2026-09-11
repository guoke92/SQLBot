---
type: table
title: 项目上线审批节点表（tenant_project_approval_flow）
page_key: tables/tenant_project_approval_flow
domain: 租户项目
status: draft
aliases: [tenant_project_approval_flow, 项目上线审批节点表]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


项目上线审批节点表记录审批实例下的每个审批节点状态，是 [[tables/tenant_project_approval]] 的下级明细。节点状态迁移见 [[processes/project_approval_node_status]]，其中「业务经理节点通过」同时是后补合作协议判断的触发点（见 [[rules/back_agreement_check]]）。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表要解决的是审批流中各节点的处理进度落库，并驱动后续协议判断。

## 版本演进
本表未进入 field_semantics，仅节点状态机证据可用；字段清单与节点定义方式待补。

```ground:table
table: tenant_project_approval_flow
database: lowcode_pplatform
desc: 租户项目审批流程表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: node_status
    type: string
    desc: 节点状态
    dict: node_status
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: approver_user_id
    type: string
    desc: 审批人 userId
  - name: approver_user_name
    type: string
    desc: 审批人姓名
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: is_operate
    type: string
    desc: 是否可编辑
  - name: is_optional
    type: string
    desc: 是否可选节点：Y/N
  - name: name
    type: string
    desc: 名称
  - name: node_code
    type: string
    desc: 节点编码
  - name: node_name
    type: string
    desc: 节点名称（中文）
  - name: node_order
    type: number
    desc: 节点顺序，从 1 开始
  - name: organization_id
    type: string
    desc: 机构编号
  - name: ref_tenant_project_approval_flow_tenant_project_approval
    type: string
    desc: 关联项目审批
  - name: remark
    type: string
    desc: remark
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```
## 关联表

- [[tenant_project_approval]]：tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval → tenant_project_approval.code（ref-convention:TenantProjectApprovalFlowDO.java，suggested）
- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow.code → tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow（java-eq:ProjectApprovalApplication.java，suggested）
