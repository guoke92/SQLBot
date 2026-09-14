---
type: table
title: 资金方异常解析及建议主表
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
contract_version: "0.1"
belong: tables
---












本表沉淀资方侧报错的处理知识：以「产品 code + 对接方标识 + 报错关键字」三元组构成业务唯一键，向上游返回报错原因与建议处理方案。表内同时存在页面手工维护链路与 Excel 导入链路，两条链路共用同一唯一性约束 [[exception_check_before_save_unique]]。资方标识与产品 code 的跨域命名差异见 [[funding_party_mark]]；产品维度的取值分布见 [[exception_resolution_product_scope]]。

## 需求背景

- 导入是全量前置校验型：5 个必填列（产品 code / 对接方标识 / 资金方名称 / 报错关键字 / 建议处理方案）任一不通过即整批不落库，见 [[exception_import_all_or_nothing]] 与 [[exception_import_name_code_translation]]。
- 上游调用场景只按报错关键字做 contains 命中，不做模糊度控制，见 [[exception_provider_contains_match]]。
- 数据可见性统一由 `enable` 口径约束，见 [[exception_resolution_enable_y]]。

## 版本演进

v0 首次建立：字段语义取自语义分析 field_semantics（exception_no / funding_party_code / funding_party_name / error_keyword / error_reason / suggestion / file_path / product_code / enable）。语义分析未提供列类型，type 暂记为 `unknown`，待 v1 从 DDL 校准。删除行为为物理删除，`enable` 不承担软删职责，见 [[batch_delete_physical]]。

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
desc: 资金方异常解析及建议主表
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
    topk: "base"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
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
    topk: "abc|alipay|bob|bod|boscBeehive|cdrcb|cgb|cmbchina|czbank|default|hfbank|hsbc|icbc|icbcProjectLoan|lzbank|scb|szbank"
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
    topk: "ACFLOW|RVSFACTOR_PC"
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
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```