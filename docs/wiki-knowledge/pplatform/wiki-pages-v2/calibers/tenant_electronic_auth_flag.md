---
type: caliber
title: 电子授权书租户开关
page_key: tenant_electronic_auth_flag
domain: 授权协议与电子授权
status: draft
aliases:
  - 租户电子授权书开关
  - generate_electronic_auth_flag=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:tenant_setting_config
  - code:ElectronicAuthLetterApplication.java
contract_version: "0.1"
belong: calibers
---

判断某租户是否启用「线下授权书电子签约版」的口径，查询时另带 `enable='Y'`。它是 [[offline_eauth_sign_trigger]] 多重与门中的租户级条件，与 [[electronic_auth_letter]] 概念对应。

```ground:caliber
name: 电子授权书租户开关
predicate: "tenant_setting_config.generate_electronic_auth_flag = 'Y'"
scope: "租户是否开启线下授权书电子签约版；查询另带 enable='Y'"
evidence: "code:ElectronicAuthLetterApplication.java:isGenerateElectronicAuthEnabled"
```