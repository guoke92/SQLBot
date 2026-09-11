---
type: table
title: 租户互通产品表（tenant_interworking_product）
page_key: tables/tenant_interworking_product
domain: 互通产品
status: draft
aliases: [tenant_interworking_product, 租户互通产品表, 互通产品]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_interworking_product
  - code:TenantInterworkingProductApplication
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


租户互通产品表登记租户级互通产品的配置，除融资口径外还承载业务描述型字段（增信措施、客户群体）。与 [[tables/cust_interworking_product]] 的客户级开通状态形成「配置表—状态表」的配对关系，状态推进见 [[processes/interworking_product_open_status]]。本表同时出现逻辑租户标识与数据租户标识两列，见 [[concepts/logical_vs_db_tenant_code]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，本表要解决的是按租户描述互通产品的业务属性（增信措施、客户群体、融资上下限）并控制其启用。

## 版本演进
- credit_measures、customer_group 的 DB 实测值包含 HTCP15/ddd/sdsd 等疑似测试值，与「共同债务人增信、差额补足」「供应商、金融机构、项目公司」等业务用语混存，属自由文本字段的典型历史形态。
- max_financing_period 实测为「1-3年」这类区间文本，与 [[tables/tenant_product]] 同名字段的数值形态不同，见 [[calibers/financing_period_cap]]。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
desc: 租户互通产品
fields:
  - name: id
    type: number
    desc: 表主键
  - name: open_status
    type: string
    desc: 产品开通状态
    dict: tenant_interworking_product__open_status
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
  - name: credit_measures
    type: string
    desc: 增信措施
  - name: customer_group
    type: string
    desc: 客户群体
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: logo_icon_url
    type: string
    desc: 产品logo
  - name: max_financing_amount
    type: string
    desc: 融资金额上限
  - name: max_financing_amount_flag
    type: string
    desc: 是否限额融资资金上限
  - name: max_financing_period
    type: string
    desc: 融资期限上限
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_product_code
    type: string
    desc: 平台产品编号
  - name: platform_product_id
    type: number
    desc: 平台产品id
  - name: product_cate
    type: string
    desc: 产品类型
  - name: product_description
    type: string
    desc: 产品详细描述
  - name: product_summary
    type: string
    desc: 产品概述
  - name: ref_tenant_interworking_product_platform_product
    type: string
    desc: 关联产品大类
  - name: ref_tenant_interworking_product_tenant_setting_config
    type: string
    desc: 关联租户
  - name: remark
    type: string
    desc: remark
  - name: scope
    type: string
    desc: 适应范围标识
  - name: scope_project
    type: string
    desc: 适用范围项目
  - name: scope_role
    type: string
    desc: 适用角色
  - name: target_sys_channel
    type: string
    desc: 目标系统ssochannel
  - name: tenant_id
    type: number
    desc: 租户id
  - name: transaction_structure
    type: string
    desc: 交易结构
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

- [[cust_interworking_product]]：tenant_interworking_product.code → cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product（ref-convention:CustInterworkingProductDO.java，suggested）
- [[platform_product]]：tenant_interworking_product.ref_tenant_interworking_product_platform_product → platform_product.code（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_interworking_project]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_setting_config]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantInterworkingProductDO.java，suggested）
