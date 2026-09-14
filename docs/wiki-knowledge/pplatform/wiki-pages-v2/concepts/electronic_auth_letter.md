---
type: concept
title: 电子授权书（电子签约版授权书）
page_key: electronic_auth_letter
domain: 授权协议与电子授权
status: draft
aliases:
  - 线下电子授权书
  - off_auth 授权书
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - db:tenant_setting_config
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
maps_to:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - tenant_setting_config.generate_electronic_auth_flag
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - tenant_setting_config.generate_electronic_auth_flag
adjudication: boundary
also_confused_with:
  - authorization_agreement.authed_status
belong: concepts
sources: ["enrich:wiki-admin"]
---

「电子授权书」指线下授权（off_auth）场景下把纸质授权书改为 CFCA 在线签署的方案，其存在性由租户开关 + 企业签章能力共同定义：[[tenant_electronic_auth_flag]]、[[need_register_ca]]、[[cfca_registered]]。它不是一个独立的授权状态字段，因此**不能**用 `authorization_agreement.authed_status` 来代替描述。

## 需求背景
线下授权书需要人工签署与回收，效率低且难追溯，因此引入电子签约版：租户开关打开、企业已开通 CA、且本次业务满足审核通过与变更项白名单时，系统自动发起签署，完整触发条件见 [[offline_eauth_sign_trigger]]；签署幂等见 [[auth_sign_idempotent]]。

## 版本演进
该能力上线时同时引入了租户级开关（[[tenant_setting_config]] 的 `generate_electronic_auth_flag`）与企业级签章字段；后续又加入“CA 未开通时延迟补偿签署”的补签链路，见 [[ca_delayed_compensation_sign]]，以及简易认证强制不开通 CA 的约束，见 [[simple_identify_disable_ca]]。

相关：[[cust_company_info]]
