---
type: rule
title: AMS 迁移去重（企业已存在则只补人员）
page_key: ams_migratory_dedup
domain: 租户迁移
status: draft
aliases: [AMS 迁移合并, 企业已存在只补人员]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
contract_version: "0.1"
belong: rules
---

**（document_claim，未证实）** 需求侧"讯易链与 AMS 都建过档的存量企业需做数据合并"的主张在语义分析中原文截断，尚未与代码逐条对齐。

`productAppId=AMS` 时不重建企业：先用统一社会信用代码（为空则按名称模糊反查）+ `db_tenant_code` 查已存在企业，命中后仅按 手机号+companyType+userType 过滤出增量管理员/经办人、按 roleType 过滤增量角色，走客户变更流程补齐。人员匹配涉及加密列，见 [[migratory_person_phone_encrypt_match]]。

```ground:rule
name: AMS 迁移去重（企业已存在则只补人员）
content: "productAppId=AMS 时，先用统一社会信用代码（为空则 companyNameVagueCheckService 按名称反查）+dbTenantCode 查已存在企业；命中则不重建企业，只按 手机号+companyType+userType 过滤出增量管理员/经办人、按 roleType 过滤增量角色，走客户变更流程补齐"
impact: "实现『讯易链与 AMS 都有建档时保留一条』的企业合并"
field_targets:
  - cust_company_info.certification_no
  - cust_person_info.phone
  - cust_person_info.company_type
  - cust_person_info.user_type
  - cust_role_info.role_type
evidence: "code:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

同一家企业在两个业务系统都有建档（如讯易链与 AMS）时，迁移后只应保留一条企业主体，人员以增量方式补齐，避免重复主体与重复人员。

## 版本演进

由"一律新建"演进为"命中即合并只补人员"；合并粒度从企业级下沉到人员级（手机号+企业类型+用户类型）与角色级（roleType）。需求文档中关于合并范围与保留规则的表述在语义分析中截断（document_claim，未证实），需回原文确认。

相关：[[cust_company_info]]、[[cust_person_info]]、[[产品编码]]。