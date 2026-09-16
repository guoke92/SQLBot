---
type: table
title: 企业定制产品入口
page_key: cust_customized_product
domain: 平台产品配置
status: draft
anchors: [cust_customized_product]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [platform_product]
---

# 企业定制产品入口

企业自己的产品入口 URL / logo。`ref_cust_customized_product_cust_company_info` → 企业 `code`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[platform_product]]

`id`, `enable`, `create_time`, `update_time`, `cust_id`, `url`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `logo_icon_url`, `name`, `organization_id`, `ref_cust_customized_product_cust_company_info`, `remark`, `view_order`

```ground:table
table: cust_customized_product
database: lowcode_pplatform
desc: 客户快捷入口配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [platform_product]
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
    scenes: [platform_product]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [platform_product]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [platform_product]
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
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    roles: [query]
    scenes: [platform_product]
  - name: url
    type: string
    phys: varchar(512)
    desc: "入口地址"
    scenes: [platform_product]
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
    topk: "base|dsjx"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "LN1|beehive-scf.qhhrly.cn|dsjx"
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: "图标"
  - name: name
    type: string
    phys: varchar(128)
    desc: "产品名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: ref_cust_customized_product_cust_company_info
    type: string
    phys: varchar(128)
    desc: "客户关联自定义产品配置"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: view_order
    type: number
    phys: int(10)
    desc: "显示顺序"
```

```ground:relation
type: EQUI_JOIN
left: cust_customized_product.ref_cust_customized_product_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustCustomizedProductDO.java
```
