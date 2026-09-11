---
type: table
title: 客户应用渠道关系
page_key: cust_app_channel_config
domain: 基线
status: draft
anchors: [cust_app_channel_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# 客户应用渠道关系

（基线页：19 字段，行数估计 1。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_app_channel_config
database: lowcode_pplatform
desc: 客户应用渠道关系
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
  - name: app_id
    type: string
    phys: varchar(64)
    desc: 应用id
    topk: 73d62771729e4ffba7f263cb6012746d
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: longteng
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
    topk: longteng
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
    topk: minmetals
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: longteng
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
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
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```
