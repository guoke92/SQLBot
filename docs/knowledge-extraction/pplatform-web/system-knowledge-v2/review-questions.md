# pplatform-web v2 知识包待审核问题

## 数据库结构与关系

1. `cust_company_info.id` 与 `code` 的唯一性、历史版本策略分别是什么？哪些业务表连接 id，哪些连接 code？
2. `cust_project_rel` 是否存在同一企业、项目、角色的重复有效记录？`show_flag=Y` 是否有数据库唯一约束？
3. `tenant_project.product_id → tenant_product.id`、`tenant_product.platform_product_id → platform_product.id` 的空值率和实际基数如何？
4. `cust_person_info.ref_cust_company_info` 与 `cust_role_info.ref_cust_company_info` 是否始终保存企业 code？
5. `cust_access_secret.cust_id`、`cust_change_record.cust_id`、`cust_company_lifecycle_info.cust_id` 的实际外键和历史保留策略是什么？

## 业务口径与时间

6. “建档时间”默认指首次提交、运营审核通过、企业生效还是主记录创建时间？各入口是否有统一字段？
7. “项目生效”应使用 `project_status`、`rule_status`、`enable` 还是组合口径？
8. “产品已开通”在租户产品与客户产品授权两类主体上是否都使用 `OPENED`，是否存在在途但可用状态？
9. “当前关联企业”除 `cust_project_rel.enable=Y` 外，是否还必须限定企业有效、项目有效和租户作用域？
10. 企业变更被拒绝但原企业仍有效时，应如何统计“变更失败企业”和“当前有效企业”？

## 外部系统与查询验证

11. 协议、通知、工作流的主数据是否有可接入 SQLBot 的独立数据源？若无，哪些本地引用字段可用于查询？
12. `client_api_sync_error` 中可用于业务去重的字段是什么？失败后成功重试如何闭环关联？
13. 运营人员字段中哪些是标量 ID、哪些是 JSON 数组？如何确定性展开并连接 `operation_user.operation_id`？
14. 为本包绑定实际数据源后，应对所有 10 条关系执行基数、空值率和孤儿率验证，并对 7 个查询范式生成 SQL 后实际执行。
