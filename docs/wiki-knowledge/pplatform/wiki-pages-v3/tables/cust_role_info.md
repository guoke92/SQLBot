---
type: table
title: 企业角色切片
page_key: cust_role_info
domain: 客户角色与端口
status: draft
anchors: [cust_role_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_role]
---

# 企业角色切片

场景 [[company_role]] 主档。`role_type` 用 [[company_type]]。`status` 用联系人/角色激活字典（未激活/已激活），不要套企业 [[cust_status]] 的「新增/生效」。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_role]]

`id`, `enable`, `create_time`, `update_time`, `platform_cust_id`, `ref_cust_auth_application`, `ref_cust_company_info`, `role_type`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `main_data_id`, `name`, `organization_id`, `remark`

```ground:table
table: cust_role_info
database: lowcode_pplatform
desc: 客户产品角色关联表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    roles: [query, result]
    group: always
    scenes: [company_role]
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
    scenes: [company_role]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    roles: [result]
    group: always
    scenes: [company_role]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_role]
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
  - name: platform_cust_id
    type: number
    phys: bigint(20)
    desc: "关联平台企业ID"
    scenes: [company_role]
  - name: ref_cust_auth_application
    type: string
    phys: varchar(128)
    desc: "应用客户角色"
    scenes: [company_role]
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: "客户类型"
    scenes: [company_role]
  - name: role_type
    type: string
    phys: varchar(512)
    desc: "角色类型"
    topk: ""CORE"|"SUPPLIER"|CORE|CORE_ADMIN|CORE_MANAGER|CORE_SUB|CORPORATION_COMPANY|DEALER|FACTOR_COMPANY|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
    roles: [query]
    scenes: [company_role]
  - name: status
    type: string
    phys: varchar(64)
    desc: "状态"
    topk: "ADD|EFFECT|FREEZE|WRITEOFF"
    scenes: [company_role]
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
    topk: "QA2tiepai2|base|common|zlskscf"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: "主数据id"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    roles: [query, result]
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```

```ground:relation
type: EQUI_JOIN
left: cust_role_info.ref_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustRoleInfoDO.java
```

```ground:relation
type: EQUI_JOIN
left: cust_role_info.ref_cust_auth_application
right: cust_auth_application.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustRoleInfoDO.java
```
