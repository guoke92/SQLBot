---
type: table
title: 客户互通产品表（cust_interworking_product）
page_key: tables/cust_interworking_product
domain: 互通产品
status: draft
aliases: [cust_interworking_product, 客户互通产品表]
oid: 1
scope:
  databases: []
sources:
  - db:cust_interworking_product
  - code:CustProductActiveConstant
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


客户互通产品表记录客户维度的互通产品开通状态，是互通产品链路上「配置在前、状态在后」的状态一侧：配置见 [[tables/tenant_interworking_product]]，状态推进见 [[processes/interworking_product_open_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表需要回答「某客户是否已开通某互通产品」，并支撑开通/取消两类操作。

## 版本演进
- DB 对账值 OPENED 与代码常量 CustProductActiveConstant.OPENED 同名，但语义分析指出该常量未在代码枚举基线上覆盖本表取值，属代码与数据未完全对齐的遗留点，见 [[concepts/product_open_status]]。
- 本表未提供字段级明细（仅一条字段证据），字段清单待补。

```ground:table
table: cust_interworking_product
database: lowcode_pplatform
desc: 企业互通产品
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
  - name: agree_authorization_flag
    type: string
    desc: 是否同意授权
  - name: agree_authorization_time
    type: temporal
    desc: 同意授权时间
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
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
  - name: cust_id
    type: number
    desc: 企业id
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: open_time
    type: temporal
    desc: 开通时间
  - name: open_user
    type: number
    desc: 开通人
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_product_code
    type: string
    desc: 平台产品编码
  - name: product_id
    type: number
    desc: 互通产品id
  - name: ref_cust_interworking_product_cust_company_info
    type: string
    desc: 关联企业
  - name: ref_cust_interworking_product_tenant_interworking_product
    type: string
    desc: 关联互通产品
  - name: remark
    type: string
    desc: remark
  - name: tenant_id
    type: number
    desc: 租户id
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

- [[cust_company_info]]：cust_interworking_product.ref_cust_interworking_product_cust_company_info → cust_company_info.code（ref-convention:CustInterworkingProductDO.java，suggested）
- [[tenant_interworking_product]]：cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product → tenant_interworking_product.code（ref-convention:CustInterworkingProductDO.java，suggested）
