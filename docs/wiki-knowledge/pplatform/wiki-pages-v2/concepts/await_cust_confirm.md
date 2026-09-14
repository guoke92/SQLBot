---
type: concept
title: 待客户确认
page_key: await_cust_confirm
domain: 准入接入与接入密钥
status: draft
aliases:
  - CUST_CONFIRM_AWAIT
  - AWAIT_CUST_CONFIRM
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustAuditMsgService.java:getCustBuildStatus
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status = 'CUST_CONFIRM_AWAIT'
also_confused_with:
  - cust_company_info.cust_build_status = 'AWAIT_CUST_CONFIRM'
adjudication: boundary
boundary: 邀请/自主流程用CUST_CONFIRM_AWAIT；简易认证代码用AWAIT_CUST_CONFIRM，需核对dictKey。
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 待客户确认

## 业务定位

「待客户确认」表示建档申请已提交、等待客户侧确认的状态，落在 [[tables/cust_company_info|cust_company_info]] 的 `cust_build_status = 'CUST_CONFIRM_AWAIT'`。运营中台退回客户（`CUST_CHECK_BACKTOCUSTOM`）时，本地建档态也会回到该值。

## 边界与混淆

代码中同时存在 `AWAIT_CUST_CONFIRM`（简易认证分支 `confirmCustInfoForSimpleAuth` 使用）。两者是否同一字典键下的两种写法尚未确认，读库时不可默认等价。

## 需求背景

自主/邀请流程需要客户确认这一中间环节；简易认证流程的确认语义与之接近，因此出现命名近似的两个值。

## 版本演进

`CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM` 并存，属历史分支遗留，需核对字典键后收敛。

---REVIEW: concept | 待客户确认
- `CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM` 是否为同一 dictKey 的两个值，语义分析未给出结论，需核对数据字典与简易认证分支代码。
---END REVIEW---

相关：[[cust_company_info]]
