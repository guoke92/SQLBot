---
type: table
title: 租户项目审批流程授信表
page_key: tenant_project_approval_flow_credit
belong: tables
domain: 基线
status: draft
anchors: [tenant_project_approval_flow_credit]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目审批流程授信表

（基线页：30 字段，行数估计 130。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_flow_credit
database: lowcode_pplatform
desc: 租户项目审批流程授信表
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
  - name: credit_limit
    type: number
    phys: decimal(20,2)
    desc: 授信额度
  - name: credited_cust_id
    type: string
    phys: varchar(64)
    desc: 被授信方（核心企业）id
  - name: credited_cust_name
    type: string
    phys: varchar(64)
    desc: 被授信方（核心企业）
  - name: crediting_cust_id
    type: string
    phys: varchar(64)
    desc: 授信方（资金方）id
  - name: crediting_cust_name
    type: string
    phys: varchar(64)
    desc: 授信方（资金方）
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: LN1|LN2|beehive-scf.qhhrly.cn|sdhsg.beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: finance_email
    type: string
    phys: varchar(128)
    desc: 资金方邮箱（需格式校验）
  - name: is_group_limit
    type: string
    phys: varchar(64)
    desc: 是否为集团额度：Y/N
    topk: N|Y
  - name: is_recyclable
    type: string
    phys: varchar(64)
    desc: 额度是否可循环：Y/N
    topk: N|Y
  - name: limit_begin_date
    type: temporal
    phys: date
    desc: 额度有效期开始
  - name: limit_end_date
    type: temporal
    phys: date
    desc: 额度有效期结束
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_tenant_project_approval_flow_credit_project_approval
    type: string
    phys: varchar(128)
    desc: 关联项目审批
  - name: ref_tenant_project_approval_flow_credit_project_approval_node
    type: string
    phys: varchar(128)
    desc: 关联项目审批流程节点
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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

- [[tenant_project_approval]]：tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval → tenant_project_approval.code（java-eq:ProjectApprovalApplication.java，suggested）
- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node → tenant_project_approval_flow_node.code（write-flow:ProjectApprovalDeskApplication.java，confirmed）
