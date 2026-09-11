---
type: table
title: 租户项目审批流程配置表
page_key: tenant_project_approval_flow_config
domain: 基线
status: draft
anchors: [tenant_project_approval_flow_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# 租户项目审批流程配置表

（基线页：24 字段，行数估计 15。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_flow_config
database: lowcode_pplatform
desc: 租户项目审批流程配置表
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: flow_code
    type: string
    phys: varchar(64)
    desc: 流程编码：NO_ONLINE，STANDARD，REGULAR
    topk: NO_ONLINE|REGULAR|STANDARD
  - name: is_operate
    type: string
    phys: varchar(64)
    desc: 是否可操作
    topk: N|Y
  - name: is_optional
    type: string
    phys: varchar(64)
    desc: 是否可选节点：Y/N
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: node_code
    type: string
    phys: varchar(64)
    desc: 节点编码字典
    topk: BUSINESS_MANAGER|LEGAL_PROCESS|LEGAL_REVIEW|OPERATION
  - name: node_name
    type: string
    phys: varchar(64)
    desc: 节点名称（中文）
    topk: 业务经理审批|其他|方案经理|方案配置
  - name: node_order
    type: number
    phys: int(10)
    desc: 节点顺序
    topk: 1|2|3|4
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
    topk: 固定杨英|如有|如需
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[tenant_project_approval]]：tenant_project_approval_flow_config.code → tenant_project_approval.ref_tenant_project_approval_tenant_project_approval_flow_config（ref-convention:TenantProjectApprovalDO.java，suggested）
