---
type: table
title: 企业互通产品
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
contract_version: "0.1"
belong: tables
---












`cust_interworking_product` 记录客户维度的互通产品开通情况，是 [[interworking_product_term]] 在客户侧的落库表。开通状态使用另一套取值 `OPENED/OPENING/NOT_OPENED`（CustProductActiveConstant），与租户侧 ProductOpenStatusEnum 的 N/P/Y 不通用，口径见 [[cust_interworking_product_opened]]，两端对照见 [[cust_product_active_constant]]。

## 需求背景
语义分析未附带需求文档锚点，依据 DB 与代码证据归纳：客户侧互通产品开通需要"带客户确认 forams"的中间态，故状态集合与租户侧不同。

## 版本演进
语义分析未记录该表的版本演进；DB 实测仅见 OPENED，其余两态由常量类定义。

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
desc: 企业互通产品
fields:
  - name: agree_authorization_flag
    type: string
    phys: varchar(2)
    desc: 是否同意授权
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
  - name: agree_authorization_time
    type: temporal
    phys: datetime
    desc: 同意授权时间
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base|common"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
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
    topk: "ISOLATE_TAG_CJTZ|ISOLATE_TAG_JHYL|ISOLATE_TAG_hylg|ISOLATE_TAG_lygs|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: open_status
    type: string
    phys: varchar(16)
    desc: 开通状态
    topk: "OPENED"
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
    topk: "AMS|HTCP1|HTCP13|HTCP14|HTCP2|HTCP5"
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
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_company_info]]：cust_interworking_product.ref_cust_interworking_product_cust_company_info → cust_company_info.code（ref-convention:CustInterworkingProductDO.java，suggested）
- [[cust_company_info]]：cust_interworking_product.ref_cust_interworking_product_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[tenant_interworking_product]]：cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product → tenant_interworking_product.code（ref-convention:CustInterworkingProductDO.java，suggested）
- [[tenant_interworking_product]]：cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product → tenant_interworking_product.id（db-index:ref_-naming，suggested）
