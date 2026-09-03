---
type: table
title: 企业问卷星活动状态
page_key: cust_company_survey_state
domain: 基线
status: draft
anchors: [cust_company_survey_state]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 企业问卷星活动状态

（基线页：24 字段，行数估计 11。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_company_survey_state
database: lowcode_pplatform
desc: 企业问卷星活动状态
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
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
    topk: 00499a5efa5845948d731cd49ad8447c|125f6f8219634a58bd829d96a4b5dcec
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业ID
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1993860799612551169|2008459574226952194|2033379015458893826|2034240969483669505
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 13011590390|13574638494|14704055441|14750870832
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: LN1|all
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: first_visit_time
    type: temporal
    phys: datetime
    desc: 首个用户首次访问时间
  - name: first_visitor_lottery_shown
    type: string
    phys: varchar(4)
    desc: 首个用户转盘抽奖是否已展示 Y/N
    topk: Y
  - name: first_visitor_lottery_shown_time
    type: temporal
    phys: datetime
    desc: 首个用户转盘展示时间
  - name: first_visitor_user_id
    type: number
    phys: bigint(20)
    desc: 该企业首个进入产融首页的用户ID
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
  - name: respondent
    type: string
    phys: varchar(64)
    desc: 问卷星 respondent/source
    topk: 1993860367081840641|2054762388929851394|2058837800669777921|2059103360591134721
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1993860799612551169|2008459574226952194|2033379015458893826|2034240969483669505
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 13011590390|13574638494|14704055441|14750870832
```
