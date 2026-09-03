---
type: table
title: 调研答案表
page_key: cust_survey_answer
domain: 基线
status: draft
anchors: [cust_survey_answer]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 调研答案表

（基线页：25 字段，行数估计 284。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
desc: 调研答案表
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
  - name: answer_value
    type: string
    phys: varchar(512)
    desc: 选项明文，多选每个选项单独一行
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_id
    type: number
    phys: bigint(20)
    desc: 当前登录企业ID
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
    topk: all
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
  - name: other_text
    type: string
    phys: varchar(512)
    desc: 当选项为"其他"时，填写的文本内容
    topk: 1|hjhh|额温枪容量空间|饿啊讽德诵功
  - name: question_no
    type: number
    phys: int(10)
    desc: 题号（1~N）
    topk: 1|2|3|4
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: submit_time
    type: temporal
    phys: datetime
    desc: 提交时间
  - name: survey_code
    type: string
    phys: varchar(64)
    desc: 问卷code
    topk: XYL_2024_Q1
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
  - name: user_id
    type: number
    phys: bigint(20)
    desc: 当前登录用户ID
```
