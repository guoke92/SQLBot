---
type: dict
title: tenant_project_approval_business_info.zhongdeng_register
page_key: tenant_project_approval_business_info__zhongdeng_register
belong: dicts
status: draft
anchors: [tenant_project_approval_business_info.zhongdeng_register]
sources: ['database_profile:tenant_project_approval_business_info.zhongdeng_register']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval_business_info]
---

# tenant_project_approval_business_info.zhongdeng_register

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `tenant_project_approval_business_info.zhongdeng_register`，表页 [[tables/tenant_project_approval_business_info]]。

## 取值

```ground:dict
dict: tenant_project_approval_business_info__zhongdeng_register
fields: [tenant_project_approval_business_info.zhongdeng_register]
values:
  交易前中登登记;转让时中登查询、中登登记;融资时中登查询、中登登记: {trust: proposed}
  交易前中登登记;融资时中登查询: {trust: proposed}
  融资时中登查询: {trust: proposed}
  交易前中登登记: {trust: proposed}
  无需中登登记: {trust: proposed}
  中登登记啊大大: {trust: proposed}
  中登登记方服务: {trust: proposed}
  中登登记我是受让方: {trust: proposed}
  交易前中登登记;转让时中登查询: {trust: proposed}
  交易前中登登记;转让时中登查询;融资时中登查询: {trust: proposed}
  BEFORE_REGISTER: {trust: proposed}
triage: hold
needs_review: true
```
