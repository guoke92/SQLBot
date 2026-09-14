---
type: concept
title: Y/N 布尔约定
page_key: yn_flag_convention
domain: 平台内部服务对接
status: draft
aliases:
  - Y/N 标志位
  - 布尔字符约定
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
field_targets:
  - cust_company_info.enable
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.audit_back_flag
  - cust_person_info.enable
  - cust_project_rel.show_flag
  - sys_cust_user_rel.is_freeze
adjudication: >
  上述字段以字符 Y / N 表达布尔语义，Y 表示是、启用、需要或已冻结状态成立；
  服务侧读取与写入均应使用单字符取值，不写入 1/0 或 true/false。
also_confused_with:
  - cust_person_info.status
  - cust_company_info.cust_status
belong: concepts
---

「Y/N 布尔约定」描述平台内部服务对接中一组以字符 `Y` / `N` 存储的布尔字段。它们语义各异——启用（`enable`）、是否需要开通电子签章（`need_register_ca`）、CA 注册状态（`ca_register_status`）、审核退回标志（`audit_back_flag`）、关联显示标志（`show_flag`）、经办人冻结状态（`is_freeze`）——但取值形态一致，因此查询与写入可以按同一约定处理。

这类字段是查询口径的常见组成：企业有效性口径 [[valid_company]] 使用 `enable = 'Y'`，未冻结口径 [[not_frozen_user_rel]] 使用 `is_freeze = 'N'`，冻结状态机见 [[operator_freeze_flow]]。

## 需求背景
布尔语义在不同表上以字符存储，如果某些服务按 1/0 处理，就会出现过滤条件永远为假或永远为真的隐性缺陷；把取值形态固化为一条约定，可以让人工与代码审查都按同一标准检查。

## 版本演进
- v0.1（本页）：约定来自代码语义分析中各字段释义中「Y/N」描述的一致性归纳。注意区分同为「状态」但取值是枚举字符串的字段，例如 `cust_person_info.status`、`cust_company_info.cust_status`，它们不属于本约定。