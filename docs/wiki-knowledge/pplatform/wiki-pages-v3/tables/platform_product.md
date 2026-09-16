---
type: table
title: 平台产品
page_key: platform_product
domain: 平台产品配置
status: draft
anchors: [platform_product]
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

# 平台产品

全局产品模板。业务键 `product_code`（如 ACFLOW）；内部 `code` 给引用。`product_status` 落库 `'0'` 待生效 / `'1'` 已生效。`product_type`：GENERAL 通用产品 / INTERWORKING 互通产品；ALL 的 dictKey 是 `'2'`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[platform_product]]

`id`, `enable`, `create_time`, `update_time`, `basic_product`, `multiple_project_flag`, `product_code`, `product_status`, `product_type`, `wkfl_flag`

### [[tenant_product]]

`id`, `enable`, `create_time`, `update_time`, `product_code`, `product_status`, `product_type`

### 未分窗

仍留表页，待代码证据划入场景：`general_flag`, `max_financing_amount_flag`, `multiple_cust_role_flag`, `platform_flag`, `product_construction_status`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_code`, `app_tenant_code`, `credit_measures`, `cust_role_combine`, `customer_group`, `db_tenant_code`, `default_menu_code`, `default_menu_index`, `logo_icon_url`, `max_financing_amount`, `max_financing_period`, `menu_type`, `multiple_client_type`, `name`, `organization_id`, `platform_code`, `product_cate`, `product_description`, `product_ref_num`, `product_summary`, `project_code`, `project_config`, `remark`, `transaction_structure`

```ground:table
table: platform_product
database: lowcode_pplatform
desc: 平台产品基础配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [platform_product, tenant_product]
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
    scenes: [platform_product, tenant_product]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [platform_product, tenant_product]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [platform_product, tenant_product]
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
  - name: basic_product
    type: string
    phys: varchar(12)
    desc: "是否基础产品"
    scenes: [platform_product]
  - name: general_flag
    type: string
    phys: varchar(2)
    desc: "通用产品标识"
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: "是否限额融资资金上线"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: multiple_cust_role_flag
    type: string
    phys: varchar(2)
    desc: "是否有多企业角色"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: multiple_project_flag
    type: string
    phys: varchar(2)
    desc: "是否多项目"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [platform_product]
  - name: platform_flag
    type: string
    phys: varchar(2)
    desc: "是否平台标识"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: product_code
    type: string
    phys: varchar(128)
    desc: "产品编码"
    topk: "ACFLOW|AMS|BEECREDIT|DEALER|DRAFT|DRAFTQA|HTCP1|HTCP13|HTCP14|HTCP15|HTCP18|HTCP19|HTCP2|HTCP5|HTCP6|HTCP7|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [query]
    scenes: [platform_product, tenant_product]
  - name: product_construction_status
    type: string
    phys: varchar(4)
    desc: "产品建设情况"
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: product_status
    type: string
    phys: varchar(512)
    desc: "产品状态"
    dict: product_status
    topk: "1"
    labels: "1:已生效"
    roles: [query]
    scenes: [platform_product, tenant_product]
  - name: product_type
    type: string
    phys: varchar(16)
    desc: "产品类型"
    dict: product_type
    topk: "GENERAL|INTERWORKING"
    labels: "GENERAL:通用产品|INTERWORKING:互通产品"
    roles: [query]
    scenes: [platform_product, tenant_product]
  - name: wkfl_flag
    type: string
    phys: varchar(512)
    desc: "是否工作流"
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
    topk: "r"
  - name: app_code
    type: string
    phys: varchar(64)
    desc: "蜂搭平台app编号"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: credit_measures
    type: string
    phys: varchar(512)
    desc: "增信措施"
  - name: cust_role_combine
    type: string
    phys: text
    desc: "支持企业角色组合"
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: "客户群体"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "beehive-scf.lianyirong.com.cn|beehive-scf.qhhrly.cn|common"
  - name: default_menu_code
    type: string
    phys: varchar(128)
    desc: "默认菜单编号"
  - name: default_menu_index
    type: number
    phys: int(10)
    desc: "默认菜单编号"
    topk: "1"
    labels: "1:是"
  - name: logo_icon_url
    type: string
    phys: text
    desc: "产品logo"
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: "融资金额上限"
    topk: "0|10亿元|不限"
  - name: max_financing_period
    type: string
    phys: varchar(512)
    desc: "融资期限上限"
    topk: "1-3年|12个月|36个月|6|6个月|HTCP15"
  - name: menu_type
    type: string
    phys: varchar(32)
    desc: "菜单展示类型(topLeft/left)"
    topk: "left"
  - name: multiple_client_type
    type: string
    phys: varchar(128)
    desc: "多端口类型"
    topk: "CompanyType|default"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: platform_code
    type: string
    phys: varchar(16)
    desc: "平台编码"
    topk: "AMS|DRAFT|DRAFTQA|HTCP1|HTCP13|HTCP14|HTCP15|HTCP18|HTCP19|HTCP2|HTCP5|HTCP6|HTCP7|PPLATFORM|STORAGE|VOUCHER|XYC"
  - name: product_cate
    type: string
    phys: varchar(512)
    desc: "产品类型"
    topk: "CREDIT|STRONG|WEAKLY"
  - name: product_description
    type: string
    phys: text
    desc: "产品详细描述"
  - name: product_ref_num
    type: number
    phys: int(10)
    desc: "引用产品的平台数"
  - name: product_summary
    type: string
    phys: text
    desc: "产品概述"
  - name: project_code
    type: string
    phys: varchar(64)
    desc: "蜂搭平台项目编号"
  - name: project_config
    type: string
    phys: varchar(256)
    desc: "项目配置"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: transaction_structure
    type: string
    phys: varchar(1024)
    desc: "交易结构"
```
