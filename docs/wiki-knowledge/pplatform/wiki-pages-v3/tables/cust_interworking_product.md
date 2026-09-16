---
type: table
title: 企业互通产品开通
page_key: cust_interworking_product
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [cust_interworking_product]
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

# 企业互通产品开通

企业开通互通产品，`open_status` 用 [[cust_product_active]]。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[interworking_product]]

`id`, `enable`, `create_time`, `update_time`, `cust_id`, `open_status`, `platform_product_code`, `product_id`

### 未分窗

仍留表页，待代码证据划入场景：`agree_authorization_flag`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `agree_authorization_time`, `app_tenant_code`, `db_tenant_code`, `name`, `open_time`, `open_user`, `organization_id`, `ref_cust_interworking_product_cust_company_info`, `ref_cust_interworking_product_tenant_interworking_product`, `remark`, `tenant_id`

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
desc: 企业互通产品
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [interworking_product]
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
  - name: agree_authorization_flag
    type: string
    phys: varchar(2)
    desc: "是否同意授权"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    roles: [query]
    scenes: [interworking_product]
  - name: open_status
    type: string
    phys: varchar(16)
    desc: "开通状态"
    dict: cust_product_active
    topk: "OPENED"
    labels: "OPENED:已开通"
    roles: [query]
    scenes: [interworking_product]
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: "平台产品编码"
    topk: "AMS|HTCP1|HTCP13|HTCP14|HTCP2|HTCP5"
    roles: [query]
    scenes: [interworking_product]
  - name: product_id
    type: number
    phys: bigint(20)
    desc: "互通产品id"
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
  - name: agree_authorization_time
    type: temporal
    phys: datetime
    desc: "同意授权时间"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base|common"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "ISOLATE_TAG_CJTZ|ISOLATE_TAG_JHYL|ISOLATE_TAG_hylg|ISOLATE_TAG_lygs|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: open_time
    type: temporal
    phys: datetime
    desc: "开通时间"
  - name: open_user
    type: number
    phys: bigint(20)
    desc: "开通人"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: ref_cust_interworking_product_cust_company_info
    type: string
    phys: varchar(128)
    desc: "关联企业"
  - name: ref_cust_interworking_product_tenant_interworking_product
    type: string
    phys: varchar(128)
    desc: "关联互通产品"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "租户id"
```

```ground:relation
type: EQUI_JOIN
left: cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product
right: tenant_interworking_product.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustInterworkingProductDomainService.java
```
