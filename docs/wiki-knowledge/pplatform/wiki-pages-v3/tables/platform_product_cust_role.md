---
type: table
title: 产品企业角色矩阵
page_key: platform_product_cust_role
domain: 客户角色与端口
status: draft
anchors: [platform_product_cust_role]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_role, platform_product]
---

# 产品企业角色矩阵

配置表：某 `product_code` 允许哪些 `company_type_code`。不是客户已开通角色。`company_type_name` 是中文展示拷贝。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_role]]

`id`, `enable`, `create_time`, `update_time`, `company_type_code`, `company_type_name`, `product_code`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `name`, `organization_id`, `remark`

```ground:table
table: platform_product_cust_role
database: lowcode_pplatform
desc: 平台产品企业角色
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
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
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    group: always
    scenes: [company_role]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
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
  - name: company_type_code
    type: string
    phys: varchar(32)
    desc: "企业角色编码"
    dict: company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
    roles: [query]
    scenes: [company_role]
  - name: company_type_name
    type: string
    phys: varchar(128)
    desc: "企业角色名称"
    scenes: [company_role]
  - name: product_code
    type: string
    phys: varchar(128)
    desc: "产品编码"
    topk: "ACCOUNT_PRODUCT|ACFLOW|AMS|BEECREDIT|CROSSBORDER|DEALER|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [query]
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: name
    type: string
    phys: varchar(64)
    desc: "产品名称拷贝"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```
