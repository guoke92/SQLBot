---
type: concept
title: CA 升级授权书
page_key: ca_upgrade_auth
domain: CA证书认证
status: draft
aliases: [CaUpgradeAuth, otherAgreementFile1]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaUpgradeAuthApplication.java
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.file_refs_json
field_targets:
  - ca_certification_info.file_refs_json
  - ca_certification_info.notify_agreement_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.notify_agreement_json
belong: concepts
field_targets: [ca_certification_info.file_refs_json]
---

CA 升级授权书（serviceKey=CaUpgradeAuth，门户侧字段常写作 otherAgreementFile1）是企业在升级场景下出具的一份授权文件，其文件路径落在 file_refs_json 的 embeddedFiles（multipartField=CaUpgradeAuth），对应协议条目则在 notify_agreement_json 中留痕。

**边界（boundary）**：它与数字证书服务协议 CFCA_Auth（agreementFile1）是两份不同材料——两者 serviceKey 不同，在 notify_agreement_json 的 data.service_key 与 embeddedFiles.multipartField 上分别落位，filterUpgradeAuthContracts 还需排除 CFCA_Auth 文件。把 CFCA_Auth 的文件当成升级授权书，或反之，都会导致上送材料错配。业务事实记录在 [[ca_cfca_upgrade_report]]。

## 需求背景

升级授权书盖章要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)，与 [[non_build_success_no_ca]] 同源；办理入口为 processUpgradeAuthOnOpsNameChange。

## 版本演进

- v0：首次明确 CaUpgradeAuth 与 CFCA_Auth 的 serviceKey 分工与排除逻辑。

关联页面：[[ca_certification_info]]、[[ca_cfca_upgrade_report]]、[[notify_agreement]]、[[non_build_success_no_ca]]。