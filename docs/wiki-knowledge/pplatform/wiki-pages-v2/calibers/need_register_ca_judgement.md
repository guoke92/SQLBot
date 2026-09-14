---
type: caliber
title: 需开通 CFCA 判定口径
page_key: need_register_ca_judgement
domain: CA证书认证
status: draft
aliases: [needOpenCa, 需开通 CA 判定]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: calibers
---

判定一家企业当前是否需要发起 CFCA 开通：意愿位 need_register_ca='Y'，且（ca_register_status in ('N','P') 或签章中台判定 CA 失效）；否则 needOpenCa=N。中台失效判定来自 [[sign_center_cert_status]] 的归一结果，且 isOpenCa 中存在"仅内存视为未开通、不回写库"的分支。

## 需求背景

本口径与 [[legacy_package_companies|存量打包企业口径]] 是互补的两个集合；与 BS（上上签）渠道的判定平行但独立，两者在 isOpenCa 中分别组装 serviceKeys（DATA_SOURCE_CFCA_AUTH / DATA_SOURCE_BS_AUTH），边界见 [[ca_certificate]]。建档未成功时直接判 N，见 [[non_build_success_no_ca]]。

## 版本演进

- v0：首次固化判定表达式与内存分支。

```ground:caliber
name: 需开通 CFCA 判定口径
predicate: "cust_company_info.need_register_ca = 'Y'"
scope: "且 ca_register_status in ('N','P') 或签章中台判定 CA 失效；否则 needOpenCa=N"
evidence: "code_path:CaOpenCaApplication.java#isOpenCa"
```

关联页面：[[cust_company_info]]、[[ca_register_status]]、[[legacy_package_companies]]、[[non_build_success_no_ca]]、[[ca_certificate]]。