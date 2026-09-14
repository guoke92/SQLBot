---
type: table
title: 客户产品开通表
page_key: cust_auth_application
domain: 自动审核与工作流审核
status: draft
anchors: [cust_auth_application]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_auth_application 保存企业对平台产品的授权申请：`ref_cust_company_info` 按 [[ref_cust_company_info]] 约定关联企业编码，`platform_product_code` 标识申请的产品。企业的认证与建档过程见 [[cust_build_status_flow]]，授权申请是该过程在服务侧的业务结果之一。

## 需求背景
内部服务在产品开通链路上需要记录「哪家企业申请了哪个产品」，产品编码取值须与 [[tenant_product]] 保持一致；企业维度的关联一律以企业编码而非主键进行。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: cust_auth_application
database: lowcode_pplatform
desc: 客户产品开通表
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: open_status
    type: string
    phys: varchar(512)
    desc: 开通状态
    dict: cust_auth_application__open_status
    topk: "NOT_OPENED|OPENED|OPENING"
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
    topk: "LLS|QA2tiepai2|base|common|xyc.llschain.com"
  - name: application
    type: string
    phys: varchar(64)
    desc: 产品应用
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
  - name: cust_manager_id
    type: number
    phys: bigint(20)
    desc: 企业管理员
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: name
    type: string
    phys: varchar(128)
    desc: 产品名称
  - name: open_time
    type: temporal
    phys: datetime
    desc: 开通时间
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: 平台产品编码
    topk: "ACFLOW|BEECREDIT|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: ref_cust_auth_application_tenant_product
    type: string
    phys: varchar(128)
    desc: 关联应用
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户应用
  - name: ref_parent_company
    type: string
    phys: varchar(128)
    desc: 关联母公司
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

- [[cust_company_info]]：cust_auth_application.main_data_id → cust_company_info.id（write-flow:CustProductDomainService.java，confirmed）
- [[cust_company_info]]：cust_auth_application.ref_cust_company_info → cust_company_info.code（ref-convention:CustAuthApplicationDO.java，suggested）
- [[cust_company_info]]：cust_auth_application.ref_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[cust_company_info]]：cust_auth_application.ref_parent_company → cust_company_info.code（write-flow:CustProductDomainService.java，confirmed）
- [[cust_role_info]]：cust_auth_application.code → cust_role_info.ref_cust_auth_application（ref-convention:CustRoleInfoDO.java，suggested）
- [[tenant_product]]：cust_auth_application.platform_product_code → tenant_product.platform_product_code（copy:CustCompanyInfoApplication.java，suggested）
- [[tenant_product]]：cust_auth_application.ref_cust_auth_application_tenant_product → tenant_product.code（ref-convention:CustAuthApplicationDO.java，suggested）
- [[tenant_product]]：cust_auth_application.ref_cust_auth_application_tenant_product → tenant_product.id（db-index:ref_-naming，suggested）
