---
type: table
title: 企业问卷星活动状态
page_key: cust_company_survey_state
domain: GP学习/问卷/企业画像
status: draft
anchors: [cust_company_survey_state]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表是问卷星活动的企业级状态：以 `company_id` 为键，记录该企业首个用户首次访问时间，以及首个用户转盘抽奖是否已展示。它是「谁是企业首个访问用户」这一判定的落点，但判定结果本身不落用户字段，只落一个展示标记，概念边界见 [[concepts/first_visitor]]。状态机见 [[processes/first_visitor_lottery_shown]]。

## 需求背景

活动的展示对象被收窄到「企业首个访问用户」：同一企业的其他用户首页不展示抽奖、指引与右下角入口（[[rules/first_visitor_only_ui]]）。为防止刷新重复展示转盘，前端动效结束后回调 `mark-lottery-shown`，由服务端把 `first_visitor_lottery_shown` 单向置 `Y`（[[rules/lottery_shown_idempotent]]）。整个链路读写前强制 `MetaDataThreadLocalConfig.setDbTenantCode("all")`（[[rules/wenjuan_all_tenant_fallback]]、[[calibers/wenjuan_all_tenant]]）。

答卷完成态不在本表：`syncAndResolve` 每次实时调问卷星查 `isSurveyCompleted`，接口注释明确「答卷状态不落库」（[[rules/survey_status_not_persisted]]）。

## 版本演进

- 当前观测：`first_visitor_lottery_shown` 11 行全为 `Y`，无 `N` 样本，`N` 仅由代码语义推断（见 [[enums/first_visitor_lottery_shown]]）。
- `db_tenant_code` 实测 `all`(10) 与 `LN1`(1) 并存，代码在 Wenjuan 链路强制写 `all`，该行属口径外历史/异常数据（[[enums/cust_company_survey_state_db_tenant_code]]）。
- 字段物理类型未在语义分析证据中给出，锚点块 `type` 记为 `unknown`；表结构证据在 `respondent` 之后出现截断，是否存在独立的「首个访问用户ID」列无法从现有证据确认（见 REVIEW）。

```ground:table
table: cust_company_survey_state
database: lowcode_pplatform
desc: 企业问卷星活动状态
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: first_visitor_lottery_shown
    type: string
    phys: varchar(4)
    desc: 首个用户转盘抽奖是否已展示 Y/N
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
    topk: "base"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 企业ID
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
    topk: "LN1|all"
  - name: first_visit_time
    type: temporal
    phys: datetime
    desc: 首个用户首次访问时间
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