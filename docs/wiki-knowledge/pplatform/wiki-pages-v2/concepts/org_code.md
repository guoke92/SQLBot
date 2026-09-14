---
type: concept
title: orgCode
page_key: org_code
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - org_code
  - ContextHelper.orgCodeKey
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.org_code
  - code:UserInfoFacade.java:updateCustPerson
contract_version: "0.1"
maps_to: open_sso_channel.org_code
also_confused_with:
  - open_sso_channel.sys_channel
adjudication: boundary
belong: concepts
field_targets: [open_sso_channel.org_code]
sources: ["enrich:wiki-admin"]
---

orgCode 是同步到 SSO 的机构编码，落在 [[open_sso_channel.org_code]]，代码中经
RpcContext attachment（ContextHelper.orgCodeKey）在调用 SSO 前透传。

## 需求背景

用户/联系人与邮箱同步 SSO 时都要带上机构编码，以保证更新落到正确的 SSO 机构下
（[[update_cust_person_sso_email]]）。

## 版本演进

- v0（草稿）：术语边界来自代码透传点。

边界：orgCode 是机构编码，不是渠道编码本身；不可与 [[sys_channel]] 互换。

相关：[[open_sso_channel]]
