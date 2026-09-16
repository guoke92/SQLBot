---
type: table
title: 企业项目关系
page_key: cust_project_rel
domain: 项目报表/统计/上报
status: draft
anchors: [cust_project_rel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_project]
---

# 企业项目关系

`project_id` 对齐 [[tenant_project]].id（字符串）。`ref_cust_project_rel_cust_company_info` → 企业 `code`。运营联系人字段是从项目拷贝的 DERIVED。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_project]]

`id`, `enable`, `create_time`, `update_time`, `channel_code`, `company_type`, `product_id`, `project_id`, `show_flag`, `top_flag`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `config_model`, `db_tenant_code`, `name`, `op_contact_a`, `op_contact_a_group`, `op_contact_b`, `op_update_time`, `op_update_user`, `organization_id`, `project_open_status`, `ref_cust_project_rel_cust_company_info`, `ref_cust_project_rel_platform_product`, `remark`, `risk_control_contact_a`, `risk_control_contact_a_group`, `risk_control_contact_b`, `status`, `tenant_code`, `tenant_flg_en`, `verification_contact`, `verification_contact_group`

```ground:table
table: cust_project_rel
database: lowcode_pplatform
desc: 客户项目关联表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    roles: [query, result]
    group: always
    scenes: [company_project]
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
    scenes: [company_project]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    roles: [result]
    group: always
    scenes: [company_project]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_project]
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
  - name: channel_code
    type: string
    phys: varchar(128)
    desc: "渠道编码"
    scenes: [company_project]
  - name: company_type
    type: string
    phys: varchar(128)
    desc: "企业角色"
    dict: company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PLATFORM_OPREATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
    roles: [query]
    scenes: [company_project]
  - name: product_id
    type: string
    phys: varchar(512)
    desc: "租户产品id"
    scenes: [company_project]
  - name: project_id
    type: string
    phys: varchar(512)
    desc: "项目id"
    roles: [query]
    scenes: [company_project]
  - name: show_flag
    type: string
    phys: varchar(20)
    desc: "是否展示"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [company_project]
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: "是否置顶"
    topk: "0|1"
    labels: "0:否|1:是"
    scenes: [company_project]
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
    topk: "base|common|xyc.llschain.com"
  - name: config_model
    type: string
    phys: varchar(8)
    desc: "项目配置模式"
    topk: "admin"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    roles: [query, result]
  - name: op_contact_a
    type: string
    phys: varchar(64)
    desc: "运营对接人A"
    topk: "141|145|257|267|333|344|360|383|411|415|420|454|466|93|OP001|OP002|OP003|OP010"
    roles: [query, result]
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: "运营组别"
    roles: [query, result]
  - name: op_contact_b
    type: string
    phys: varchar(400)
    desc: "运营对接人B"
    roles: [result]
  - name: op_update_time
    type: temporal
    phys: datetime
    desc: "运营信息更新时间"
    roles: [result]
  - name: op_update_user
    type: string
    phys: varchar(64)
    desc: "运营信息更新人"
    topk: "刘倍材|刘宁"
    roles: [result]
  - name: organization_id
    type: string
    phys: varchar(30)
  - name: project_open_status
    type: string
    phys: varchar(64)
    desc: "项目开通状态"
    topk: "NOT_OPEN|OPENED"
  - name: ref_cust_project_rel_cust_company_info
    type: string
    phys: varchar(128)
    desc: "客户和项目关系"
  - name: ref_cust_project_rel_platform_product
    type: string
    phys: varchar(128)
    desc: "平台产品"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
    topk: "ACFLOW|AMS|BEECREDIT|DEALER|DRAFT|DRAFTQA|ORDER|RVSFACTOR|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: "风控对接人A"
    topk: "257|267|333|344|360|383|420|441|466|97|OP001|OP002|OP005|OP006|OP007"
    roles: [query, result]
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: "风控组别"
    roles: [query, result]
  - name: risk_control_contact_b
    type: string
    phys: varchar(200)
    desc: "风控对接人B"
    roles: [result]
  - name: status
    type: string
    phys: varchar(64)
    desc: "关联状态"
    topk: " 1 |0|1"
  - name: tenant_code
    type: string
    phys: varchar(512)
    desc: "租户"
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: "项目标识（英文）"
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: "查验对接人"
    topk: "257|289|333|344|360|383|404|430|454|97|OP001|OP002|OP003|OP004"
    roles: [query, result]
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: "查验组别"
    roles: [query, result]
```

```ground:relation
type: EQUI_JOIN
left: cust_project_rel.project_id
right: tenant_project.id
cardinality: many_to_one
status: proposed
evidence: code_path:extract-relationships.yaml
```

```ground:relation
type: EQUI_JOIN
left: cust_project_rel.ref_cust_project_rel_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:QuerySqlOptimizerImpl.java
```
