---
type: table
title: cust_company_info（企业主数据表）
page_key: table.cust_company_info
domain: 平台内部服务对接
status: draft
aliases:
  - cust_company_info
  - 企业主数据表
  - 客户企业表
  - CustCompanyInfoDO
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info]
  - semantic:state_machines[企业建档/认证状态, 客户生命周期状态]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

企业主数据表，平台内部服务对接中「客户」这一实体的唯一权威载体。对外 Provider 暴露的 companyId / custId 即本表主键，各关系表（[[tables/cust_person_info]]、[[tables/cust_role_info]]、[[tables/cust_project_rel]]、[[tables/cust_group_rel]]）通过业务编码 code 挂接本表。

## 需求背景

企业信息需要在「客户中心—运营中台—业务系统」之间来回同步：建档与认证状态由 [[processes/cust_build_status_machine]] 驱动，生命周期状态由 [[processes/cust_status_machine]] 驱动，两者字段分离、互不覆盖。有效数据一律以 enable='Y' 为前提（见 [[rules/company_query_enable_y]]），状态类更新必须限定主数据（见 [[rules/status_update_main_data_type]]）。

## 版本演进

v0：按语义分析给出的字段语义与状态机证据首次成页；仅收录有证据的字段含义，未收录的列不做推断。

```ground:table
table: cust_company_info
columns:
  - field: id
    meaning: "企业主键，对外 Provider 的 companyId/custId 即此值（DO: CustCompanyInfoDO）"
    evidence: code
  - field: code
    meaning: "企业业务编码，新建时由 DataModelUtils.uuid() 生成，作为各关系表 ref_cust_company_info 的关联键"
    evidence: code
  - field: name
    meaning: "企业名称"
    evidence: code
  - field: certification_no
    meaning: "统一社会信用代码，跨系统一致性对齐字段"
    evidence: code
  - field: enable
    meaning: "有效标志，查询一律 .eq(enable, 'Y')"
    evidence: code
  - field: db_tenant_code
    meaning: "数据租户编码，数据隔离键；Provider 层常用 MetaDataThreadLocalConfig.setDbTenantCode(\"all\") 跨租户查询"
    evidence: code
  - field: cust_build_status
    meaning: "建档/认证状态（见状态机）"
    evidence: code
  - field: cust_status
    meaning: "客户生命周期状态（见状态机），与建档状态分离"
    evidence: code
  - field: cust_company_type
    meaning: "企业角色，JSON 数组字符串，如 \"[\\\"CORE\\\"]\"，创建时由 JSONArray/字符串拼接写入"
    evidence: code
  - field: identify_style
    meaning: "认证方式（自主/邀请-客户录入/邀请-平台录入/简易）"
    evidence: code
  - field: cust_build_type
    meaning: "建档渠道类型（PC_BUILD / AGW_BUILD）"
    evidence: code
  - field: cust_from
    meaning: "客户来源，邀请类认证为空时写 \"平台邀请\""
    evidence: code
  - field: data_type
    meaning: "数据类型，主数据为 CustDataTypeConstant.DATA_TYPE_MAIN；状态更新均带此条件"
    evidence: code
  - field: check_status
    meaning: "审核状态，提交建档时被置 null"
    evidence: code
  - field: audit_back_flag
    meaning: "审核退回标记 'Y'/'N'，非自主录入提交时置 'N'"
    evidence: code
  - field: need_register_ca
    meaning: "是否需要开通电子签章 'Y'/'N'；简易建档政策上强制为不开通"
    evidence: code
  - field: ca_register_status
    meaning: "电子签章开通状态 'Y'/'N'（对外返回还需叠加 caRegisterStatusY 校验）"
    evidence: code
  - field: need_register_bs
    meaning: "是否需要开通上上签 'Y'/'N'"
    evidence: code
  - field: bs_register_status
    meaning: "上上签开通状态 'Y'/'N'"
    evidence: code
  - field: legal_name / legal_phone / legal_email / legal_certification_type / legal_certification_no
    meaning: "法人姓名/电话/邮箱/证件类型/证件号，用于开通 CA 请求体"
    evidence: code
  - field: cust_email
    meaning: "企业邮箱"
    evidence: code
  - field: contact_address
    meaning: "联系地址"
    evidence: code
  - field: head_company
    meaning: "总部/集团企业标识，为空时（简易认证）置为 'Y'"
    evidence: code
  - field: ext
    meaning: "扩展 JSON，含 isChange/alterMode/alterTypes 等变更指令"
    evidence: code
  - field: cust_source
    meaning: "客户来源渠道标识（如 PLATFORM_PUSH）"
    evidence: code
```
## 关联表

- [[authorization_agreement]]：cust_company_info.id → authorization_agreement.cust_id（write-flow:CustAuthAgreementDomainServiceTest.java，confirmed）
- [[cust_account_info]]：cust_company_info.code → cust_account_info.ref_cust_company_info（ref-convention:CustAccountInfoDO.java，suggested）
- [[cust_auth_application]]：cust_company_info.code → cust_auth_application.ref_parent_company（write-flow:CustProductDomainService.java，confirmed）
- [[cust_build_record]]：cust_company_info.id → cust_build_record.cust_id（java-eq:OperCustFacade.java，suggested）
- [[cust_certification_info]]：cust_company_info.code → cust_certification_info.ref_cust_company_info（ref-convention:CustCertificationInfoDO.java，suggested）
- [[cust_change_record]]：cust_company_info.id → cust_change_record.cust_id（java-eq:OperCustFacade.java，suggested）
- [[cust_customized_product]]：cust_company_info.code → cust_customized_product.ref_cust_customized_product_cust_company_info（ref-convention:CustCustomizedProductDO.java，suggested）
- [[cust_group_rel]]：cust_company_info.id → cust_group_rel.root_cust_id（java-eq:CustGroupRelApplication.java，suggested）
- [[cust_head_company_info]]：cust_company_info.code → cust_head_company_info.ref_cust_head_company_info_cust_company_info（ref-convention:CustHeadCompanyInfoDO.java，suggested）
- [[cust_interworking_product]]：cust_company_info.code → cust_interworking_product.ref_cust_interworking_product_cust_company_info（ref-convention:CustInterworkingProductDO.java，suggested）
- [[cust_person_info]]：cust_company_info.code → cust_person_info.ref_cust_company_info（ref-convention:CustPersonInfoDO.java，suggested）
- [[cust_project_code_record]]：cust_company_info.id → cust_project_code_record.company_id（write-flow:CustProjectRelEnhanceService.java，confirmed）
- [[cust_project_rel]]：cust_company_info.code → cust_project_rel.ref_cust_project_rel_cust_company_info（ref-convention:CustProjectRelDO.java，suggested）
- [[cust_role_info]]：cust_company_info.code → cust_role_info.ref_cust_company_info（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_shareholder_info]]：cust_company_info.code → cust_shareholder_info.ref_cust_company_info（ref-convention:CustShareholderInfoDO.java，suggested）
- [[cust_user_rel]]：cust_company_info.id → cust_user_rel.company_id（write-flow:SubmitCustInfoEnhanceService.java，confirmed）
