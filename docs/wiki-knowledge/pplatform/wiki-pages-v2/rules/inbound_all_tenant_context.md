---
type: rule
title: 入站渠道全租户上下文
page_key: inbound_all_tenant_context
domain: 外部渠道与银行对接
status: draft
aliases:
  - 入站租户上下文置 all
oid: 1
scope:
  databases:
    - cust
sources:
  - code:TianmaController.companyArchive
  - code:AlipayAntArchiveController.channelArchive
  - code:CustAccessApplication.validateSetValue
  - code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-tianma/.../controller/TianmaController.java#companyArchive
contract_version: "0.1"
belong: rules
---

天马与蚂蚁渠道入站控制器在入口处先把数据租户上下文置为 `all`，再依据渠道秘钥定位真实租户。

## 需求背景
跨租户检索是渠道建档查重的前提（同一信用代码可能已在其他租户下存在），但落库必须回到真实租户，否则归属错误。该规则是 [[channel_enable_filter]] 与 [[company_certification_tenant_match]] 的前置条件，租户语义见 [[tenant]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 入站渠道全租户上下文
content: 天马/蚂蚁渠道入站控制器入口先执行 MetaDataThreadLocalConfig.setDbTenantCode("all")，随后由渠道秘钥(cust_access_secret)定位真实租户
impact: 跨租户检索与落库租户归属
field_targets:
  - cust_company_info.db_tenant_code
  - cust_access_secret.channel
evidence: "code:TianmaController.companyArchive; AlipayAntArchiveController.channelArchive; CustAccessApplication.validateSetValue + code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-tianma/.../controller/TianmaController.java#companyArchive + reqdoc:tianma-supplier-company-archive-inbound"
```