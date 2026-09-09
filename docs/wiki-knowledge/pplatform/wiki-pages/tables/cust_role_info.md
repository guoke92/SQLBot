---
type: table
title: 客户产品角色关联表
page_key: cust_role_info
belong: tables
domain: 基线
status: draft
anchors: [cust_role_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户产品角色关联表

（基线页：24 字段，行数估计 48236。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_role_info
database: lowcode_pplatform
desc: 客户产品角色关联表
inactive: false
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    roles: [query, result]
  - name: role_type
    type: string
    phys: varchar(512)
    desc: 角色类型
    topk: CORE|CORE_ADMIN|CORE_MANAGER|CORE_SUB
    roles: [query]
  - name: status
    type: string
    phys: varchar(64)
    desc: 状态
    dict: cust_status
    topk: ADD|EFFECT|FREEZE|WRITEOFF
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: QA2tiepai2|base|common|zlskscf
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
    topk: 2057088320256253954
  - name: platform_cust_id
    type: number
    phys: bigint(20)
    desc: 关联平台企业ID
  - name: ref_cust_auth_application
    type: string
    phys: varchar(128)
    desc: 应用客户角色
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户类型
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_auth_application]]：cust_role_info.ref_cust_auth_application → cust_auth_application.code（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_change_record]]：cust_role_info.ref_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_role_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustRoleInfoDO.java，suggested）
