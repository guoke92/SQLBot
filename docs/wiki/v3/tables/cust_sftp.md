---
type: table
title: 客戶sftp信息
page_key: cust_sftp
belong: tables
status: draft
anchors: [cust_sftp]
sources: ['database_schema:lowcode_pplatform.cust_sftp', 'code_path:CustAccessApplication.java:490']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_sftp__enable, cust_sftp__channel]
---

# 客戶sftp信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_sftp
database: lowcode_pplatform
desc: 客戶sftp信息
inactive: false
primary_key: [id]
grain: 渠道 SFTP 配置，不是企业主档
name_anchors: [code, name, user_name]
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
- name: host
  type: string
  desc: 服务器地址IP地址
- name: port
  type: number
  desc: 端口
- name: user_name
  type: string
  desc: 登录用户名
- name: password
  type: string
  desc: 登录密码
- name: private_key
  type: string
  desc: 私钥
- name: private_key_pwd
  type: string
  desc: 私钥的密码
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
- name: channel
  type: string
  desc: 渠道
  dict: [dahua, app_jkny, app_bosc_shtl, ZTSJ, alipayAnt-test, longteng, tianma, alipayAnt,
    bgy, eascs, hbjg, sny_test, trinasolar, dahua-test, sny, meituan]
default_filter:
  predicate: cust_sftp.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustAccessApplication.java:490
```

## 页面链接

### 字典

- [[dicts/cust_sftp__enable]]（`cust_sftp.enable`）
- [[dicts/cust_sftp__channel]]（`cust_sftp.channel`）
