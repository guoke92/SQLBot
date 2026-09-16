---
type: table
title: GP 学习海报日志
page_key: gpt_learn_poster_log
domain: GP学习/问卷/企业画像
status: draft
anchors: [gpt_learn_poster_log]
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

# GP 学习海报日志

`company_id` → 企业 id。弹出门闸要求企业角色 FINANCE。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_survey]]

`id`, `enable`, `create_time`, `update_time`, `click_time`, `company_id`, `popup_time`, `user_id`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `company_name`, `db_tenant_code`, `name`, `organization_id`, `remark`, `user_name`

```ground:table
table: gpt_learn_poster_log
database: lowcode_pplatform
desc: 智能审核引流卡片埋点记录
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
    roles: [query]
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
  - name: click_time
    type: temporal
    phys: datetime
    desc: "点击时间"
    scenes: [company_survey]
  - name: company_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    roles: [query]
    scenes: [company_survey]
  - name: popup_time
    type: temporal
    phys: datetime
    desc: "弹出时间"
    scenes: [company_survey]
  - name: user_id
    type: number
    phys: bigint(20)
    desc: "用户id"
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
  - name: company_name
    type: string
    phys: varchar(128)
    desc: "企业名称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "beehive-scf.qhhrly.cn"
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
  - name: user_name
    type: string
    phys: varchar(64)
    desc: "用户名"
```

```ground:relation
type: EQUI_JOIN
left: gpt_learn_poster_log.company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:GptLearnService.java
```
