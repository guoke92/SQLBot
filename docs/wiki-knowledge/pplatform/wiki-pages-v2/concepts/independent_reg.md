---
type: concept
title: 自主建档
page_key: independent_reg
domain: 准入接入与接入密钥
status: draft
aliases:
  - independentReg
  - 自主注册
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - db:cust_company_info.identify_style
contract_version: "0.1"
maps_to: cust_company_info.identify_style = 'INVITE'
also_confused_with:
  - cust_company_info.identify_style = 'SELF'
  - cust_company_info.identify_style = 'INVITE_AGW'
adjudication: boundary
boundary: 代码independentReg实际setIdentifyStyle=INVITE；SELF是自主认证消息分支；INVITE_AGW是非自主/平台录入。
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 自主建档

## 业务定位

「自主建档」指接入客户自行发起并确认建档的流程。在数据上，代码中的 `independentReg` 分支实际把 [[tables/cust_company_info|cust_company_info]] 的 `identify_style` 置为 `INVITE`，因此本术语映射到 `identify_style = 'INVITE'`。

## 边界与混淆

- `SELF`：自主认证消息分支使用的取值，与业务口语「自主」同名但落值不同。
- [[concepts/dependent_reg|非自主建档]]（`INVITE_AGW`）：平台代录，流程不同。

建档状态上的差异见 [[processes/cust_build_status_state_machine|企业建档准入状态机]]：自主分支提交后先进入待客户确认。

## 需求背景

自主与非自主两类来源需要走不同的确认链路，故以 `identify_style` 分流。

## 版本演进

业务词「自主」与代码值 `INVITE` 之间的错位是命名遗留，暂无进一步演进证据。

---REVIEW: concept | 自主建档
- 业务词（independentReg / 自主注册）与落值 `INVITE` 不一致，`SELF` 的实际消费分支未在证据中明确，建议核对字典与前端文案。
---END REVIEW---

相关：[[cust_company_info]]
