---
type: table
title: 客户产品角色关联表
page_key: cust_role_info
domain: 客户角色与端口
status: draft
anchors: [cust_role_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---











cust_role_info 是「客户角色与端口」主题的事实表：一条记录表示某个客户企业在某产品下持有的一个企业角色（端口）。角色编码 role_type 与平台产品端口表 [[platform_product_cust_role]] 的 company_type_code 共用值域，术语解释见 [[company_role]] 与 [[port]]。

## 需求背景

客户开通产品后需要被赋予相应的企业角色，平台据此决定其可见菜单与可执行业务。角色以“全量覆盖”的方式维护（见 [[role_full_overwrite]]）：先按企业 code 删除旧角色，再按 roleType 数组逐个插入，新增记录状态为 ADD，需要后续激活。角色的可用性由 status 生命周期（见 [[cust_role_status_machine]]）与 enable 逻辑标识共同决定，常用口径见 [[valid_cust_role]]、[[effect_cust_role]]。

## 字段说明

- id：表主键。
- code：角色编码，新增时通过 DataModelUtils.uuid() 生成，每次覆盖都会重新生成。
- role_type：企业角色编码，如 CORE、SUPPLIER、FINANCE；写入前会去除 JSON 引号。
- status：角色状态，取值与流转见 [[cust_role_status]] 与 [[cust_role_status_machine]]。
- ref_cust_company_info：关联客户企业编码，指向 cust_company_info.code，用于反查企业信息（relation_audit 判定 confirm）。
- ref_cust_auth_application：应用客户角色（关联客户开通产品），当前代码未直接使用，未发现实现级关联（reject，待确认）。
- platform_cust_id：关联平台企业 ID。
- db_tenant_code：数据租户标识，全量覆盖写入时取自关联企业。
- enable：逻辑启用标识（Y/N），查询时常用 enable='Y' 过滤。

与其他表的关联：ref_cust_company_info 与 cust_person_info.ref_cust_company_info 为共享键（同为企业的 code 值，derived，非直接外键 JOIN）；与 cust_change_record 的关联无直接查询证据（reject）。

## 版本演进

- v0（draft）：基于 db 字段语义与代码路径首次成页；列类型、role_type 带引号历史值均待后续核实与清洗。

```ground:table
table: cust_role_info
database: lowcode_pplatform
desc: 客户产品角色关联表
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
    dict: role_type
    topk: "\"CORE\"|\"SUPPLIER\"|CORE|CORE_ADMIN|CORE_MANAGER|CORE_SUB|CORPORATION_COMPANY|DEALER|FACTOR_COMPANY|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
    roles: [query]
  - name: status
    type: string
    phys: varchar(64)
    desc: 状态
    dict: cust_role_info__status
    topk: "ADD|EFFECT|FREEZE|WRITEOFF"
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
    topk: "QA2tiepai2|base|common|zlskscf"
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
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_auth_application]]：cust_role_info.ref_cust_auth_application → cust_auth_application.code（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_auth_application]]：cust_role_info.ref_cust_auth_application → cust_auth_application.id（db-index:ref_-naming，suggested）
- [[cust_change_record]]：cust_role_info.ref_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_role_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_company_info]]：cust_role_info.ref_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[cust_person_info]]：cust_role_info.ref_cust_company_info → cust_person_info.ref_cust_company_info（java-eq-same:AbstractSmsMessageService.java，suggested）
