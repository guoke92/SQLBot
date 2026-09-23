---
type: table
title: 企业信息配置表
page_key: cust_config_mapping
belong: tables
status: draft
anchors:
- cust_config_mapping
sources:
- database_schema:lowcode_pplatform.cust_config_mapping
- code_path:CustConfigMappingDaoImpl.java:48
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- cust_config_mapping__enable
---

# 企业信息配置表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_config_mapping
database: lowcode_pplatform
desc: 企业信息配置表
inactive: false
primary_key:
- id
grain: 内外渠道字段映射配置，无企业 FK
name_anchors:
- code
- name
- inner_code
- inner_name
- outer_code
- outer_name
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
- name: outer_channel
  type: string
  desc: 外部渠道
  dict:
  - ACFLOW
  - ORDER
  - SELF
  - OPS
- name: inner_code
  type: string
  desc: 内部编码
  dict:
  - CORE_FUNCTIONAL_DEPARTMENT
  - SUPPLIER
  - CORE
  - PLATFORM_OPREATOR_COMPANY
  - DEALER
  - CORE_MANAGER
  - CORE_BRANCH
  - PROJECT_COMPANY
  - FINANCE
  - CORE_SUB
  - A0007
  - A0002
  - A0037
  - HEAD_COMPANY_LEGAL
  - A0012
  - COMPANY_LEGAL
  - A0008
  - COMPANY
  - A0004
  - A0038
  - HEAD_COMPANY_LEGAL_CE_PERIOD
  - A0035
  - COMPANY_MANAGER_CE_PERIOD
  - A0011
  - COMPANY_AUTH_AGGREMENT
- name: inner_name
  type: string
  desc: 内部名称
- name: outer_code
  type: string
  desc: 外部编码
  dict:
  - CE
  - PROJ
  - SPY
  - CPT
  - OPE
  - A0004
  - A0037
  - UN0001
  - A0011
  - UN0014
  - A0002
  - UN0005
  - A0008
  - A0035
  - A0038
  - UN0002
  - A0012
  - UN0008
  - A0007
  - UN0011
- name: outer_name
  type: string
  desc: 外部名称
- name: type
  type: string
  desc: 类型
  dict:
  - COMPANY_TYPE_MAPPING
  - COMPANY_MEDIA
  - CHANGE_ITEM
- name: groups
  type: string
  desc: 分组
  dict:
  - BRANCH_COMPANY
  - HEAD_COMPANY
- name: enable
  type: string
  desc: enable
  dict:
  - Y
  - N
  label: [启用, 停用]
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
  predicate: cust_config_mapping.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustConfigMappingDaoImpl.java:48
```

## 页面链接

### 字典

- [[dicts/cust_config_mapping__outer_channel]]（`cust_config_mapping.outer_channel`）
- [[dicts/cust_config_mapping__inner_code]]（`cust_config_mapping.inner_code`）
- [[dicts/cust_config_mapping__outer_code]]（`cust_config_mapping.outer_code`）
- [[dicts/cust_config_mapping__type]]（`cust_config_mapping.type`）
- [[dicts/cust_config_mapping__groups]]（`cust_config_mapping.groups`）
- [[dicts/cust_config_mapping__enable]]（`cust_config_mapping.enable`）
