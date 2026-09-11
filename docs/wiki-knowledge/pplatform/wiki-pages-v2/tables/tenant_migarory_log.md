---
type: table
title: tenant_migarory_log（租户迁移日志表）
page_key: tenant_migarory_log
domain: 租户迁移
status: draft
aliases: [租户迁移日志, 迁移日志表, tenant_migratory_log]
oid: 1
scope:
  databases: [未提供]
sources:
  - db
contract_version: "0.1"
---


tenant_migarory_log 是租户迁移/同步主链路上的日志表：每一次迁移或同步动作都会在本表留下一条记录，记录本次请求的方向（入向/出向）、操作类型与事件名称、请求编号与流水编码、产品与租户标识、迁移数据载荷、请求/响应报文，以及成功、失败与总量三个计数。它是判断“某个租户/项目/客户迁移是否成功”的第一事实来源，也是 [[migration_tenant_log]]、[[migration_project_log]]、[[migration_cust_log]] 三个口径的承载表。

```ground:table
table: tenant_migarory_log
database: lowcode_pplatform
desc: 租户项目迁移记录表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: batch_no
    type: string
    desc: 批次号
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: data
    type: string
    desc: 迁移数据
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: direction
    type: string
    desc: 数据方向
  - name: enable
    type: string
    desc: enable
  - name: falied_number
    type: number
    desc: 失败数量
  - name: message
    type: string
    desc: 错误信息
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_product_code
    type: string
    desc: 产品编码
  - name: remark
    type: string
    desc: remark
  - name: req_no
    type: string
    desc: 请求编号
  - name: req_sn
    type: string
    desc: 请求流水编码
  - name: request
    type: string
    desc: 请求数据
  - name: response
    type: string
    desc: 返回数据
  - name: status
    type: string
    desc: 迁移状态
  - name: success_number
    type: number
    desc: 成功数量
  - name: total_number
    type: number
    desc: 总数量
  - name: trace_id
    type: string
    desc: trace_id
  - name: type
    type: string
    desc: 类型
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

## 需求背景

本表的字段语义全部来自 DB 值分布证据（evidence: db），没有代码侧证据，因此“type 与 name 双写同一业务含义”的现象需要在口径层显式收口，见 [[migration_tenant_log]] / [[migration_project_log]] / [[migration_cust_log]]。字段拼写 `falied_number` 为库中实际列名，按逐字原则保留，不在本页做纠错推断；`tenant_migarory_log` 的表名拼写同理。

## 版本演进

- v0（草稿）：以 DB 值分布还原 15 个字段的业务含义；status 的 N/Y 语义归入 [[migration_log_success]] 口径，direction 的 IN/OUT 语义仅在本页记录，尚未建立独立口径页。

关联页面：[[migratory_user_record]]、[[migratory_tenant]]、[[migratory_project]]、[[migratory_cust]]。