---
type: concept
title: 企业主键与企业编码
page_key: company_id_vs_code
belong: concepts
domain: cust
status: draft
aliases: [custId, 企业code, ref_cust_company_info]
maps_to: cust_company_info.code
field_targets: [cust_company_info.id, cust_company_info.code]
sources: ['code_path:CustCompanyQueryMapper.xml:80', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [bank_account_center]
adjudication: boundary
---

# 企业主键与企业编码

人员/角色/账户/证照/股东/授权申请/互通产品按 code=ref_* 关联。
建档记录、变更记录、集团关系、定制产品、邀请方、项目码记录、调研/问卷、运营人员变更留痕、用户企业角色按 id=company_id/cust_id。
不要把 ref_* 当成企业主键。
建档银行账号在 cust_account_info.ref_cust_company_info=企业 code，不是需求「账户中心」里的业务产品账户。

## 页面链接

- [[tables/cust_company_info]]
- [[concepts/bank_account_center]]
