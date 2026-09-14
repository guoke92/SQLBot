---
type: table
title: 客户产品开通配置
page_key: cust_auth_application_config
domain: 自动审核与工作流审核
status: draft
anchors: [cust_auth_application_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 客户产品开通配置

（基线页：24 字段，行数估计 0。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_auth_application_config
database: lowcode_pplatform
desc: 客户产品开通配置
fields:
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
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: needs_company_type_configuration
    type: string
    phys: varchar(512)
    desc: 是否区分企业
  - name: needs_product_agreement_configuration
    type: string
    phys: varchar(512)
    desc: 是否需要产品协议
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_protocol_agreement
    type: string
    phys: varchar(512)
    desc: 产品协议
  - name: product_sign_mode
    type: string
    phys: varchar(512)
    desc: 产品协议签署方式
  - name: ref_cust_auth_application_config_cust_auth_application
    type: string
    phys: varchar(128)
    desc: 客户产品开通
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
```

## 关联表

- [[cust_auth_application]]：cust_auth_application_config.ref_cust_auth_application_config_cust_auth_application → cust_auth_application.id（db-index:ref_-naming，suggested）
