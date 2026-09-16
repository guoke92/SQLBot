---
type: table
title: 企业产品开通
page_key: cust_auth_application
domain: 自动审核与工作流审核
status: draft
anchors: [cust_auth_application]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [product_activation]
---

# 企业产品开通

场景 [[product_activation]] 主档。`ref_cust_company_info` → 企业 `code`；`ref_cust_auth_application_tenant_product` → [[tenant_product]].code。唯一约束 `(ref_cust_company_info, ref_cust_auth_application_tenant_product)`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[product_activation]]

`id`, `enable`, `create_time`, `update_time`, `open_status`, `open_time`, `platform_product_code`, `ref_cust_auth_application_tenant_product`, `ref_cust_company_info`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `application`, `cust_manager_id`, `db_tenant_code`, `main_data_id`, `name`, `organization_id`, `ref_parent_company`, `remark`

```ground:table
table: cust_auth_application
database: lowcode_pplatform
desc: 客户产品开通表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [product_activation]
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
    scenes: [product_activation]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [product_activation]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [product_activation]
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
  - name: open_status
    type: string
    phys: varchar(512)
    desc: "开通状态"
    dict: cust_product_active
    topk: "NOT_OPENED|OPENED|OPENING"
    labels: "NOT_OPENED:未开通|OPENED:已开通|OPENING:开通中：带客户确认 forams"
    roles: [query]
    scenes: [product_activation]
  - name: open_time
    type: temporal
    phys: datetime
    desc: "开通时间"
    scenes: [product_activation]
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: "平台产品编码"
    topk: "ACFLOW|BEECREDIT|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [query]
    scenes: [product_activation]
  - name: ref_cust_auth_application_tenant_product
    type: string
    phys: varchar(128)
    desc: "租户产品编码"
    roles: [query]
    scenes: [product_activation]
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: "客户编码"
    roles: [query]
    scenes: [product_activation]
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
    topk: "LLS|QA2tiepai2|base|common|xyc.llschain.com"
  - name: application
    type: string
    phys: varchar(64)
    desc: "产品应用"
  - name: cust_manager_id
    type: number
    phys: bigint(20)
    desc: "企业管理员"
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
    phys: varchar(128)
    desc: "产品名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: ref_parent_company
    type: string
    phys: varchar(128)
    desc: "关联母公司"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```

```ground:relation
type: EQUI_JOIN
left: cust_auth_application.ref_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustAuthApplicationDO.java
```

```ground:relation
type: EQUI_JOIN
left: cust_auth_application.ref_cust_auth_application_tenant_product
right: tenant_product.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustProductDomainService.java
```
