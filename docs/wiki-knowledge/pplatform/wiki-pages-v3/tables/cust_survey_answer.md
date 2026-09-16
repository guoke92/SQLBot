---
type: table
title: 问卷答卷
page_key: cust_survey_answer
domain: GP学习/问卷/企业画像
status: draft
anchors: [cust_survey_answer]
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

# 问卷答卷

按 `(company_id, survey_code)` 查。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_survey]]

`id`, `enable`, `create_time`, `update_time`, `company_id`, `survey_code`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `answer_value`, `app_tenant_code`, `db_tenant_code`, `name`, `organization_id`, `other_text`, `question_no`, `remark`, `submit_time`, `user_id`

```ground:table
table: cust_survey_answer
database: lowcode_pplatform
desc: 调研答案表
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
  - name: company_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    roles: [query]
    scenes: [company_survey]
  - name: survey_code
    type: string
    phys: varchar(64)
    desc: "问卷编码"
    topk: "XYL_2024_Q1"
    roles: [query]
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
  - name: answer_value
    type: string
    phys: varchar(512)
    desc: "选项明文，多选每个选项单独一行"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "all"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: other_text
    type: string
    phys: varchar(512)
    desc: "当选项为\"其他\"时，填写的文本内容"
  - name: question_no
    type: number
    phys: int(10)
    desc: "题号（1~N）"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: submit_time
    type: temporal
    phys: datetime
    desc: "提交时间"
  - name: user_id
    type: number
    phys: bigint(20)
    desc: "当前登录用户ID"
```

```ground:relation
type: EQUI_JOIN
left: cust_survey_answer.company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:WenjuanController.java
```
