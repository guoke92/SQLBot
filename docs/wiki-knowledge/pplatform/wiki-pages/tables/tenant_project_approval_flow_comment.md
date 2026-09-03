---
type: table
title: 租户项目审批备注信息
page_key: tenant_project_approval_flow_comment
domain: 基线
status: draft
anchors: [tenant_project_approval_flow_comment]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户项目审批备注信息

（基线页：21 字段，行数估计 65。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_project_approval_flow_comment
database: lowcode_pplatform
desc: 租户项目审批备注信息
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
  - name: cc_user_id
    type: string
    phys: varchar(500)
    desc: 抄送相关人员
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: content
    type: string
    phys: varchar(2048)
    desc: 备注内容
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1534087161817419777|1761948088379621378|1801438863791919106|1998571949021429761
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: 刘倍材|刘宁|林彦湘|陈凯文
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_szbank|LN1|beehive-scf.qhhrly.cn
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
  - name: ref_tenant_project_approval_flow_comment_approval
    type: string
    phys: varchar(128)
    desc: 关联项目审批
    topk: 0b913987d10e416c83bbc4810153db74|23099f85ba3e478b95eeba5b4262de36
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1534087161817419777|1761948088379621378|1801438863791919106|1998571949021429761
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: 刘倍材|刘宁|林彦湘|陈凯文
```
