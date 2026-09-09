---
type: table
title: 客户产品开通表
page_key: cust_auth_application
belong: tables
domain: 基线
status: draft
anchors: [cust_auth_application]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户产品开通表

（基线页：27 字段，行数估计 26226。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_auth_application
database: lowcode_pplatform
desc: 客户产品开通表
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: open_status
    type: string
    phys: varchar(512)
    desc: 开通状态
    dict: cust_auth_application__open_status
    topk: NOT_OPENED|OPENED|OPENING
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
    topk: LLS|QA2tiepai2|base|common
  - name: application
    type: string
    phys: varchar(64)
    desc: 产品应用
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_manager_id
    type: number
    phys: bigint(20)
    desc: 企业管理员
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: name
    type: string
    phys: varchar(128)
    desc: 产品名称
  - name: open_time
    type: temporal
    phys: datetime
    desc: 开通时间
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: 平台产品编码
    topk: ACFLOW|BEECREDIT|DRAFT|DRAFTQA
  - name: ref_cust_auth_application_tenant_product
    type: string
    phys: varchar(128)
    desc: 关联应用
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户应用
  - name: ref_parent_company
    type: string
    phys: varchar(128)
    desc: 关联母公司
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
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_company_info]]：cust_auth_application.ref_parent_company → cust_company_info.code（write-flow:CustProductDomainService.java，confirmed）
- [[cust_role_info]]：cust_auth_application.code → cust_role_info.ref_cust_auth_application（ref-convention:CustRoleInfoDO.java，suggested）
- [[tenant_product]]：cust_auth_application.ref_cust_auth_application_tenant_product → tenant_product.code（ref-convention:CustAuthApplicationDO.java，suggested）
