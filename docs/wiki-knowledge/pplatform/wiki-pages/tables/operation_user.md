---
type: table
title: 运营中台人员数据
page_key: operation_user
domain: 基线
status: draft
anchors: [operation_user]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 运营中台人员数据

（基线页：23 字段，行数估计 126。行语义/常用过滤待语义摄取增强。）

```ground:table
table: operation_user
database: lowcode_pplatform
desc: 运营中台人员数据
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
    topk: base
  - name: deleted
    type: string
    phys: varchar(3)
    desc: 删除标识
    topk: N|Y
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: operation_group
    type: string
    phys: varchar(64)
    desc: 运营组别
  - name: operation_id
    type: string
    phys: varchar(64)
    desc: 运营中台id
  - name: operation_name
    type: string
    phys: varchar(64)
    desc: 运营人员姓名
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: status
    type: string
    phys: varchar(64)
    desc: 用户状态标识
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
