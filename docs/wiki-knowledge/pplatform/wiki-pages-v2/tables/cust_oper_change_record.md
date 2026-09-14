---
type: table
title: 客户操作运营变更记录
page_key: cust_oper_change_record
domain: 企业变更与运营变更
status: draft
anchors: [cust_oper_change_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`cust_oper_change_record` 记录企业联系人（运营人员）归属的变更历史：一次变更一条记录，以 `before_operator_id` / `after_operator_id` 结构化保存变更前后运营人员。它与 [[cust_change_record]] 是两类不同业务，见 [[customer_change]]；`person_id` 指向 [[cust_person_info]] 的主键，运营人员维度语义见 [[operator]]。

`change_type` 以字面量落库（非枚举 `name()`），与 [[change_status]] 所描述的枚举式状态字段在落库方式上不同，写入方必须保持一致。

## 需求背景

运营人员变更来源多样（手动、批量、自动分配、自动更新、资产审核同步、企业变更回调），需要在同一张表中留存可追溯的变更链路，因此把「谁触发（`source_system` / `change_type`）、改了什么（before/after）、为什么（`change_reason`）」拆开保存；资产审核同步场景额外落 `asset_id`。查询口径见 [[valid_oper_change_record]] 与 [[oper_change_query]]。

## 版本演进

v0.1：首次抽取字段含义与查询口径；本页暂无历史版本差异记录。

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
desc: 客户操作运营变更记录
fields:
  - name: change_type
    type: string
    phys: varchar(30)
    desc: 变更类型
    dict: change_type
    topk: "ASSET_AUDIT_SYNC|BATCH|CUST_CHANGE_CALLBACK|MANUAL"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
  - name: after_operator_id
    type: string
    phys: varchar(64)
    desc: 变更后运营人员ID
  - name: after_operator_name
    type: string
    phys: varchar(128)
    desc: 变更后运营人员姓名
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: asset_id
    type: string
    phys: varchar(64)
    desc: 资产id
  - name: asset_no
    type: string
    phys: varchar(64)
    desc: 资产编号
  - name: before_operator_id
    type: string
    phys: varchar(64)
    desc: 变更前运营人员ID
  - name: before_operator_name
    type: string
    phys: varchar(128)
    desc: 变更前运营人员姓名
  - name: change_reason
    type: string
    phys: varchar(256)
    desc: 变更原因
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_code
    type: string
    phys: varchar(60)
    desc: 企业编号
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业ID
  - name: company_name
    type: string
    phys: varchar(128)
    desc: 企业名称
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
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: person_id
    type: number
    phys: bigint(20)
    desc: 企业联系人id
  - name: person_name
    type: string
    phys: varchar(128)
    desc: 联系人姓名
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_system
    type: string
    phys: varchar(64)
    desc: 来源系统
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

相关页面：[[cust_person_info]]、[[operator]]、[[valid_oper_change_record]]、[[oper_change_query]]、[[customer_change]]。