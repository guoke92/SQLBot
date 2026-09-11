---
type: table
title: 微企链项目企业关联运营
page_key: wec_project_cust_operation_rel
domain: 基线
status: draft
anchors: [wec_project_cust_operation_rel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# 微企链项目企业关联运营

（基线页：31 字段，行数估计 2318。行语义/常用过滤待语义摄取增强。）

```ground:table
table: wec_project_cust_operation_rel
database: lowcode_pplatform
desc: 微企链项目企业关联运营
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
  - name: company_id
    type: string
    phys: varchar(64)
    desc: 微企链企业id
  - name: company_type
    type: string
    phys: varchar(64)
    desc: 微企链企业角色
    topk: ce|cpt
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1480444461854887938|1525044710953656322|1801438863791919106|1998571949021429761
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 刘宁|林彦湘|欧阳鹏飞|黄丽玉
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: op_contact_a
    type: string
    phys: varchar(64)
    desc: 运营对接人A
    topk: 267|271|293|321
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: 运营组别
    topk: 1|xxcc|可乐可口2|小微蜂组
  - name: op_contact_b
    type: string
    phys: varchar(400)
    desc: 运营对接人B
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: string
    phys: varchar(64)
    desc: 微企链项目id
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: 风控对接人A
    topk: 105|108|271|321
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: 风控组别
    topk: A1|可乐可口2|小微蜂组|组一
  - name: risk_control_contact_b
    type: string
    phys: varchar(400)
    desc: 风控对接人B
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: 置顶标识
    topk: 0
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1480444461854887938|1525044710953656322|1801438863791919106|1998571949021429761
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: huangliyu|linyanxiang|liuning|刘宁
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: 查验对接人
    topk: 141|305|321|454
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: 查验组别
    topk: 1组|3|可乐可口2|小微蜂组
  - name: wec_rel_id
    type: string
    phys: varchar(64)
    desc: 微企链关联关系id
```
