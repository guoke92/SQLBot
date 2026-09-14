---
type: concept
title: CA（数字证书）
page_key: ca_certificate
domain: CA证书认证
status: draft
aliases: [CFCA, 一证四步, 电子签章开通]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - code:CustCompanyCaPolicy.java
contract_version: "0.1"
maps_to: cust_company_info.ca_register_status
field_targets:
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_ca
adjudication: boundary
also_confused_with:
  - cust_company_info.bs_register_status
belong: concepts
field_targets: [cust_company_info.ca_register_status]
---

CA（数字证书）在本主题里特指 CFCA 渠道的电子签章开通能力，业务口头语包括"CFCA""一证四步""电子签章开通"。它落到数据上是 cust_company_info 的意愿位与注册状态位两个字段，链路状态由 [[ca_register_status]] 描述，判定口径见 [[need_register_ca_judgement]]。

**边界（boundary）**：need_register_ca / ca_register_status 属 CFCA 数字证书；need_register_bs / bs_register_status（上上签/BS）属另一签章渠道，二者在 isOpenCa 中分别组装 serviceKeys（DATA_SOURCE_CFCA_AUTH / DATA_SOURCE_BS_AUTH），不可互换。凡把 bs_register_status 当作 CFCA 状态统计的结论都应作废。

## 需求背景

"一证四步"指协议告知、企业实名核验、被授权人核验、意愿留痕四类材料齐备后上送签章中台；材料落在 [[ca_certification_info]]，上送结果落 [[ca_submit_status]]，中台证书态归一为 [[sign_center_cert_status]]。简易认证企业被强制不纳入 CA，见 [[simple_auth_forbid_ca]]。

## 版本演进

- v0：首次区分 CFCA 与 BS 两条渠道的字段边界。中台证书态与本地上送态的语义差在 [[cert_status]] 中单独沉淀。

关联页面：[[cust_company_info]]、[[ca_register_status]]、[[need_register_ca_judgement]]、[[sign_center_cert_status]]、[[cert_status]]、[[ca_certification_info]]。