---
type: table
title: 企业互通产品
page_key: cust_interworking_product
belong: tables
domain: 基线
status: draft
anchors: [cust_interworking_product]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 企业互通产品

（基线页：29 字段，行数估计 267。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
desc: 企业互通产品
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: open_status
    type: string
    phys: varchar(16)
    desc: 开通状态
    dict: cust_auth_application__open_status
    topk: OPENED
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: agree_authorization_flag
    type: string
    phys: varchar(2)
    desc: 是否同意授权
    topk: N
  - name: agree_authorization_time
    type: temporal
    phys: datetime
    desc: 同意授权时间
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base|common
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1871372696502611970|1877554398443442177|1877642389362937857|1878981781704773633
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_CJTZ|ISOLATE_TAG_JHYL|ISOLATE_TAG_hylg|ISOLATE_TAG_lygs
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: AMS|AMS供应商|AMS金融机构|AMS项目公司
  - name: open_time
    type: temporal
    phys: datetime
    desc: 开通时间
  - name: open_user
    type: number
    phys: bigint(20)
    desc: 开通人
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: 平台产品编码
    topk: AMS|HTCP1|HTCP13|HTCP14
  - name: product_id
    type: number
    phys: bigint(20)
    desc: 互通产品id
  - name: ref_cust_interworking_product_cust_company_info
    type: string
    phys: varchar(128)
    desc: 关联企业
  - name: ref_cust_interworking_product_tenant_interworking_product
    type: string
    phys: varchar(128)
    desc: 关联互通产品
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 租户id
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1871372696502611970|1877554398443442177|1877642389362937857|1878981781704773633
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_company_info]]：cust_interworking_product.ref_cust_interworking_product_cust_company_info → cust_company_info.code（ref-convention:CustInterworkingProductDO.java，suggested）
- [[tenant_interworking_product]]：cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product → tenant_interworking_product.code（ref-convention:CustInterworkingProductDO.java，suggested）
