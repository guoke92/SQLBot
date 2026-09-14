---
type: caliber
title: 存量打包企业口径
page_key: legacy_package_companies
domain: CA证书认证
status: draft
aliases: [存量打包, queryEligibleCompanies 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CfcaOneCertFourStepPackageApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: calibers
---

圈定可以进入一证四步批量打包的存量企业：ca_register_status='Y'，同时要求 enable='Y'、update_time >= since、identify_style != 'SIMPLE'（简易认证不打包）。当请求指定了 custIds 时，改为在内存中过滤，SQL 侧的筛选条件不再全量生效——这是做口径核对时最容易漏掉的一条分支。

## 需求背景

本口径是"已注册企业复用"的入参集合，与 [[need_register_ca_judgement|需开通 CFCA 判定口径]]（面向未注册/处理中企业）互为补集，二者共用 cust_company_info 的 CA 字段但方向相反。

## 版本演进

- v0：首次固化筛选条件与内存过滤分支。

```ground:caliber
name: 存量打包企业口径
predicate: "cust_company_info.ca_register_status = 'Y'"
scope: 同时要求 enable='Y'、update_time >= since、identify_style != 'SIMPLE'（简易认证不打包）；指定 custIds 时改为内存过滤
evidence: "code_path:CfcaOneCertFourStepPackageApplication.java#queryEligibleCompanies"
```

关联页面：[[cust_company_info]]、[[ca_register_status]]、[[need_register_ca_judgement]]、[[simple_auth_forbid_ca]]。