---
type: table
title: 推送企业的默认项目
page_key: cust_project_pushcust
domain: 基线
status: draft
anchors: [cust_project_pushcust]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 推送企业的默认项目

（基线页：21 字段，行数估计 2。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_project_pushcust
database: lowcode_pplatform
desc: 推送企业的默认项目
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
    topk: ISOLATE_TAG_HBLT|ISOLATE_TAG_JHYL|ZTSJ
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: string
    phys: varchar(64)
    desc: 项目id
    topk: 2150151662310789151|7038695915979223040|7188022193298518016|7272544026650607616
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_sso_channel
    type: string
    phys: varchar(100)
    desc: 起始系统的SSO渠道
    topk: JHYL|ZTSJ|dahua|hubeiliantou
  - name: target_sso_channel
    type: string
    phys: varchar(100)
    desc: 跳转系统的SSO渠道
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
