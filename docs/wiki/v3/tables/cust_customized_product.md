---
type: table
title: 客户快捷入口配置
page_key: cust_customized_product
belong: tables
status: draft
anchors: [cust_customized_product]
sources: ['database_schema:lowcode_pplatform.cust_customized_product', 'code_path:CustCustomizedProductDaoImpl.java:24']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_interworking_product, cust_project_rel, cust_customized_product__code,
  cust_customized_product__enable]
---

# 客户快捷入口配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_customized_product
database: lowcode_pplatform
desc: 客户快捷入口配置
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
  dict: [16d3c0b5af534650a04c091afdf7ecf4, 1610216e61e34e6bb6de7e6edf21efda, 657438ff3af74b9997a374a203f73055,
    1ecbca6d91da4711be24dda5df18d2c5, d019609761a0448581b66902c82da564, 5ee6cb2419774bc9984050a71f1d16da,
    b68c0f6474ae496683cd872299fda110, 8f2aa3a0d4b64a389bf076468b756d29, 41e96e8bd7914d2390d1c485bd6243e4,
    9b849d76eda548d693f58ed2da03ea72, 1ab1a54939ed445c8bcb7a0ee8d22077, dc26f54628524fb498e39256122be054,
    abc9fc960e124cd79acf47f372778964, e42929b50ffd4391a4de6da8d5323737, 22ca980e2a5c41b589fb8c7959d16e59,
    658138dc149d4361a8ed9785a03efaff, c4307aec51cc47dea2104890b6e8eef0, 2867a221ed0d4f65b4decbd99b199d05,
    e024d5e16a314577a4a4bb9b51229457, 3f659e407e744430ba36fab0934f8a92, f8e0f25e1e804362bed17d422956ed7b,
    bcfee01811bc43f29fcd038583318f9c, 0627da4dc89b4a0b8a53a18f6a8dfcb9, 1a928de05b4e45f9929b6ed202ed238a,
    86d9d00400d84d04ac43e0b6f3fd22a0]
- name: name
  type: string
  desc: 产品名称
- name: cust_id
  type: number
  desc: 企业id
- name: url
  type: string
  desc: 跳转链接
- name: logo_icon_url
  type: string
  desc: 图标
- name: view_order
  type: number
  desc: 显示顺序
- name: ref_cust_customized_product_cust_company_info
  type: string
  desc: 客户关联自定义产品配置
- name: enable
  type: string
  desc: enable
  dict: [Y]
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
default_filter:
  predicate: cust_customized_product.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCustomizedProductDaoImpl.java:24
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_customized_product.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCustomizedProductDaoImpl.java:25
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 15
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 定制产品按企业主键 cust_id，不是 ref_cust_customized_product_cust_company_info。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_customized_product.ref_cust_customized_product_cust_company_info
cardinality: one_to_many
trust: disputed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_customized_product.ref_cust_customized_product_cust_company_info;database_profile:lowcode_pplatform.cust_customized_product.ref_cust_customized_product_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 客户关联自定义产品配置
overlap:
  probed: true
  sample_size: 0
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
sides:
- {source: l1_code, left: cust_company_info.id, right: cust_customized_product.cust_id,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_customized_product.ref_cust_customized_product_cust_company_info,
  trust: proposed}
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_interworking_product]]
- [[tables/cust_project_rel]]

### 字典

- [[dicts/cust_customized_product__code]]（`cust_customized_product.code`）
- [[dicts/cust_customized_product__enable]]（`cust_customized_product.enable`）
