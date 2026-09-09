---
type: table
title: 客户端接口同步失败记录
page_key: client_api_sync_error
belong: tables
domain: 基线
status: draft
anchors:
  - client_api_sync_error
oid: 1
    - 15
sources:
  - db:db-catalog.yaml
  - code:extract-catalog.yaml
  - enrich:wiki-admin
created: 2026-09-02
updated: 2026-09-02
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户端接口同步失败记录

（基线页：21 字段，行数估计 2045。行语义/常用过滤待语义摄取增强。）

```ground:table
table: client_api_sync_error
database: lowcode_pplatform
desc: 客户端接口同步失败记录
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
    topk: N
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: param
    type: string
    phys: text
    desc: 参数
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: retry_num
    type: number
    phys: int(11)
    desc: 重试次数
    topk: 3
  - name: service_class_name
    type: string
    phys: varchar(256)
    desc: 服务类名称
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
