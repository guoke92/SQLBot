---
type: concept
title: roleClass
page_key: concept.role-class
domain: 客户角色与端口
status: draft
aliases:
  - SysRoleDO.roleClass
  - 权限角色归属标识
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:RoleFacade#generateRoleClass
  - code_path:ClientCustRoleSyncService
also_confused_with:
  - cust_role_info.role_type
adjudication: boundary
boundary: roleClass 是权限角色的归属标识（企业类型+企业ID），ClientCustRoleSyncService 按最后一个下划线拆分出 companyType 与 companyId 后再同步；不等同于 cust_role_info 角色记录。
contract_version: "0.1"
---

# roleClass

roleClass 是权限侧（SysRoleDO）的**归属标识**，格式为 `{custType}_{custId}`，由 RoleFacade#generateRoleClass 拼接。ClientCustRoleSyncService 拿到 roleClass 后，按**最后一个下划线**拆分出 companyType 与 companyId，再据此做角色同步。

它与 [[concepts/company-role]] 的 role_type 长得像但不是一回事：roleClass 是字符串拼装的定位键（谁的角色），role_type 是枚举身份（是什么角色）。因为拆分规则依赖「最后一个下划线」，当 custType 本身含下划线时解析会退化为把前面全部当作 custType，这是使用该字段时最需要留意的隐式约束。

## 需求背景

需求文档在讲「企业角色同步」时混用了 roleClass 与 companyType 两个词；实现侧以 roleClass 作为同步入口参数，再反解出 companyType/companyId。

## 版本演进

- 由「按固定分隔解析」演进为「按最后一个下划线解析」，以兼容 custType 中出现的下划线。

## 关联

- [[concepts/company-role]]
- [[tables/cust_role_info]]