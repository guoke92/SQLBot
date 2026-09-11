---
type: table
title: cust_company_survey_state（企业问卷星活动状态）
page_key: tables/cust_company_survey_state
domain: 问卷
status: draft
aliases:
  - 问卷星活动状态表
  - 企业活动状态
  - first visitor state
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_state
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---


# cust_company_survey_state（企业问卷星活动状态）

本表以「企业」为单位记录[[concepts/wenjuan]]（问卷星活动，入口 `/cust-web/wenjuan`）的活动状态。核心字段是 `first_visit_time`（首个用户首次访问时间）与 `first_visitor_lottery_shown` / `first_visitor_lottery_shown_time`（首个用户转盘抽奖是否已展示及其时间，实测均为 Y）。这组字段支撑「[[concepts/first_visitor]]」判定：抽奖、指引与右下角问卷入口只对企业的首个访问用户开放。

`respondent` 字段是问卷星答卷标识，来自代码 `String.valueOf(companyId)`，用于调用问卷星开放接口查询完成态。请注意：本表只保存「谁第一个来、抽奖有没有展示过」这类企业级状态，**不保存答卷内容**——完成态是每次实时查询问卷星得到的，见 [[calibers/wenjuan_no_persist_completion]]。

状态字段的取值组合直接决定首页展示场景，其状态机见 [[processes/wenjuan_home_display_scene]]。表内 `db_tenant_code`（实测为 LN1/all）与 `enable`（实测均为 Y）承担租户与逻辑有效标识。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。需要业务补充：活动结束后 `cust_company_survey_state` 记录是保留还是清理、抽奖已展示后用户重复登录的展示预期。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:table
table: cust_company_survey_state
database: lowcode_pplatform
desc: 企业问卷星活动状态
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: company_id
    type: number
    desc: 企业ID
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: first_visit_time
    type: temporal
    desc: 首个用户首次访问时间
  - name: first_visitor_lottery_shown
    type: string
    desc: 首个用户转盘抽奖是否已展示 Y/N
  - name: first_visitor_lottery_shown_time
    type: temporal
    desc: 首个用户转盘展示时间
  - name: first_visitor_user_id
    type: number
    desc: 该企业首个进入产融首页的用户ID
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: remark
    type: string
    desc: remark
  - name: respondent
    type: string
    desc: 问卷星 respondent/source
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

相关页面：[[tables/cust_company_survey_whitelist]]、[[concepts/wenjuan]]、[[concepts/first_visitor]]、[[concepts/survey_completed]]、[[processes/wenjuan_home_display_scene]]、[[calibers/wenjuan_whitelist_company]]。