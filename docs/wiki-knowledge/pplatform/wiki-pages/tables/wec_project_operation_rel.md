---
type: table
title: 微企链项目关联运营
page_key: wec_project_operation_rel
domain: 基线
status: draft
anchors: [wec_project_operation_rel]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 微企链项目关联运营

（基线页：41 字段，行数估计 409。行语义/常用过滤待语义摄取增强。）

```ground:table
table: wec_project_operation_rel
database: lowcode_pplatform
desc: 微企链项目关联运营
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
  - name: business_group
    type: string
    phys: varchar(100)
    desc: 关联业务部门
  - name: business_manager
    type: string
    phys: varchar(64)
    desc: 业务经理
    topk: AMS的需求|丛彦彦|刘宁|欧阳鹏飞
  - name: bussiness_project_relation
    type: string
    phys: varchar(100)
    desc: 运营项目归属
    topk: 111|AMS测试|宁的运营部门一|测试版
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1364399217692581890|1480444461854887938|1525044710953656322|1761948088379621378
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: chenkaiwen|liuning|刘宁|周录彬zhoulubin
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一
    topk: 1|532423433|532423434|532423435
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: 自定义字段三
    topk: 3|643543543543|qa_cf3_1786619291710|字段3
  - name: custom_field_two
    type: string
    phys: varchar(400)
    desc: 自定义字段二
    topk: 2|543543544|543543545|543543546
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: 首笔落地时间
    group: project_up_time_group
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: op_contact_a
    type: string
    phys: varchar(64)
    desc: 运营对接人A
    topk: 169|210|257|267
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: 运营组别
    topk: 1|小微蜂组|组十1|运营组别0123
  - name: op_contact_b
    type: string
    phys: varchar(400)
    desc: 运营对接人B
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_relation
    type: string
    phys: varchar(100)
    desc: 项目归属
  - name: project_tag
    type: string
    phys: varchar(150)
    desc: 项目标签
    topk: PRD|TEST
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: 风控对接人A
    topk: 116|141|271|321
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: 风控组别
    topk: 1|3|QA测试二组|zu1
  - name: risk_control_contact_b
    type: string
    phys: varchar(400)
    desc: 风控对接人B
  - name: solution_manager
    type: string
    phys: varchar(64)
    desc: 方案经理
    topk: 丛彦彦|岁测|张俊杰|管梓呈
  - name: text
    type: string
    phys: varchar(1000)
    desc: 备注
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: 置顶标识
    topk: 0
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1207485686830276611|1364399217692581890|1480444461854887938|1499638761616445441
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: chenkaiwen|huangliyu|linyanxiang|liuning
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: 查验对接人
    topk: 305|321|363|411
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: 查验组别
    topk: 1|1组|可乐可口2|小微蜂组
  - name: wec_project_id
    type: string
    phys: varchar(40)
    desc: 微企链项目id
  - name: wechat_audit_no
    type: string
    phys: varchar(40)
    desc: 企微审批编号
  - name: wechat_audit_pass_time
    type: temporal
    phys: datetime
    desc: 项目立项审批通过时间
```
