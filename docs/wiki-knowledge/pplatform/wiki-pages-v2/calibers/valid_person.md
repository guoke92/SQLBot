---
type: caliber
title: 有效联系人
page_key: valid_person
domain: 平台内部服务对接
status: draft
aliases:
  - 有效联系人口径
  - 企业联系人过滤
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「有效联系人」用于查询 [[cust_person_info]] 中的企业联系人列表，同时施加两个条件：启用状态为 Y，且联系人状态属于 ADD 或 EFFECT。两个条件的语义不同——前者是记录级启用（见 [[yn_flag_convention]]），后者是人员状态机上的可用节点（取值见 CustPersonStatusConstant），因此只过滤其中之一都会产生偏差。

## 需求背景
企业用户列表是客户侧与运营侧共用的高频查询，需要稳定地排除停用与失效人员；把该组合固化为口径后，人员表的 `status` 字典变更不应悄悄放宽查询结果。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析，`status` 的完整枚举取值未在证据中出现，当前仅记录参与判定的两个取值。

```ground:caliber
name: 有效联系人
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.status IN ('ADD','EFFECT')"
scope: 查询企业联系人列表
evidence: "code_path:PlatFormUserApplication.java:listCompanyUser"
```