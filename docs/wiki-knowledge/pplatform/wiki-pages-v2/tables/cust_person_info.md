---
type: table
title: cust_person_info（企业联系人表）
page_key: table.cust_person_info
domain: 平台内部服务对接
status: draft
aliases:
  - cust_person_info
  - 企业联系人表
  - 经办人表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_person_info]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

企业联系人（含客户管理员、经办人、游客）明细表。联系人既挂在企业 code 上，也通过 user_id 串联用户中心（[[tables/sys_user_sso_user]]），是内部服务对接中「人—企业—产品」链路的中间节点。

## 需求背景

联系人的有效性与企业侧口径不同：企业看 enable，联系人查询有效数据时取 status ∈ {ADD, EFFECT}（见 [[calibers/person_effective_status]]）。经办人无产品权限时会被置 enable='N'，解冻后恢复（见 [[rules/operator_permission_disable]]）。手机号加密存储，查询需传密文（见 [[rules/person_phone_encrypted_query]]）。

## 版本演进

v0：首次成页，收录语义分析中给出含义的联系人字段。

```ground:table
table: cust_person_info
columns:
  - field: ref_cust_company_info
    meaning: "所属企业 code，联系人查询主关联键"
    evidence: code
  - field: cust_company_id
    meaning: "所属企业 id"
    evidence: code
  - field: phone
    meaning: "手机号，加密存储（metaDataEncryptionService.encryptAndBase64Str），查询需传密文"
    evidence: code
  - field: user_id
    meaning: "对应 sys_user 主键，用于按用户维度串联企业联系人"
    evidence: code
  - field: user_type
    meaning: "用户类型：admin（客户管理员）/ operator（经办人）/ guest（游客）"
    evidence: code
  - field: company_type
    meaning: "企业角色（单值，对应 cust_company_type 数组中的一项）"
    evidence: code
  - field: status
    meaning: "联系人状态，查询有效联系人时取 ADD 或 EFFECT（CustPersonStatusConstant）"
    evidence: code
  - field: enable
    meaning: "有效标志 'Y'/'N'；经办人无产品权限时被置 'N'，解冻时恢复 'Y'"
    evidence: code
  - field: name / user_name / email
    meaning: "姓名/登录名/业务邮箱；仅本身为空时才由经办人新增流程补全"
    evidence: code
  - field: operator_id / operator_realname / operator
    meaning: "运营人员 id/姓名/登录名，由资产审核运营人员同步写入"
    evidence: code
  - field: operator_push_system
    meaning: "需要推送的运营中台渠道集合，逗号分隔，用于 systemLinkFacade.syncOperation"
    evidence: code
  - field: cust_build_status
    meaning: "联系人侧冗余的建档状态"
    evidence: code
```
## 关联表

- [[cust_certification_info]]：cust_person_info.code → cust_certification_info.ref_cust_company_info（write-flow:MiniFaceServiceImpl.java，confirmed）
- [[cust_change_cfg]]：cust_person_info.ref_cust_company_info → cust_change_cfg.code（java-eq:CustCompanyInfoApplication.java，suggested）
- [[cust_change_record]]：cust_person_info.ref_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_person_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustPersonInfoDO.java，suggested）
