---
type: table
title: 建档推送运营记录表
page_key: cust_build_record
domain: 基线
status: draft
anchors: [cust_build_record]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 建档推送运营记录表

（基线页：27 字段，行数估计 18958。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_build_record
database: lowcode_pplatform
desc: 建档推送运营记录表
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
  - name: channel
    type: string
    phys: varchar(60)
    desc: 渠道
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
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业ID
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: electronic_auth_sign_status
    type: string
    phys: varchar(16)
    topk: PENDING|SIGNED
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
    desc: 联系人ID
  - name: plat_cust_id
    type: number
    phys: bigint(20)
    desc: 运营中台ID
  - name: plat_person_id
    type: number
    phys: bigint(20)
    desc: 运营中台ID
  - name: push_data
    type: string
    phys: varchar(1000)
    desc: 推送json
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: retry_status
    type: string
    phys: varchar(20)
    desc: 补偿重试状态：PENDING-待重试，RETRYING-重试中，SUCCESS-重试成功，FAILED-重试失败
  - name: return_data
    type: string
    phys: varchar(1000)
    desc: 返回data
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

- [[cust_company_info]]：cust_build_record.cust_id → cust_company_info.id（java-eq:OperCustFacade.java，suggested）
