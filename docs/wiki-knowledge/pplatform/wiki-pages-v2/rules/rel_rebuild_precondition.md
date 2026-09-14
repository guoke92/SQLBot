---
type: rule
title: 关联重建前置条件
page_key: rel_rebuild_precondition
domain: 经办人/联系人/管理员管理
status: draft
aliases: [processSingleCompany, reBuildSysCustUserRel, 关联重建]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustCompanyUserRelApplication.java#processSingleCompany,#reBuildSysCustUserRel"]
contract_version: "0.1"
belong: rules
---

processSingleCompany / reBuildSysCustUserRel 的完整前置条件：企业 enable=Y、cust_build_status ∈ {BUILD_SUCCESS, CUST_CHANGE}、存在 open_status=OPENED 的产品、管理员 user_id>0；管理员角色码取 custNacosProperties.getAuthUserRoleCode(companyType)，经办人固定 ROLE_CODE_NORMAL；若 (productId, roleId) 已在关联集中则跳过（[[sys_cust_user_rel]]、[[rel_rebuild_company]]、[[opened_product]]）。

## 需求背景
- 该规则决定 sys_cust_user_rel 是否写入，是"已开通产品"与权限关联的唯一入口（[[opened_product]]）。
- 管理员 user_id 为空（尚未开户/未同步用户中心）时重建被跳过，需先完成用户开户（[[cust_person_info]]）。

## 版本演进
- 当前版本已按 (productId, roleId) 做幂等去重，重复重建不会产生重复关联。

```ground:rule
name: 关联重建前置条件
content: "processSingleCompany/ reBuildSysCustUserRel 要求：企业 enable=Y、cust_build_status ∈ {BUILD_SUCCESS, CUST_CHANGE}、存在 open_status=OPENED 的产品、管理员 user_id>0；管理员角色码取 custNacosProperties.getAuthUserRoleCode(companyType)，经办人固定 ROLE_CODE_NORMAL；已在关联集（productId_roleId）中则跳过"
impact: 决定 sys_cust_user_rel 是否写入
field_targets:
  - cust_company_info.cust_build_status
  - cust_person_info.user_type
  - cust_person_info.user_id
evidence: "code_path:CustCompanyUserRelApplication.java#processSingleCompany,#reBuildSysCustUserRel"
```

相关页面：[[sys_cust_user_rel]]、[[cust_company_info]]、[[cust_person_info]]、[[opened_product]]、[[rel_rebuild_company]]。