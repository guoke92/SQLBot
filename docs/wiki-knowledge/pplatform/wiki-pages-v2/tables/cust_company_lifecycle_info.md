---
type: table
title: 企业生命周期记录
page_key: cust_company_lifecycle_info
domain: 基线
status: draft
anchors: [cust_company_lifecycle_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# 企业生命周期记录

（基线页：23 字段，行数估计 71。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_company_lifecycle_info
database: lowcode_pplatform
desc: 企业生命周期记录
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
    topk: base
  - name: attach
    type: string
    phys: varchar(526)
    desc: 冻结附件路径集合
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1207485686830276611|1310118569410772993|1310119175595626498|1346751471598141442
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: chenkaiwen|liujingyun|liuning|liuning3
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
    topk: 四川卫利清环保科技有限公司|国内信用证测试供应商003|大西瓜供应商|宁的企业08051121
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: reason
    type: string
    phys: varchar(200)
    desc: 冻结原因
  - name: ref_cust_company_info
    type: string
    phys: varchar(30)
    desc: 关联企业code
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: type
    type: string
    phys: varchar(64)
    desc: 类型
    topk: FRZ|UNFRZ
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1207485686830276611|1310118569410772993|1310119175595626498|1346751471598141442
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: chenkaiwen|liujingyun|liuning|liuning3
```

## 关联表

- [[cust_company_info]]：cust_company_lifecycle_info.ref_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
