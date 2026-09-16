---
type: table
title: 租户互通产品
page_key: tenant_interworking_product
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_interworking_product]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [interworking_product]
---

# 租户互通产品

INTERWORKING 产品的租户开通行，不要 JOIN 进 [[tenant_product]]。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[interworking_product]]

`id`, `enable`, `create_time`, `update_time`, `open_status`, `platform_product_code`, `scope`, `target_sys_channel`

### 未分窗

仍留表页，待代码证据划入场景：`max_financing_amount_flag`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `credit_measures`, `customer_group`, `db_tenant_code`, `logo_icon_url`, `max_financing_amount`, `max_financing_period`, `name`, `organization_id`, `platform_product_id`, `product_cate`, `product_description`, `product_summary`, `ref_tenant_interworking_product_platform_product`, `ref_tenant_interworking_product_tenant_setting_config`, `remark`, `scope_project`, `scope_role`, `tenant_id`, `transaction_structure`

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
desc: 租户互通产品
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "主键"
    roles: [query]
    group: always
    scenes: [interworking_product]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    roles: [query]
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    group: always
    scenes: [interworking_product]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [interworking_product]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [interworking_product]
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
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: "是否限额融资资金上限"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: open_status
    type: string
    phys: varchar(4)
    desc: "开通状态"
    dict: enable
    topk: "N|Y"
    labels: "N:未开通|Y:已开通"
    roles: [query]
    scenes: [interworking_product]
  - name: platform_product_code
    type: string
    phys: varchar(16)
    desc: "平台产品编码"
    topk: "AMS|HTCP1|HTCP13|HTCP14|HTCP15|HTCP18|HTCP19|HTCP2|HTCP5|HTCP6|HTCP7"
    roles: [query]
    scenes: [interworking_product]
  - name: scope
    type: string
    phys: varchar(8)
    desc: "适应范围标识"
    topk: "ALL|SOME"
    scenes: [interworking_product]
  - name: target_sys_channel
    type: string
    phys: varchar(64)
    desc: "目标系统渠道"
    scenes: [interworking_product]
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
    topk: "GREENTOWNAT|JHYL|base|hylg"
  - name: credit_measures
    type: string
    phys: varchar(256)
    desc: "增信措施"
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: "客户群体"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "ISOLATE_TAG_CJTZ|ISOLATE_TAG_GREENTOWNAT|ISOLATE_TAG_JHYL|ISOLATE_TAG_QLT|ISOLATE_TAG_hylg|ISOLATE_TAG_lygs|ISOLATE_TAG_xjt|ISOLATE_TAG_yccsfzjt|LN1|LNceshizuhu0113|beehive-scf.qhhrly.cn|mengniu|yunyingzhongtai"
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: "产品logo"
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: "融资金额上限"
    topk: "0|88888888|不限"
  - name: max_financing_period
    type: string
    phys: varchar(128)
    desc: "融资期限上限"
    topk: "1-3年|6|HTCP15"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: "平台产品id"
  - name: product_cate
    type: string
    phys: varchar(64)
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
  - name: ref_tenant_interworking_product_platform_product
    type: string
    phys: varchar(128)
    desc: "关联产品大类"
  - name: ref_tenant_interworking_product_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: "关联租户"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: scope_project
    type: string
    phys: longtext
    desc: "适用范围项目"
  - name: scope_role
    type: string
    phys: varchar(200)
    desc: "适用角色"
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "租户id"
  - name: transaction_structure
    type: string
    phys: text
    desc: "交易结构"
```
