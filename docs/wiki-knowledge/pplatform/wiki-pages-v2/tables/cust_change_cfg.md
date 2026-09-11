---
type: table
title: cust_change_cfg（客户变更项配置表）
page_key: table.cust_change_cfg
domain: 授权协议与电子授权
status: draft
aliases:
  - 客户变更项配置表
  - 变更项字典表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_cfg
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


`cust_change_cfg` 为 [[tables/cust_change_record]] 的 `alter_type_id` 提供语义：`item_code`（如 `UN0008`/`UN0012`/`UN0013`/`UN0015`/`UN0016`）是「变更项是否允许触发电子授权签署」这个白名单口径的比对值，见 [[calibers/change-scope-self-alter-items]]。

## 需求背景
变更项是配置化字典，授权签署白名单必须以编码而非 id 表达，才能在配置表数据演进时保持判定语义稳定。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
desc: 客户变更配置
fields:
  - name: cust_type
    type: string
    desc: 客户类型
    dict: cust_type
  - name: id
    type: number
    desc: 表主键
  - name: identify_style
    type: string
    desc: 认证方式
    dict: identify_style
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: client_type
    type: string
    desc: 端类型
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: data_desc
    type: string
    desc: 变更需要材料说明
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: head_company
    type: string
    desc: 是否总公司
  - name: item_code
    type: string
    desc: 变更项编码
  - name: name
    type: string
    desc: 名称
  - name: open_process
    type: string
    desc: 开启流程
  - name: oper_item
    type: string
    desc: 运营中台变更项
  - name: organization_id
    type: string
    desc: 机构编号
  - name: plat_item
    type: string
    desc: 平台变更项
  - name: remark
    type: string
    desc: remark
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

## 关联表

- [[cust_change_record]]：cust_change_cfg.id → cust_change_record.alter_type_id（read-flow:CustSyncEventProcessor.java，confirmed）
- [[cust_person_info]]：cust_change_cfg.code → cust_person_info.ref_cust_company_info（java-eq:CustCompanyInfoApplication.java，suggested）
- [[cust_project_rel]]：cust_change_cfg.id → cust_project_rel.product_id（write-flow:PlatFormMigratoryApplication.java，confirmed）
```ground:field
table: cust_change_cfg
fields:
  - field: item_code
    meaning: "变更项编码，如 UN0008/UN0012/UN0013/UN0015/UN0016"
    evidence: code
```