---
type: caliber
title: 人员启用过滤
page_key: person_enable_filter
domain: 外部渠道与银行对接
status: draft
aliases:
  - 管理员定位口径
  - cust_person_info.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCurrentAdmin
contract_version: "0.1"
belong: calibers
---

定位企业管理员时的取数口径：enable='Y' 且 user_type=admin，按 create_time 倒序取 1 条。

## 需求背景
管理员是建档结果推送与运营流程通知的收件人，必须唯一且有效；数据落点见 [[cust_person_info]]，与企业的 code 级软关联决定了查询需带 ref_cust_company_info。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 人员启用过滤
predicate: "cust_person_info.enable = 'Y'"
scope: 定位企业管理员（user_type=admin、按 create_time 倒序 limit 1）
evidence: "code:CustAccessApplication.getCurrentAdmin"
```