# pplatform-web 业务数据域目录

## 客户建档与变更 (`customer`)

- 业务概念：建档、建档成功、企业变更
- 本地数据表：`cust_company_info`, `cust_build_record`, `cust_change_record`, `cust_company_lifecycle_info`, `cust_person_info`, `cust_role_info`
- 运行时条目：`TERM-ONBOARDING`, `TERM-BUILT-SUCCESS`, `CAL-EFFECTIVE-BUILT-COMPANY`, `RULE-PROCESS-NOT-SUCCESS`

## 产品、项目与企业角色 (`project-product`)

- 业务概念：平台产品、租户产品、租户项目、企业关联项目、企业角色
- 本地数据表：`platform_product`, `tenant_product`, `tenant_project`, `cust_project_rel`
- 运行时条目：`CAL-OPENED-TENANT-PRODUCT`, `CAL-FINANCE-PROJECT-REL`, `REL-PROJECT-COMPANY`, `REL-PROJECT-TENANT-PROJECT`

## 租户配置 (`tenant`)

- 业务概念：租户配置
- 本地数据表：`tenant_setting_config`
- 运行时条目：`CAL-ENABLED-TENANT-CONFIG`

## 运营人员与风险提示 (`operation`)

- 业务概念：运营对接人、离职运营人员
- 本地数据表：`operation_user`, `tenant_project`, `cust_project_rel`
- 运行时条目：`CAL-ACTIVE-OP-USER`, `CAL-DELETED-OP-USER`, `RULE-TOP-FLAG-RISK`

## OpenAPI、推数与协议边界 (`integration`)

- 业务概念：推数、同步失败记录、协议签署
- 本地数据表：`cust_access_secret`, `client_api_sync_error`
- 运行时条目：`RULE-SYNC-ERROR-GRAIN`, `RULE-AGREEMENT-EXTERNAL`
- 外部数据存储：协议插件、通知插件
