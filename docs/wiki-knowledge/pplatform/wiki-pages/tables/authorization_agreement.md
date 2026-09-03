---
type: table
title: 授权确认书表
page_key: authorization_agreement
domain: 基线
status: draft
anchors: [authorization_agreement]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 授权确认书表

（基线页：27 字段，行数估计 30268。行语义/常用过滤待语义摄取增强。）

```ground:table
table: authorization_agreement
database: lowcode_pplatform
desc: 授权确认书表
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
    topk: JHYL|LLS|QA2tiepai2|base
  - name: authed_status
    type: string
    phys: varchar(512)
    desc: 授权书认证状态
    topk: N|Y
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_type
    type: string
    phys: varchar(512)
    desc: 企业角色
    topk: CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER
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
  - name: creation_type
    type: string
    phys: varchar(32)
    desc: 创建类型
    topk: AUTO|COMPANY_MANAGER_CHANGE_CODE|CUST_BUILD_INIT
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: cust_manager_id
    type: number
    phys: bigint(20)
    desc: 企业管理员id
  - name: cust_manager_name
    type: string
    phys: varchar(256)
    desc: 客户管理员名称
  - name: cust_name
    type: string
    phys: varchar(128)
    desc: 企业名称
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
    phys: varchar(300)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: original_cust_id
    type: string
    phys: varchar(128)
    desc: 源系统custid
    topk: 1796784307050151938|1797504376757383169|1798257982988562434
  - name: platform_product_code
    type: string
    phys: varchar(128)
    desc: 平台产品id
    topk: ACFLOW|AMS|BEECREDIT|ORDER
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

- [[cust_company_info]]：authorization_agreement.cust_id → cust_company_info.id（write-flow:CustAuthAgreementDomainServiceTest.java，confirmed）
