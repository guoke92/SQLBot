---
type: table
title: 客户操作运营变更记录
page_key: cust_oper_change_record
belong: tables
domain: 基线
status: draft
anchors: [cust_oper_change_record]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户操作运营变更记录

（基线页：32 字段，行数估计 4008。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_oper_change_record
database: lowcode_pplatform
desc: 客户操作运营变更记录
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
  - name: after_operator_id
    type: string
    phys: varchar(64)
    desc: 变更后运营人员ID
  - name: after_operator_name
    type: string
    phys: varchar(128)
    desc: 变更后运营人员姓名
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: asset_id
    type: string
    phys: varchar(64)
    desc: 资产id
  - name: asset_no
    type: string
    phys: varchar(64)
    desc: 资产编号
  - name: before_operator_id
    type: string
    phys: varchar(64)
    desc: 变更前运营人员ID
  - name: before_operator_name
    type: string
    phys: varchar(128)
    desc: 变更前运营人员姓名
  - name: change_reason
    type: string
    phys: varchar(256)
    desc: 变更原因
    topk: 企业变更回调运营人员变更|手动变更运营人员|批量变更运营人员|资产审核同步
  - name: change_type
    type: string
    phys: varchar(30)
    desc: 变更类型
    topk: ASSET_AUDIT_SYNC|BATCH|CUST_CHANGE_CALLBACK|MANUAL
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_code
    type: string
    phys: varchar(60)
    desc: 企业编号
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业ID
  - name: company_name
    type: string
    phys: varchar(128)
    desc: 企业名称
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1346751471598141442|1364399217692581890|1397053042238709762|1480444461854887938
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: huangliyu|lijingjin|liuning|liuning4
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: person_id
    type: number
    phys: bigint(20)
    desc: 企业联系人id
  - name: person_name
    type: string
    phys: varchar(128)
    desc: 联系人姓名
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: source_system
    type: string
    phys: varchar(64)
    desc: 来源系统
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1346751471598141442|1364399217692581890|1397053042238709762|1480444461854887938
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: huangliyu|lijingjin|liuning|liuning4
```
