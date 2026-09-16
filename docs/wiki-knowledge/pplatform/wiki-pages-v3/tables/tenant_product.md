---
type: table
title: 租户通用产品
page_key: tenant_product
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_product]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [tenant_product, product_activation]
---

# 租户通用产品

租户对 GENERAL 产品的开通行。`open_status` 为 Y/P/N（[[open_status]]），开通后会增加平台产品引用计数。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[product_activation]]

`id`, `code`, `enable`, `create_time`, `update_time`, `open_status`, `platform_product_code`

### [[tenant_product]]

`id`, `enable`, `create_time`, `update_time`, `open_status`, `platform_product_code`, `platform_product_id`, `ref_tenant_product_tenant_setting_config`

### [[tenant_project]]

`id`, `enable`, `create_time`, `update_time`, `open_status`, `platform_product_code`

### 未分窗

仍留表页，待代码证据划入场景：`is_migratory`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `credit_measures`, `customer_group`, `db_tenant_code`, `logo_icon_url`, `max_financing_amount`, `max_financing_amount_flag`, `max_financing_period`, `multiple`, `name`, `organization_id`, `product_agreement`, `product_cate`, `product_description`, `product_summary`, `product_web_url`, `ref_tenant_product_project_code`, `remark`, `tenant_id`, `transaction_structure`, `view_order`

```ground:table
table: tenant_product
database: lowcode_pplatform
desc: 租户产品配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "主键"
    roles: [query]
    group: always
    scenes: [product_activation, tenant_product, tenant_project]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    roles: [query]
    group: always
    scenes: [product_activation]
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    group: always
    scenes: [product_activation, tenant_product, tenant_project]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [product_activation, tenant_product, tenant_project]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [product_activation, tenant_product, tenant_project]
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
  - name: is_migratory
    type: string
    phys: varchar(4)
    desc: "是否迁移标识,N代表未迁移,Y代表迁移"
    dict: enable
    topk: "N|Y"
    labels: "N:代表未迁移|Y:代表迁移"
  - name: open_status
    type: string
    phys: varchar(16)
    desc: "开通状态"
    dict: open_status
    topk: "N|P|Y"
    labels: "N:未开通|P:开通中|Y:已开通"
    roles: [query]
    scenes: [product_activation, tenant_product, tenant_project]
  - name: platform_product_code
    type: string
    phys: varchar(128)
    desc: "平台产品编码"
    topk: "ACFLOW|BEECREDIT|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [query]
    scenes: [product_activation, tenant_product, tenant_project]
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: "平台产品id"
    scenes: [tenant_product]
  - name: ref_tenant_product_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: "租户-产品"
    scenes: [tenant_product]
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
  - name: credit_measures
    type: string
    phys: varchar(128)
    desc: "增信措施"
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: "客户群体"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: "产品logo"
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: "融资金额上限"
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: "是否限额融资资金上线"
    topk: "0|1|N|Y"
    labels: "0:否|1:是|N:否|Y:是"
  - name: max_financing_period
    type: string
    phys: varchar(128)
    desc: "融资期限上限"
    topk: "0|12|12个月|36|36个月|6|6-12个月|6个月"
  - name: multiple
    type: string
    phys: varchar(512)
    desc: "是否多个"
    topk: "0"
    labels: "0:否"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: product_agreement
    type: string
    phys: varchar(1024)
    desc: "产品协议"
  - name: product_cate
    type: string
    phys: varchar(16)
    desc: "产品类型"
    topk: "CREDIT|STRONG|WEAKLY"
  - name: product_description
    type: string
    phys: text
    desc: "产品详细描述"
  - name: product_summary
    type: string
    phys: text
    desc: "产品概述"
  - name: product_web_url
    type: string
    phys: varchar(512)
    desc: "站点url"
  - name: ref_tenant_product_project_code
    type: string
    phys: varchar(128)
    desc: "租户产品-平台产品"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "租户id"
  - name: transaction_structure
    type: string
    phys: text
    desc: "交易结构"
  - name: view_order
    type: number
    phys: int(10)
    desc: "展示顺序"
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.platform_product_code
right: platform_product.product_code
cardinality: many_to_one
status: proposed
evidence: code_path:TenantProductDomainService.java
```
