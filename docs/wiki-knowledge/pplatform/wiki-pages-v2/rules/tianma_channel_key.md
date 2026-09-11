---
type: rule
title: 天马渠道键写入
page_key: rules/tianma_channel_key
domain: 外部渠道与银行对接
status: draft
aliases:
  - CloudChannel.TIANMA.getDictKey()
  - 天马渠道键
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
  - code:CustAccessApplication#validateSetValueOfTianma
contract_version: "0.1"
---

# 天马渠道键写入

## 业务定位

天马入站建档会执行 `custDependentReqDto.setChannel(CloudChannel.TIANMA.getDictKey())`，把天马渠道键写入内部请求对象；随后由 `validateSetValueOfTianma` 用该渠道键反查 `cust_access_secret`，得到本次落库使用的 `db_tenant_code`。（本条规则的证据引用在语义分析原文中于方法名处被截断，方法名以 [[concepts/tianma_inbound_outbound]] 中相同引用为准。）

## 需求背景

天马渠道不能自行指定租户，租户必须由渠道密钥表配置决定（见 [[calibers/channel_tenant_mapping]]）。因此入站服务的第一步是把"我是天马"显式写入请求对象，再交给统一的校验/解析流程，避免渠道身份与租户解析散落在各分支里。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析；证据引用截断，已登记 REVIEW，尚无需求文档或变更单佐证。

```ground:rule
name: 天马渠道键写入
content: "custDependentReqDto.setChannel(CloudChannel.TIANMA.getDictKey())，由 validateSetValueOfTianma 用该渠道反查 cust_access_secret 得到 dbTenantCode"
impact: 天马入站租户由渠道密钥表决定，而非请求参数
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code:TianmaService#companyArc"
```

## 关联页面

- 概念：[[concepts/tianma_inbound_outbound]]、[[concepts/channel]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/non_writeoff]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/nonstandard_inbound_all_tenant]]
- 载体表：[[tables/cust_company_info]]