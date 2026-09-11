---
type: table
title: 项目上线审批表（tenant_project_approval）
page_key: tables/tenant_project_approval
domain: 租户项目
status: draft
aliases: [tenant_project_approval, 项目上线审批表]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


项目上线审批表承载 [[tables/tenant_project]] 的上线审批实例，是项目由「审批中」走向生效的凭据；审批通过后触发项目生效（见 [[rules/effective_on_approval_finished]]）。工作流状态的完整迁移见 [[processes/project_approval_workflow_status]]，节点级状态见 [[processes/project_approval_node_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表要解决的是「项目上线需要审批、审批可以反复发起、草稿可暂存」这三件事，并通过复制新审批记录回到待发起态。

## 版本演进
本次语义分析未给出本表的字段级语义（field_semantics 未覆盖），仅状态机证据可用；因此本页锚点只登记 wf_status 的取值，字段清单待补。

```ground:table
table: tenant_project_approval
database: lowcode_pplatform
desc: 租户项目审批表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: wf_status
    type: string
    desc: 工作流状态
    dict: wf_status
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
  - name: approval_no
    type: string
    desc: 审批编号，格式：SX+yyyymmdd+xxx
  - name: capital_names
    type: string
    desc: 资金方名称(JSON格式字符串，含order字段标记顺序)
  - name: code
    type: string
    desc: 编码
  - name: complete_time
    type: temporal
    desc: 完成时间
  - name: core_enterprise_names
    type: string
    desc: 核心企业名称(JSON格式字符串，含order字段标记顺序)
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
  - name: flow_code
    type: string
    desc: 流程配置编码（tenant_project_approval_flow_config#flow_code）
  - name: initiate_time
    type: temporal
    desc: 发起时间
  - name: initiator_user_id
    type: string
    desc: 发起人 userId
  - name: initiator_user_name
    type: string
    desc: 发起人姓名
  - name: is_add
    type: string
    desc: 是否新增项目；Y=是，N=否
  - name: is_latest
    type: string
    desc: 是否最新审批
  - name: is_low_risk
    type: string
    desc: 是否低风险项目:Y,N
  - name: is_online_approval
    type: string
    desc: 是否发起上线审批：Y/N
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: project_plan
    type: string
    desc: 项目方案描述
  - name: project_type
    type: string
    desc: 项目类型：STANDARD（标准） / REGULAR（常规）
  - name: ref_tenant_project_approval_tenant_project
    type: string
    desc: 关联租户项目
  - name: ref_tenant_project_approval_tenant_project_approval
    type: string
    desc: 关联原审批数据
  - name: ref_tenant_project_approval_tenant_project_approval_flow_config
    type: string
    desc: 关联租户项目流程配置
  - name: related_approval_no
    type: string
    desc: 关联审批编号
  - name: remark
    type: string
    desc: remark
  - name: simple_mode
    type: string
    desc: 是否为简易模式项目/常规非低风险项目，Y/N
  - name: solution_manager_id
    type: string
    desc: 方案经理 userId
  - name: solution_manager_name
    type: string
    desc: 方案经理姓名
  - name: sp_no
    type: string
    desc: 立项审批编号（wechat_project_approval_apply#sp_no）
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
  - name: wf_last_operate_time
    type: temporal
    desc: 工作流最近操作时间
  - name: wf_last_operator
    type: string
    desc: 工作流最近操作人
  - name: wf_last_operator_id
    type: string
    desc: 工作流最近操作人ID
  - name: wf_procdef_key
    type: string
    desc: 工作流流程定义key
  - name: whitelist_query_result
    type: string
    desc: 白名单查询结果(JSON，提交后锁定)
```
## 关联表

- [[tenant_project]]：tenant_project_approval.ref_tenant_project_approval_tenant_project → tenant_project.code（ref-convention:TenantProjectApprovalDO.java，suggested）
- [[tenant_project_approval_business_info]]：tenant_project_approval.code → tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow]]：tenant_project_approval.code → tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval（ref-convention:TenantProjectApprovalFlowDO.java，suggested）
- [[tenant_project_approval_flow_config]]：tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config → tenant_project_approval_flow_config.code（ref-convention:TenantProjectApprovalDO.java，suggested）
- [[tenant_project_approval_flow_credit]]：tenant_project_approval.code → tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow_node]]：tenant_project_approval.code → tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval（java-eq:ProjectApprovalDeskApplication.java，suggested）
