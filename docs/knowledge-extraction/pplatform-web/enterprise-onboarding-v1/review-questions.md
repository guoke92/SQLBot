# 企业建档知识审核问题

以下问题必须在发布前确认；未确认不会阻止继续扩展提取，但对应候选不得标记为 certified。

1. 业务人员口中的“建档完成”是否始终要求 `BUILD_SUCCESS + EFFECT`，还是包含 `CUST_CHANGE + CHANGE` 的在途变更企业？
2. “建档时间”默认指首次提交认证时间、运营流程创建时间、审核通过时间，还是企业主记录创建时间？当前代码没有发现一个覆盖所有来源的统一“建档成功时间”。
3. `cust_first_submit_auth` 明确只覆盖 `SELF`/`INVITE`，其他录入方式应使用哪个时间字段？
4. `BUILDING` 与 `CUST_BUILDING` 是否仍在不同生产场景使用，还是前者仅为历史/兼容状态？
5. `CUST_BUILD_SUCCESS`/`CUST_BUILD_FAIL` 与 `BUILD_SUCCESS`/`BUILD_FAIL` 的产品口径边界是什么？当前回调主链主要落后者。
6. `cust_build_record` 是否存在业务唯一键？`saveOrUpdate` 未显式提供唯一条件，本轮不能据代码推断一企一次。
7. 企业与联系人应优先使用 `id=cust_company_id` 还是 `code=ref_cust_company_info`？两种路径并存，需要 DB 基数和空值率验证。
8. 企业、角色、项目关系表上的 `status`、`enable`、`project_open_status` 分别控制什么业务有效性？不同查询可能需要不同组合。
9. `db_tenant_code` 是否应作为所有关系的必要等值谓词，还是数据库层已经做物理租户隔离？
10. 审核通过时间位于哪个可稳定查询字段/历史表？仅凭 `update_time` 无法证明就是建档成功时间。
11. 补偿任务成功后是否更新原 `cust_build_record`，还是新增记录？这决定失败次数和重试成功率的查询粒度。
12. 文档中的简化状态流转与当前代码枚举、回调分支不完全一致，应由哪位业务负责人认证最终表述？

## 建议数据库验证清单

- 六张核心表的主键、唯一约束、索引和实际字段类型。
- `data_type`、`enable`、`cust_build_status`、`check_status`、`cust_status`、`identify_style` 的值分布与组合分布。
- `cust_company_info.id/code` 到人员、角色、项目、认证、建档记录的 orphan rate 与基数。
- `cust_first_submit_auth` 在各 `identify_style/cust_source/cust_build_type` 下的覆盖率。
- `cust_build_record` 每企业记录数、补偿记录占比、重复记录和 retry 状态分布。
- 建档成功企业的 `create_time/update_time/cust_first_submit_auth` 与审核事件时间差异样本。

