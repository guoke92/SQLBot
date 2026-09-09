---
type: table
title: 企业项目码输入记录
page_key: cust_project_code_record
belong: tables
domain: 基线
status: draft
anchors: [cust_project_code_record]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 企业项目码输入记录

（基线页：24 字段，行数估计 328。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_project_code_record
database: lowcode_pplatform
desc: 企业项目码输入记录
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
    topk: base|common|xyc.llschain.com
  - name: channel_code
    type: string
    phys: varchar(32)
    desc: 渠道码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: company_type
    type: string
    phys: varchar(200)
    desc: 企业角色
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
    topk: HKC|ISOLATE_TAG_HBCI|ISOLATE_TAG_LONGYANCHENGFA|ISOLATE_TAG_NAURA
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
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: status
    type: string
    phys: varchar(4)
    desc: 是否正确状态
    topk: N|Y
  - name: type
    type: string
    phys: varchar(32)
    desc: 类型
    topk: PC_BUILD|userCompanyRegister|产品中心|产品中心-企业认证成功
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
  - name: use_id
    type: number
    phys: bigint(20)
    desc: 用户id
```

## 关联表

- [[cust_company_info]]：cust_project_code_record.company_id → cust_company_info.id（write-flow:CustProjectRelEnhanceService.java，confirmed）
