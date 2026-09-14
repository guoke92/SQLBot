---
type: table
title: 问卷星白名单企业
page_key: cust_company_survey_whitelist
domain: GP学习/问卷/企业画像
status: draft
anchors: [cust_company_survey_whitelist]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












白名单表决定哪些企业能参与问卷星活动：`isParticipating(companyId)` 以其为判定键，不在名单内时首页直接返回 `NONE`，`getSurveyUrl` 抛「企业不在白名单列表中！」。口径定义见 [[calibers/wenjuan_whitelist_enabled]]，规则见 [[rules/wenjuan_whitelist_participation]]。企业名称快照与 [[tables/cust_company_info]] 的 `name` 同源。

## 需求背景

活动投放采取「名单制 + 首用户可见」两层收窄：先由本表限定企业范围，再由 [[tables/cust_company_survey_state]] 的 claim 判定限定到企业首个访问用户（[[concepts/first_visitor]]）。实测 11 家，含「测试抽奖企业」系列测试数据，说明名单在投产前经历过测试配置。

## 版本演进

- 当前观测：11 行，`enable` 全为 `Y`，尚无失效样例可验证 `enable='N'` 的行为。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`。

```ground:table
table: cust_company_survey_whitelist
database: lowcode_pplatform
desc: 问卷星白名单企业
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: company_name
    type: string
    phys: varchar(128)
    desc: 企业名称
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "LN1"
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