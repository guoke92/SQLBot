---
type: caliber
title: 存量CA数据打包企业范围
page_key: legacy_package_company_scope
domain: CA证书认证
status: draft
aliases: [queryEligibleCompanies 口径, 存量打包企业范围]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"]
contract_version: "0.1"
belong: calibers
---

口径含义：存量 CFCA 一证四步离线打包任务在 cust_company_info 上筛选符合条件的企业——enable='Y'、ca_register_status='Y'、update_time >= 起始时间、且 identify_style != 'SIMPLE'。

四个条件分别承担不同职责：enable 过滤有效企业，ca_register_status 只取已开通 CA 的企业，update_time 限定增量窗口，identify_style != 'SIMPLE' 排除简易建档企业——这与简易认证强制不开通 CA 的规则相互印证（[[rules/simple_auth_force_no_ca]]）。企业范围确定后逐企业打包，打包内容与 [[concepts/one_cert_four_steps]] 的流程步骤对应。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。谓词字段与比较方向均逐字来自代码路径证据；对应的实现规则见 [[rules/legacy_package_query]]。

## 版本演进

暂无文档化的版本演进证据。

```ground:caliber
name: 存量CA数据打包企业范围
predicate: "cust_company_info.enable = 'Y' 且 cust_company_info.ca_register_status = 'Y' 且 cust_company_info.update_time >= ? 且 cust_company_info.identify_style != 'SIMPLE'"
scope: 存量CFCA一证四步离线打包任务查询符合条件的企业
evidence: "code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"
```

相关页面：[[rules/legacy_package_query]]、[[rules/simple_auth_force_no_ca]]、[[concepts/one_cert_four_steps]]。