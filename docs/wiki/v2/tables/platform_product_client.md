---
type: table
title: 平台产品端口配置
page_key: platform_product_client
belong: tables
status: draft
anchors: [platform_product_client]
sources: ['database_schema:lowcode_pplatform.platform_product_client']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [platform_product, platform_product_client__platform_product_id, platform_product_client__client_type,
  platform_product_client__status, platform_product_client__multiple_type, platform_product_client__wx_flag,
  platform_product_client__link_type]
---

# 平台产品端口配置

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: platform_product_client
database: lowcode_pplatform
desc: 平台产品端口配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: platform_product_id
  type: number
  desc: 平台产品id
  dict: ['6', '3', '2', '4', '5', '7', '8', '10']
- name: url
  type: string
  desc: 产品url
- name: client_type
  type: string
  desc: 客户端类型方式
  dict: [AMS, ORDER, RVSFACTOR_PC, BEECREDIT, ACFLOW, DEALER]
- name: status
  type: string
  desc: 启用状态
  dict: [Y]
- name: multiple_type
  type: string
  desc: 过滤类型
  dict: [default, FINANCE, SUPPLIER, CORE, DEALER, PLATFORM_OPERATOR_COMPANY, CORE_BRANCH,
    CORE_MANAGER, CORE_SUB, PROJECT_COMPANY]
- name: ext_config
  type: string
  desc: 其他配置信息
- name: wx_flag
  type: string
  desc: 是否小程序
  dict: [N, Y]
- name: link_type
  type: string
  desc: 链接类型(iframe/redirect/forward)
  dict: [iframe]
- name: enable
  type: string
  desc: enable
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: platform_product.id
right: platform_product_client.platform_product_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.platform_product_client.platform_product_id;database_profile:lowcode_pplatform.platform_product_client.platform_product_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: platform_product
  comment: 平台产品id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 8
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/platform_product]]

### 字典

- [[dicts/platform_product_client__platform_product_id]]（`platform_product_client.platform_product_id`）
- [[dicts/platform_product_client__client_type]]（`platform_product_client.client_type`）
- [[dicts/platform_product_client__status]]（`platform_product_client.status`）
- [[dicts/platform_product_client__multiple_type]]（`platform_product_client.multiple_type`）
- [[dicts/platform_product_client__wx_flag]]（`platform_product_client.wx_flag`）
- [[dicts/platform_product_client__link_type]]（`platform_product_client.link_type`）
