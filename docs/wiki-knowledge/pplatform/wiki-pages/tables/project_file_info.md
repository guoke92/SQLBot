---
type: table
title: 项目运营文件管理
page_key: project_file_info
domain: 基线
status: draft
anchors: [project_file_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 项目运营文件管理

（基线页：22 字段，行数估计 51。行语义/常用过滤待语义摄取增强。）

```ground:table
table: project_file_info
database: lowcode_pplatform
desc: 项目运营文件管理
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
    topk: base
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: content
    type: string
    phys: varchar(500)
    desc: 描述
    topk: 1|10|11|123
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1207485686830276611|1525044710953656322|1761948088379621378|1947932799637422081
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 何琳|吴东洋|林彦湘|肖龙豪
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: file_type
    type: string
    phys: varchar(32)
    desc: 文件模块类型
    topk: approve|check|collate|cust
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 关联项目ID
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: title
    type: string
    phys: varchar(200)
    desc: 标题
    topk: 1|10|11|123
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1207485686830276611|1525044710953656322|1947932799637422081|1998571949021429761
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 何琳|吴东洋|林彦湘|肖龙豪
```
