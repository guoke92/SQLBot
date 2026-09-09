---
type: table
title: 集团成员单位关系表
page_key: cust_group_rel
belong: tables
domain: 基线
status: draft
anchors: [cust_group_rel]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 集团成员单位关系表

（基线页：27 字段，行数估计 674。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_group_rel
database: lowcode_pplatform
desc: 集团成员单位关系表
inactive: false
fields:
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
    roles: [query, result]
  - name: cust_type
    type: string
    phys: varchar(256)
    desc: 企业角色 多企业角色用逗号分隔
    dict: cust_type
    roles: [query, result]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    roles: [query, result]
  - name: parent_group_id
    type: number
    phys: bigint(20)
    desc: 父id
    roles: [query, result]
  - name: root_cust_id
    type: number
    phys: bigint(20)
    desc: 根企业id
    roles: [query, result]
  - name: root_group_id
    type: number
    phys: bigint(20)
    desc: 根id
    roles: [query, result]
  - name: status
    type: string
    phys: varchar(256)
    desc: "状态 已生效:EFFECTIVE 未生效:INEFFECTIVE 已拒绝:REJECTED"
    dict: cust_group_rel__status
    topk: EFFECTIVE|INEFFECTIVE|REJECTED
    roles: [result]
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
    topk: base
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    roles: [result]
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    roles: [result]
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_CJTZ|ISOLATE_TAG_HBCI|ISOLATE_TAG_HBLT|ISOLATE_TAG_hylg
  - name: level
    type: number
    phys: int(10)
    desc: 层级
    topk: 1
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: parent_cust_id
    type: number
    phys: bigint(20)
    desc: 父企业id
    roles: [result]
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: root_flag
    type: string
    phys: varchar(4)
    desc: "是否集团企业 Y:是 N:不是"
    topk: N|Y
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    roles: [result]
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    roles: [result]
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    roles: [result]
```

## 关联表

- [[cust_company_info]]：cust_group_rel.root_cust_id → cust_company_info.id（java-eq:CustGroupRelApplication.java，suggested）
