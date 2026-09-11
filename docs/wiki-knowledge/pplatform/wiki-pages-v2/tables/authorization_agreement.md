---
type: table
title: authorization_agreement（授权确认书表）
page_key: table.authorization_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权确认书表
  - 授权书记录表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---


`authorization_agreement` 存的是「谁授过权」的关系事实：按管理员（`cust_manager_id`，sys/SSO userId）维度记录其对企业（`cust_id`）在各产品上的授权状态。`authed_status='Y'` 即视为已授权，是免补签判定的核心输入（见 [[calibers/platform-level-authed]]）。它与 [[concepts/offline-electronic-auth]] 描述的「授权书这一份文件」生命周期不同，二者通过 `cust_id` 关联。

`platform_product_code='PLATFORM'` 表示平台级授权，是补签判定的唯一依据；具体业务产品行（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的 `Y` 表示存量系统已授权，用于免补签判定（见 [[concepts/platform-product-code]]）。记录的产生场景由 `creation_type` 承载：`AUTO`、`COMPANY_MANAGER_CHANGE_CODE`（管理员变更）、`CUST_BUILD_INIT`（建档）。`act_procinst_id` 为空时（简易认证无流程实例）不落表。

## 需求背景
企业授权按人（userid）维度判定，同一自然人在多家企业任职时只需一份平台级授权；企业管理员变更时，原管理员的全部授权记录需被禁用并同步把 `authed_status` 置 `N`，新管理员重新建/更新平台级授权记录。这要求一张既能表达产品维度、又能表达「授权人—企业」关系的记录表。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: authorization_agreement
database: lowcode_pplatform
desc: 授权确认书表
fields:
  - name: id
    type: number
    desc: 表主键
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
  - name: authed_status
    type: string
    desc: 授权书认证状态
  - name: code
    type: string
    desc: 编码
  - name: company_type
    type: string
    desc: 企业角色
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: creation_type
    type: string
    desc: 创建类型
  - name: cust_id
    type: number
    desc: 企业id
  - name: cust_manager_id
    type: number
    desc: 企业管理员id
  - name: cust_manager_name
    type: string
    desc: 客户管理员名称
  - name: cust_name
    type: string
    desc: 企业名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: original_cust_id
    type: string
    desc: 源系统custid
  - name: platform_product_code
    type: string
    desc: 平台产品id
  - name: remark
    type: string
    desc: remark
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

- [[cust_company_info]]：authorization_agreement.cust_id → cust_company_info.id（write-flow:CustAuthAgreementDomainServiceTest.java，confirmed）
```ground:field
table: authorization_agreement
fields:
  - field: authed_status
    meaning: "授权书认证状态：'Y'=已授权，'N'=未授权；DDL 默认 '0'，实测仅 N/Y 两值。平台级（platform_product_code='PLATFORM'）为 Y 即视为企业已完成授权"
    evidence: db
  - field: platform_product_code
    meaning: "授权所属产品编码；'PLATFORM' 为平台级授权书（代码常量 PLATFORM_PRODUCT_TYPE），其余为具体业务产品（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的存量授权"
    evidence: db
  - field: creation_type
    meaning: "授权书产生场景/创建类型。DB 实测 AUTO、COMPANY_MANAGER_CHANGE_CODE、CUST_BUILD_INIT；代码在管理员变更场景写入 AuthAgreementCreationTypeEnum.CHANGE_COMPANY_MANAGER.getDictKey()，建档场景写 CUST_BUILD_INIT"
    evidence: db
  - field: enable
    meaning: "记录有效标志；企业管理员发生变更时，原管理员的全部授权记录被置为 'N' 并同时把 authed_status 置 N"
    evidence: db
  - field: cust_manager_id
    meaning: "企业管理员用户 id（sys/SSO userId）；授权按人（userid）维度判定，同人多企业角色只需一份平台级授权"
    evidence: code
  - field: cust_id
    meaning: "产融侧企业 id（cust_company_info.id）"
    evidence: code
  - field: company_type
    meaning: "企业角色，一般单值（SUPPLIER/CORE/FINANCE/PROJECT_COMPANY…）；DB 存在 '[\"CORE\"]' 这类 JSON 数组形态异常值"
    evidence: db
  - field: original_cust_id
    meaning: "源系统 custId，仅存量迁移产生的授权记录有值"
    evidence: db
  - field: act_procinst_id
    meaning: "流程实例 ID；简易认证无流程实例，createAuthorizationAgreement 遇到空 actProcinstId 直接返回不落表"
    evidence: code
```