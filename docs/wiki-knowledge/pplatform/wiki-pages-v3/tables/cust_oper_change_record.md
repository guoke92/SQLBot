---
type: table
title: 运营人员变更记录
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
contract_version: "0.3"
belong: tables
scenes: [oper_change]
---

# 运营人员变更记录

场景 [[oper_change]] 主档。`person_id` → [[cust_person_info]].id。前后运营人 id 逻辑对齐 [[operation_user]].operation_id，姓名已打在记录上。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[oper_change]]

`id`, `enable`, `create_time`, `update_time`, `after_operator_id`, `before_operator_id`, `change_type`, `person_id`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `after_operator_name`, `app_tenant_code`, `asset_id`, `asset_no`, `before_operator_name`, `change_reason`, `company_code`, `company_id`, `company_name`, `db_tenant_code`, `name`, `organization_id`, `person_name`, `remark`, `source_system`

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
desc: 客户操作运营变更记录
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [oper_change]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    roles: [query]
    group: always
    scenes: [oper_change]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [oper_change]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [oper_change]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: after_operator_id
    type: string
    phys: varchar(64)
    desc: "变更后运营人"
    scenes: [oper_change]
  - name: before_operator_id
    type: string
    phys: varchar(64)
    desc: "变更前运营人"
    scenes: [oper_change]
  - name: change_type
    type: string
    phys: varchar(30)
    desc: "变更类型"
    dict: oper_change_type
    topk: "ASSET_AUDIT_SYNC|BATCH|CUST_CHANGE_CALLBACK|MANUAL"
    roles: [query]
    scenes: [oper_change]
  - name: person_id
    type: number
    phys: bigint(20)
    desc: "联系人id"
    roles: [query]
    scenes: [oper_change]
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: after_operator_name
    type: string
    phys: varchar(128)
    desc: "变更后运营人员姓名"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: asset_id
    type: string
    phys: varchar(64)
    desc: "资产id"
  - name: asset_no
    type: string
    phys: varchar(64)
    desc: "资产编号"
  - name: before_operator_name
    type: string
    phys: varchar(128)
    desc: "变更前运营人员姓名"
  - name: change_reason
    type: string
    phys: varchar(256)
    desc: "变更原因"
  - name: company_code
    type: string
    phys: varchar(60)
    desc: "企业编号"
  - name: company_id
    type: number
    phys: bigint(20)
    desc: "企业ID"
  - name: company_name
    type: string
    phys: varchar(128)
    desc: "企业名称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: person_name
    type: string
    phys: varchar(128)
    desc: "联系人姓名"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: source_system
    type: string
    phys: varchar(64)
    desc: "来源系统"
```

```ground:relation
type: EQUI_JOIN
left: cust_oper_change_record.person_id
right: cust_person_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:OperChangeRecordApplication.java
```
