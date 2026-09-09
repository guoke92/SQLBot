---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log_bak
belong: tables
domain: 基线
status: draft
anchors: [tenant_migarory_log_bak]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目迁移记录表

（基线页：33 字段，行数估计 4547。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_migarory_log_bak
database: lowcode_pplatform
desc: 租户项目迁移记录表
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
    topk: base|common
  - name: batch_no
    type: string
    phys: varchar(32)
    desc: 批次号
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
  - name: data
    type: string
    phys: text
    desc: 迁移数据
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: direction
    type: string
    phys: varchar(16)
    desc: 数据方向
    topk: IN|OUT
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: error
    type: string
    phys: text
    desc: 错误信息
  - name: falied_number
    type: number
    phys: bigint(20)
    desc: 失败数量
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: ACTIVE_CFCA_SIGN|CHANGED|CREATED|DELETED
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(256)
    desc: 产品编码
  - name: remark
    type: string
    phys: text
    desc: remark
  - name: req_no
    type: string
    phys: varchar(32)
    desc: 请求编号
  - name: req_sn
    type: string
    phys: varchar(1320)
    desc: 请求流水编码
  - name: request
    type: string
    phys: text
    desc: 请求数据
  - name: response
    type: string
    phys: text
    desc: 返回数据
  - name: status
    type: string
    phys: varchar(128)
    desc: 迁移状态
    topk: N|Y
  - name: success_number
    type: number
    phys: bigint(20)
    desc: 成功数量
  - name: total_number
    type: number
    phys: bigint(20)
    desc: 总数量
  - name: trace_id
    type: string
    phys: varchar(128)
    desc: trace_id
  - name: type
    type: string
    phys: varchar(64)
    desc: 类型
    topk: CREATED|CUST_PRODUCT_SYNC|DELETED|EFFECTED
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
