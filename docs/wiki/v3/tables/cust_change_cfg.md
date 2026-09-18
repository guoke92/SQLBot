---
type: table
title: 客户变更配置
page_key: cust_change_cfg
belong: tables
status: draft
anchors: [cust_change_cfg]
sources: ['database_schema:lowcode_pplatform.cust_change_cfg', 'code_path:CustCompanyInfoApplication.java:4320']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_change_record, cust_change_cfg__cust_type, cust_change_cfg__identify_style,
  cust_change_cfg__head_company, cust_change_cfg__open_process, cust_change_cfg__item_code,
  cust_change_cfg__enable, cust_change_cfg__client_type]
---

# 客户变更配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
desc: 客户变更配置
inactive: false
primary_key: [id]
grain: 变更项配置（按认证方式/客户类型查，不是企业主档）
name_anchors: [code, name, item_code]
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
- name: plat_item
  type: string
  desc: 平台变更项
- name: oper_item
  type: string
  desc: 运营中台变更项
- name: data_desc
  type: string
  desc: 变更需要材料说明
- name: cust_type
  type: string
  desc: 客户类型
  dict: ['2', '1', '3']
  label: [企业客户, 个人客户, 运营方企业客户]
- name: identify_style
  type: string
  desc: 认证方式
  dict: [INVITE, INVITE_AGW, SELF, SIMPLE]
  label: [邀请认证-客户录入, 邀请认证-内管录入, 自主认证, 简易认证]
- name: head_company
  type: string
  desc: 是否总公司
  dict: [N, Y]
- name: open_process
  type: string
  desc: 开启流程
  dict: [N, Y]
- name: item_code
  type: string
  desc: 变更项编码
  dict: [UN0001, UN0009, UN0003, UN0002, UN0004, UN0015, UN0013, UN0012, UN0014, UN0005,
    UN0008, UN0007, UN0016, UN0011, UN0006, UN0010]
  label: [企业信息变更, 增加企业角色, 法定代表人手机号码变更, 法定代表人变更, 法定代表人证件有效期变更, 企业管理员邮箱期变更, 企业管理员手机号变更,
    企业管理员变更, 企业管理员证件有效期变更, 总公司法定代表人变更, 企业授权书, 总公司法定代表人证件有效期变更, 总公司变分公司, 总公司企业信息变更,
    总公司法定代表人手机号变更, 重新建档]
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
- name: client_type
  type: string
  desc: 端类型
  dict: [AGW, ACCOUNT_PRODUCT]
  label: [内管, 客户端]
default_filter:
  predicate: cust_change_cfg.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCompanyInfoApplication.java:4320
```

## 页面链接

### 关联表

- [[tables/cust_change_record]]

### 字典

- [[dicts/cust_change_cfg__cust_type]]（`cust_change_cfg.cust_type`）
- [[dicts/cust_change_cfg__identify_style]]（`cust_change_cfg.identify_style`）
- [[dicts/cust_change_cfg__head_company]]（`cust_change_cfg.head_company`）
- [[dicts/cust_change_cfg__open_process]]（`cust_change_cfg.open_process`）
- [[dicts/cust_change_cfg__item_code]]（`cust_change_cfg.item_code`）
- [[dicts/cust_change_cfg__enable]]（`cust_change_cfg.enable`）
- [[dicts/cust_change_cfg__client_type]]（`cust_change_cfg.client_type`）
