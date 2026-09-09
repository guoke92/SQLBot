---
type: table
title: 协议迁移记录
page_key: argeement_migratory_record
belong: tables
domain: 基线
status: draft
anchors: [argeement_migratory_record]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 协议迁移记录

（基线页：31 字段，行数估计 35544。行语义/常用过滤待语义摄取增强。）

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
desc: 协议迁移记录
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: sign_mode
    type: string
    phys: varchar(20)
    desc: 签署模式
    dict: sign_mode
    topk: 01|02|03
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
  - name: agreement_name
    type: string
    phys: varchar(128)
    desc: 协议名称
  - name: agreement_no
    type: string
    phys: varchar(64)
    desc: 协议编号
  - name: agreement_path
    type: string
    phys: varchar(128)
    desc: 协议路径
  - name: agreement_type
    type: string
    phys: varchar(64)
    desc: 协议类型
    topk: BS_Auth|CFCA_Auth|CustPersonLicense|PrivacyPolicy
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
    topk: 0|1788084948672512001|1864558245919076353|1928325034167848961
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 13545235866|中建一局|于得生|于清山
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 产融客户id
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: effect_date
    type: temporal
    phys: date
    desc: 协议生效日
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: expire_date
    type: temporal
    phys: date
    desc: 失效时间
    group: expire_date_group, update_time_group
  - name: is_new
    type: string
    phys: varchar(10)
    desc: 是否新数据
    topk: no|yes
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(64)
    desc: 产品编码
    topk: ACFLOW|AMS|BEECREDIT|ORDER
  - name: pull_num
    type: number
    phys: int(10)
    desc: 拉取次数
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sign_date
    type: temporal
    phys: date
    desc: 签署日期
    group: expire_date_group
  - name: status
    type: number
    phys: int(10)
    desc: 状态
    topk: 0|1
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 0|1788084948672512001|1864558245919076353|1928325034167848961
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 13545235866|中建一局|于得生|于清山
```
