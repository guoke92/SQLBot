---
type: table
title: 企业问卷状态
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
contract_version: "0.3"
belong: tables
scenes: [company_survey]
---

# 企业问卷状态

问卷活动主档。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_survey]]

`id`, `enable`, `create_time`, `update_time`, `first_visitor_lottery_shown`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `company_id`, `db_tenant_code`, `first_visit_time`, `first_visitor_lottery_shown_time`, `first_visitor_user_id`, `name`, `organization_id`, `remark`, `respondent`

```ground:table
table: cust_company_survey_state
database: lowcode_pplatform
desc: 企业问卷星活动状态
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [company_survey]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    group: always
    scenes: [company_survey]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [company_survey]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_survey]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: first_visitor_lottery_shown
    type: string
    phys: varchar(4)
    desc: "是否已展示首次访问抽奖"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    scenes: [company_survey]
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: company_id
    type: number
    phys: bigint(20)
    desc: "企业ID"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "LN1|all"
  - name: first_visit_time
    type: temporal
    phys: datetime
    desc: "首个用户首次访问时间"
  - name: first_visitor_lottery_shown_time
    type: temporal
    phys: datetime
    desc: "首个用户转盘展示时间"
  - name: first_visitor_user_id
    type: number
    phys: bigint(20)
    desc: "该企业首个进入产融首页的用户ID"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: respondent
    type: string
    phys: varchar(64)
    desc: "问卷星 respondent/source"
```
