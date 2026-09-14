---
type: concept
title: 被授权人
page_key: authorized_person
domain: CA证书认证
status: draft
aliases: [authPerson, 经办人, 管理员]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
  - cust_company_info.legal_name
adjudication: boundary
also_confused_with:
  - cust_company_info.legal_name
belong: concepts
field_targets: [cust_person_info.user_type]
sources: ["enrich:wiki-admin"]
---

被授权人（业务上常称 authPerson、经办人、管理员）取 cust_person_info：user_type=admin + enable=Y + companyType=登录角色，且 ref_cust_company_info 指向本企业 code。

**边界（boundary）**：法人为 cust_company_info 的法人三件套（legal_name 等），二者不可互换。同一次认证中两类人可能同时出现：H5 刷脸意愿优先取法人命中数据，公安二要素取被授权人。因此"意愿留痕里的人"和"二要素核验里的人"未必是同一个自然人，核对数据时需分别取数。

## 需求背景

被授权人身份还会决定能否进入一证四步：CA 开通操作人必须是企业管理员（user_type=admin、enable=Y、company_type=登录角色、ref_cust_company_info=企业 code），见 [[ca_open_operator_must_be_admin]]。

## 版本演进

- v0：首次沉淀被授权人取数条件与法人边界。

关联页面：[[ca_open_operator_must_be_admin]]、[[enterprise_four_elements]]、[[ca_certification_info]]、[[ca_upgrade_auth]]。

相关：[[cust_person_info]]
