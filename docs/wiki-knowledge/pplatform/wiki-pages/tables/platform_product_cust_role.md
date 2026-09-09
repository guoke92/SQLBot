---
type: table
title: 平台产品企业角色
page_key: platform_product_cust_role
belong: tables
domain: 基线
status: draft
anchors: [platform_product_cust_role]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 平台产品企业角色

（基线页：21 字段，行数估计 57。行语义/常用过滤待语义摄取增强。）

```ground:table
table: platform_product_cust_role
database: lowcode_pplatform
desc: 平台产品企业角色
inactive: false
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
  - name: company_type_code
    type: string
    phys: varchar(32)
    desc: 企业角色编码
    topk: CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER
  - name: company_type_name
    type: string
    phys: varchar(128)
    desc: 企业角色名称
    topk: 供应商|平台运营方|核心企业|核心企业管理机构
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: 产融平台|供票|供票QA|保理易融
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_code
    type: string
    phys: varchar(128)
    desc: 产品编码
    topk: ACCOUNT_PRODUCT|ACFLOW|AMS|BEECREDIT
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
