---
type: table
title: 客户接入秘钥信息
page_key: cust_access_secret
belong: tables
status: draft
anchors: [cust_access_secret]
sources: ['database_schema:lowcode_pplatform.cust_access_secret', 'code_path:CustSyncService.java:711']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_access_secret__channel, cust_access_secret__encry_type, cust_access_secret__enable,
  cust_access_secret__status_query_license_enabled]
---

# 客户接入秘钥信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_access_secret
database: lowcode_pplatform
desc: 客户接入秘钥信息
inactive: false
primary_key: [id]
grain: 租户渠道接入密钥，按 db_tenant_code+enable 查，不是企业主键
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
- name: channel
  type: string
  desc: 应用id
  dict: [trinasolar, tianma, yhkj, dahua, lls, sny_test, trinapower, dahua-test, app_jkny,
    ZTSJ, alipayAnt-test, eascs, alipayAnt, meituan, longteng, sny, hbjg, app_bosc_shtl,
    bgy]
- name: encry_type
  type: string
  desc: 加密类型
  dict: [rsa]
- name: pub_key
  type: string
  desc: 公钥
- name: pri_key
  type: string
  desc: 私钥
- name: password
  type: string
  desc: 密码
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
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
- name: key_num
  type: number
  desc: 密钥对
  nullable: false
- name: rel_lls_secret_id
  type: number
  desc: 关联平台密钥记录id
- name: status_query_license_enabled
  type: string
  desc: 建档状态查询是否返回营业执照并同步SFTP：Y-是 N-否
  dict: [N, Y]
  label: [否, 是]
default_filter:
  predicate: cust_access_secret.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustSyncService.java:711
```

## 页面链接

### 字典

- [[dicts/cust_access_secret__channel]]（`cust_access_secret.channel`）
- [[dicts/cust_access_secret__encry_type]]（`cust_access_secret.encry_type`）
- [[dicts/cust_access_secret__enable]]（`cust_access_secret.enable`）
- [[dicts/cust_access_secret__status_query_license_enabled]]（`cust_access_secret.status_query_license_enabled`）
