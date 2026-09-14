---
type: caliber
title: 未冻结的关联关系
page_key: not_frozen_rel
domain: 经办人/联系人/管理员管理
status: draft
aliases: [is_freeze=N, 关联有效口径]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java#deleteCustInfo"]
contract_version: "0.1"
belong: calibers
---

"未冻结的关联关系"口径 = sys_cust_user_rel.is_freeze='N'，在企业删除时用于判断是否还可以清理 sys_user。冻结的关联视为仍有业务挂靠，不能直接清理用户（[[sys_cust_user_rel]]）。

## 需求背景
- 该口径是企业级删除/冻结操作的安全阀，与联系人侧 enable 口径共同决定账号可否被回收（[[valid_person]]、[[company_status_cascade_person]]）。

## 版本演进
- 当前版本仅确认该口径存在于企业删除路径，未覆盖全部消费点。

```ground:caliber
name: 未冻结的关联关系
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 企业删除时判断是否可清理 sys_user
evidence: "code:CustCompanyInfoApplication.java#deleteCustInfo"
```

相关页面：[[sys_cust_user_rel]]、[[company_status_cascade_person]]、[[valid_person]]。