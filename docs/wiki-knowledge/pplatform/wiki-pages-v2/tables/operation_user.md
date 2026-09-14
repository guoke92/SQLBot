---
type: table
title: 运营中台人员数据
page_key: operation_user
domain: 数据权限与组织
status: draft
anchors: [operation_user]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












运营中台人员表，保存运营侧人员主数据与启用/删除标记。其 operation_id 为外部系统主键，
与登录用户表 [[sys_user]] 不是同一实体，勿按“用户”语义混用；数据租户维度见 [[db_tenant_code]]。

## 需求背景

运营中台人员的账号需与业务登录账号区分管理：删除用 deleted、启停用 enable 双标记，
另有 status 记录人员用户状态（DB 未给出取值分布）。

## 版本演进

- v0（草稿）：字段语义来自 DB 实测，status 取值域未获得证据。

```ground:table
table: operation_user
database: lowcode_pplatform
desc: 运营中台人员数据
fields:
  - name: deleted
    type: string
    phys: varchar(3)
    desc: 删除标识
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "base"
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
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```