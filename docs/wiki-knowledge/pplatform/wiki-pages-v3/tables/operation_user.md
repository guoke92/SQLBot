---
type: table
title: 运营中台人员
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
contract_version: "0.3"
belong: tables
scenes: [oper_change]
---

# 运营中台人员

从运营中台同步。有效人员：`deleted='N'` 且 `enable='Y'`。`org_manage` 库空，不用来查组织。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[oper_change]]

`id`, `enable`, `create_time`, `update_time`, `deleted`, `operation_group`, `operation_id`, `operation_name`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `name`, `organization_id`, `remark`, `status`

```ground:table
table: operation_user
database: lowcode_pplatform
desc: 运营中台人员数据
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
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: deleted
    type: string
    phys: varchar(3)
    desc: "删除标识"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    scenes: [oper_change]
  - name: operation_group
    type: string
    phys: varchar(64)
    desc: "运营组别"
    roles: [query]
    scenes: [oper_change]
  - name: operation_id
    type: string
    phys: varchar(64)
    desc: "运营中台id"
    roles: [query]
    scenes: [oper_change]
  - name: operation_name
    type: string
    phys: varchar(64)
    desc: "运营人员姓名"
    roles: [result]
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "base"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: status
    type: string
    phys: varchar(64)
    desc: "用户状态标识"
```
