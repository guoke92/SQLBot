---
type: table
title: cust_company_survey_whitelist（问卷星活动白名单企业）
page_key: tables/cust_company_survey_whitelist
domain: 问卷
status: draft
aliases:
  - 问卷活动白名单
  - 白名单企业
  - wenjuan whitelist
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_whitelist
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---


# cust_company_survey_whitelist（问卷星活动白名单企业）

本表是[[concepts/wenjuan]]（问卷星活动）的准入名单：只有落在本表中且 `enable = 'Y'`（配合 `isParticipating(company_id)` 判定）的企业，才会在首页看到活动 UI。判定逻辑挂在 `WenjuanDisplayService.resolveHomeDisplay`、`getSurveyUrl`、`shouldStayOnHomeForGotoProduct` 上，口径明细见 [[calibers/wenjuan_whitelist_company]]。

本表字段极简，只有企业名称、逻辑有效标识与数据租户标识（实测为 LN1），说明它是一个运营维护型的名单表，不承载活动过程状态——过程状态在 [[tables/cust_company_survey_state]]。理解两者分工是排查「白名单已加但用户看不到活动」类问题的第一步。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。需要业务确认：白名单维护的操作入口与审批流程、企业名称变更后本表是否同步。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:table
table: cust_company_survey_whitelist
database: lowcode_pplatform
desc: 问卷星白名单企业
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
    desc: 企业id
  - name: company_name
    type: string
    desc: 企业名称
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
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: remark
    type: string
    desc: remark
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

相关页面：[[tables/cust_company_survey_state]]、[[concepts/wenjuan]]、[[calibers/wenjuan_whitelist_company]]、[[processes/wenjuan_home_display_scene]]。