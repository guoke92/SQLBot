---
type: table
title: 项目运营文件管理
page_key: project_file_info
domain: 文件/附件/媒体
status: draft
anchors: [project_file_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---











project_file_info 是「项目运营文件管理」的元数据主表：登记项目下审批（approve）、审核（check）、整理（collate）、客户（cust）、其他（other）五类文件的标题与描述，文件实体仍存放在对象存储，本表只保留元数据与审批流程关联字段。它与 [[media_file]]（客户影像树）、[[attachment_info]]（表单模板附件）不是同一套存储，边界见 [[project_file]]、[[media]]、[[catg_id]]。

## 需求背景
本期语义分析未提供需求文档主张（reqdoc_claims 为空），业务定位与字段含义均来自库表与代码证据。

## 版本演进
v0 初版：字段语义、五个文件类型口径（[[project_file_type_cust]]、[[project_file_type_approve]]、[[project_file_type_check]]、[[project_file_type_collate]]、[[project_file_type_other]]）与分页查询规则 [[project_file_page_query]] 均来自本期证据；无 action=uncovered 的文档主张。

```ground:table
table: project_file_info
database: lowcode_pplatform
desc: 项目运营文件管理
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: file_type
    type: string
    phys: varchar(32)
    desc: 文件模块类型
    dict: file_type
    topk: "approve|check|collate|cust|other"
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
  - name: content
    type: string
    phys: varchar(500)
    desc: 描述
    topk: "1|10|11|123|2|22|222|2342342|3|3232424|4|5|6|7|8|9|aaa|描述1"
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
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 关联项目ID
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: title
    type: string
    phys: varchar(200)
    desc: 标题
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

关联：[[tenant_project]]、[[project_file]]、[[media_file]]。