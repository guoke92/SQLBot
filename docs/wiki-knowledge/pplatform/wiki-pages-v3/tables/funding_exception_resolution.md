---
type: table
title: 资金异常解析
page_key: funding_exception_resolution
domain: 资金规则与异常处理
status: draft
anchors: [funding_exception_resolution]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [funding_rules]
---

# 资金异常解析

唯一键产品+资方+关键字。查询要求 `enable='Y'`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[funding_rules]]

`id`, `enable`, `create_time`, `update_time`, `error_keyword`, `funding_party_code`, `product_code`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `error_reason`, `exception_no`, `file_path`, `funding_party_name`, `name`, `organization_id`, `remark`, `suggestion`

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
desc: 资金方异常解析及建议主表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [funding_rules]
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
    scenes: [funding_rules]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [funding_rules]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [funding_rules]
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
  - name: error_keyword
    type: string
    phys: varchar(256)
    desc: "异常关键字"
    roles: [query]
    scenes: [funding_rules]
  - name: funding_party_code
    type: string
    phys: varchar(64)
    desc: "资方编码"
    topk: "abc|alipay|bob|bod|boscBeehive|cdrcb|cgb|cmbchina|czbank|default|hfbank|hsbc|icbc|icbcProjectLoan|lzbank|scb|szbank"
    roles: [query]
    scenes: [funding_rules]
  - name: product_code
    type: string
    phys: varchar(32)
    desc: "产品编码"
    topk: "ACFLOW|RVSFACTOR_PC"
    roles: [query]
    scenes: [funding_rules]
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: error_reason
    type: string
    phys: text
    desc: "报错原因"
  - name: exception_no
    type: string
    phys: varchar(32)
    desc: "异常编号"
  - name: file_path
    type: string
    phys: text
    desc: "附件"
  - name: funding_party_name
    type: string
    phys: varchar(128)
    desc: "资金方名称"
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
  - name: suggestion
    type: string
    phys: text
    desc: "建议处理方案"
```
