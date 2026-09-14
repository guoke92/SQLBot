---
type: rule
title: 变更时法人手机空值不覆盖
page_key: legal_phone_not_overwrite
domain: 外部渠道与银行对接
status: draft
aliases:
  - legalPhone 空值保护
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.updateSystemData
contract_version: "0.1"
belong: rules
---

企业变更时若法人手机号入参为空或空白，不覆盖库中旧值。

## 需求背景
在途建档会把法人手机号推送至运营，若变更请求携带空值直接落库会造成运营侧联系人缺失；因此保留旧值优先。字段见 [[cust_company_info]]，变更流程前置见 [[cust_status]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 变更时法人手机空值不覆盖
content: updateSystemData 中法人手机号为空/空白时保留库中旧值，避免在途建档推运营为空
impact: cust_company_info.legal_phone 不被清空
field_targets:
  - cust_company_info.legal_phone
evidence: "code:CustAccessApplication.updateSystemData"
```