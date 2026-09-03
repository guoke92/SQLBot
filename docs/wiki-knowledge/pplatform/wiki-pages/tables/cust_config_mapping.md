---
type: table
title: 企业信息配置表
page_key: cust_config_mapping
domain: 基线
status: draft
anchors: [cust_config_mapping]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 企业信息配置表

（基线页：25 字段，行数估计 35。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_config_mapping
database: lowcode_pplatform
desc: 企业信息配置表
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
    topk: beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: groups
    type: string
    phys: varchar(32)
    desc: 分组
    topk: BRANCH_COMPANY|HEAD_COMPANY
  - name: inner_code
    type: string
    phys: varchar(32)
    desc: 内部编码
  - name: inner_name
    type: string
    phys: varchar(128)
    desc: 内部名称
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: outer_channel
    type: string
    phys: varchar(128)
    desc: 外部渠道
    topk: ACFLOW|OPS|ORDER|SELF
  - name: outer_code
    type: string
    phys: varchar(128)
    desc: 外部编码
    topk: A0002|A0004|A0007|A0008
  - name: outer_name
    type: string
    phys: varchar(128)
    desc: 外部名称
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: type
    type: string
    phys: varchar(64)
    desc: 类型
    topk: CHANGE_ITEM|COMPANY_MEDIA|COMPANY_TYPE_MAPPING
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
