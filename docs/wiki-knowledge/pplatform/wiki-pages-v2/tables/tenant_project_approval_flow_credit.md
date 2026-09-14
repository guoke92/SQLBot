---
type: table
title: 租户项目审批流程授信表
page_key: tenant_project_approval_flow_credit
domain: 微企链立项与项目审批
status: draft
anchors: [tenant_project_approval_flow_credit]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 租户项目审批流程授信表

（基线页：30 字段，行数估计 144。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_flow_credit
database: lowcode_pplatform
desc: 租户项目审批流程授信表
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
  - name: is_group_limit
    type: string
    phys: varchar(64)
    desc: 是否为集团额度：Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_recyclable
    type: string
    phys: varchar(64)
    desc: 额度是否可循环：Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
    topk: "LN1|LN2|beehive-scf.qhhrly.cn|sdhsg.beehive-scf.qhhrly.cn|xib.qhhrly.cn"
  - name: finance_email
    type: string
    phys: varchar(128)
    desc: 资金方邮箱（需格式校验）
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

- [[tenant_project_approval_flow_node]]：tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval_node → tenant_project_approval_flow_node.code（write-flow:ProjectApprovalDeskApplication.java，confirmed）
- [[tenant_project_approval]]：tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval → tenant_project_approval.code（java-eq:ProjectApprovalApplication.java，suggested）
