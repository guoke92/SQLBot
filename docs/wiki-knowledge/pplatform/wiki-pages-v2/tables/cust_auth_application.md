---
type: table
title: cust_auth_application 客户产品开通申请表
page_key: tables/cust_auth_application
domain: 平台产品配置
status: draft
aliases: [客户产品开通表, cust_auth_application]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:cust_auth_application.open_status
  - code:cust_auth_application.platform_product_code
  - code:cust_auth_application.ref_cust_company_info
  - code:cust_auth_application.ref_cust_auth_application_tenant_product
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


cust_auth_application 承载客户（企业）维度的产品开通申请与开通结果。它通过 `platform_product_code` 关联平台产品，通过 `ref_cust_company_info` 关联企业（[[tables/cust_company_info]]），并通过 `ref_cust_auth_application_tenant_product` 关联到租户产品记录（[[tables/tenant_product]]），从而把「租户开通」与「客户开通」两层关系串联起来。

`open_status` 驱动 [[processes/cust-product-open-status]] 状态机，也是 [[calibers/cust-open-product]] 口径的判定字段。

## 需求背景

语义分析未提供本表的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档。字段语义来自代码证据，状态取值与迁移见状态机页面。

```ground:table
table: cust_auth_application
database: lowcode_pplatform
desc: 客户产品开通表
fields:
  - name: id
    type: number
    desc: 表主键
  - name: open_status
    type: string
    desc: 开通状态
    dict: cust_auth_application__open_status
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
  - name: application
    type: string
    desc: 产品应用
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
  - name: cust_manager_id
    type: number
    desc: 企业管理员
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: main_data_id
    type: number
    desc: 主数据id
  - name: name
    type: string
    desc: 产品名称
  - name: open_time
    type: temporal
    desc: 开通时间
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_product_code
    type: string
    desc: 平台产品编码
  - name: ref_cust_auth_application_tenant_product
    type: string
    desc: 关联应用
  - name: ref_cust_company_info
    type: string
    desc: 客户应用
  - name: ref_parent_company
    type: string
    desc: 关联母公司
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

- [[cust_company_info]]：cust_auth_application.ref_parent_company → cust_company_info.code（write-flow:CustProductDomainService.java，confirmed）
- [[cust_role_info]]：cust_auth_application.code → cust_role_info.ref_cust_auth_application（ref-convention:CustRoleInfoDO.java，suggested）
- [[tenant_product]]：cust_auth_application.ref_cust_auth_application_tenant_product → tenant_product.code（ref-convention:CustAuthApplicationDO.java，suggested）
## 关联

- 状态机：[[processes/cust-product-open-status]]
- 状态术语辨析：[[concepts/openStatus]]
- 口径：[[calibers/cust-open-product]]
- 规则：[[rules/product-agreement-activate]]
- 企业表：[[tables/cust_company_info]]、[[tables/tenant_product]]