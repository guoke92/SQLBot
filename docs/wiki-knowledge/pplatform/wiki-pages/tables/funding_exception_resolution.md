---
type: table
title: 资金方异常解析及建议主表
page_key: funding_exception_resolution
domain: 基线
status: draft
anchors: [funding_exception_resolution]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 资金方异常解析及建议主表

（基线页：26 字段，行数估计 90。行语义/常用过滤待语义摄取增强。）

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
desc: 资金方异常解析及建议主表
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
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1207485686830276611|1291625791378644994|1438692652496736258|1480444461854887938
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: wangxianglian|刘宁|刘宁2|吴东洋
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: error_keyword
    type: string
    phys: varchar(256)
    desc: 报错关键字
  - name: error_reason
    type: string
    phys: text
    desc: 报错原因
  - name: exception_no
    type: string
    phys: varchar(32)
    desc: 异常编号
  - name: file_path
    type: string
    phys: text
    desc: 附件
  - name: funding_party_code
    type: string
    phys: varchar(64)
    desc: 对接方标识
    topk: abc|alipay|bob|bod
  - name: funding_party_name
    type: string
    phys: varchar(128)
    desc: 资金方名称
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_code
    type: string
    phys: varchar(32)
    desc: 产品code
    topk: ACFLOW|RVSFACTOR_PC
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: suggestion
    type: string
    phys: text
    desc: 建议处理方案
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1207485686830276611|1291625791378644994|1438692652496736258|1480444461854887938
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: wangxianglian|刘宁|刘宁2|吴东洋
```
