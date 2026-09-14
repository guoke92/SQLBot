---
type: table
title: 授权确认书表
page_key: authorization_agreement
domain: 授权协议与电子授权
status: draft
anchors: [authorization_agreement]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`authorization_agreement` 记录“企业管理员 → 产融平台”的授权确认关系，是企业开通业务前的一道准入凭证。每条记录通过 `cust_id` 指向 [[cust_company_info]]，通过 `cust_manager_id` 指向被授权/签署的企业管理员用户；`authed_status` 表示授权是否达成，`enable` 表示该记录当前是否有效。授权书按 `platform_product_code` 区分归属：`PLATFORM` 为平台级管理员授权书，其余为业务线产品码，口径见 [[platform_level_auth_agreement]]。

必须把它与业务协议文件区分开：产品协议、隐私政策、用户协议、CA 协议等协议实体走 [[argeement_migratory_record]]，二者不可互换，边界见 [[auth_agreement]]。

## 需求背景
平台在放行企业开通业务前，需要确认“当前企业管理员是否有权代表企业签署”。因此建档初始化、补授权、完善资料会写入/更新授权确认记录，状态判定口径为 [[auth_agreement_authed_y]] 与 [[auth_agreement_authed_n]]；管理员换人后旧授权必须整体作废，见 [[manager_change_invalidate_agreement]]。

## 版本演进
`creation_type` 同时存在 `CUST_BUILD_INIT`（建档初始化自动授权）、`AUTO`（自动）与 `COMPANY_MANAGER_CHANGE_CODE`（管理员变更），说明建档链路与管理员变更链路先后接入该表；`original_cust_id` 记录源系统 custId，说明该表承接了存量迁移数据。`company_type` 在 DB 中除标准 dictKey 外还存在 JSON 数组与拼写异常值，属历史写入遗留。

```ground:table
table: authorization_agreement
database: lowcode_pplatform
desc: 授权确认书表
fields:
  - name: authed_status
    type: string
    phys: varchar(512)
    desc: 授权书认证状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: company_type
    type: string
    phys: varchar(512)
    desc: 企业角色
    dict: company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FACTOR_COMPANY|FINANCE|PLATFORM_OPERATOR_COMPANY|PLATFORM_OPREATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|[\"CORE\"]|[\"FINANCE\"]|[\"PROJECT_COMPANY\"]"
  - name: creation_type
    type: string
    phys: varchar(32)
    desc: 创建类型
    dict: creation_type
    topk: "AUTO|COMPANY_MANAGER_CHANGE_CODE|CUST_BUILD_INIT"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
    topk: "JHYL|LLS|QA2tiepai2|base|common"
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
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业id
  - name: cust_manager_id
    type: number
    phys: bigint(20)
    desc: 企业管理员id
  - name: cust_manager_name
    type: string
    phys: varchar(256)
    desc: 客户管理员名称
  - name: cust_name
    type: string
    phys: varchar(128)
    desc: 企业名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: name
    type: string
    phys: varchar(300)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: original_cust_id
    type: string
    phys: varchar(128)
    desc: 源系统custid
  - name: platform_product_code
    type: string
    phys: varchar(128)
    desc: 平台产品id
    topk: "ACFLOW|AMS|BEECREDIT|ORDER|PLATFORM|RVSFACTOR|RVSFACTOR_PC|STORAGE|VOUCHER|pplatform"
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

- [[cust_company_info]]：authorization_agreement.cust_id → cust_company_info.id（write-flow:CustAuthAgreementDomainServiceTest.java，confirmed）
