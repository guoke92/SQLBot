---
type: rule
title: 非 BUILD_SUCCESS 不判定需开通 CA
page_key: non_build_success_no_ca
domain: CA证书认证
status: draft
aliases: [BUILD_SUCCESS 前置, 建档未完成不开通]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - code:CaUpgradeAuthApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: rules
---

cust_build_status != BUILD_SUCCESS 时 needOpenCa=N 并返回变更/未完成提示；升级授权书盖章也要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)。

**影响**：未成功建档企业不生成 CFCA/BS 协议。因此 [[ca_upgrade_auth|CA 升级授权书]] 缺失可能源于建档状态，而非附件上传失败。

## 需求背景

本规则是 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 的前置短路：即便 need_register_ca='Y'，建档未成功也不判定为需开通。

## 版本演进

- v0：首次固化前置状态与两处使用点（isOpenCa、processUpgradeAuthOnOpsNameChange）。

```ground:rule
name: 非 BUILD_SUCCESS 不判定需开通 CA
content: cust_build_status != BUILD_SUCCESS 时 needOpenCa=N 并返回变更/未完成提示；升级授权书盖章也要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)
impact: 未成功建档企业不生成 CFCA/BS 协议
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.need_register_ca
evidence: "code_path:CaOpenCaApplication.java#isOpenCa；CaUpgradeAuthApplication.java#processUpgradeAuthOnOpsNameChange"
```

关联页面：[[need_register_ca_judgement]]、[[cust_company_info]]、[[ca_upgrade_auth]]、[[company_in_change_forbid_ca]]。