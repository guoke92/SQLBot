---
type: table
title: 客户快捷入口配置
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
contract_version: "0.1"
belong: tables
---















# 客户快捷入口配置

（基线页：23 字段，行数估计 21。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_customized_product
database: lowcode_pplatform
desc: 客户快捷入口配置
fields:
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base|dsjx"
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
    topk: "LN1|beehive-scf.qhhrly.cn|dsjx"
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: 图标
  - name: name
    type: string
    phys: varchar(128)
    desc: 产品名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_cust_customized_product_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户关联自定义产品配置
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
  - name: url
    type: string
    phys: varchar(512)
    desc: 跳转链接
  - name: view_order
    type: number
    phys: int(10)
    desc: 显示顺序
```

## 关联表

- [[cust_company_info]]：cust_customized_product.ref_cust_customized_product_cust_company_info → cust_company_info.code（ref-convention:CustCustomizedProductDO.java，suggested）
- [[cust_company_info]]：cust_customized_product.ref_cust_customized_product_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[platform_product]]：cust_customized_product.logo_icon_url → platform_product.logo_icon_url（copy:CustGeneralProductApplication.java，suggested）
