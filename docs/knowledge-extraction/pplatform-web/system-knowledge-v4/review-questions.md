# v4 待复核问题

提取日期：2026-08-18。关系一律 `proposed`。查询范例 `verification.status: PENDING_VALIDATION`，未在目标库逐条执行。

## 脏值与字典冲突

1. **`cust_change_record.status`**  
   代码写入 `CUST_CHECK_*`。画像另有 `1`、`returnCust-*`。问数只认 `CUST_CHECK_*`。若生产仍有短名 `PASS`，需再核对画像分组是否截断。

2. **两套开通字典**  
   - 租户产品 `tenant_product.open_status`：`Y` / `P` / `N`  
   - 企业申请 `cust_auth_application.open_status`：`OPENED` / `OPENING` / `NOT_OPENED`  
   项目关系开通字段是 `project_open_status`（同样 Y/P/N），不是 `open_status`。

3. **`ca_fee_order.order_status`**  
   注释为 `PENDING/PAID/CLOSED/EXPIRED`，画像含 `PAIDING`、`UNPAID`。后者不纳入正式口径。

4. **`client_api_sync_error`**  
   2161 行全部 `enable=N`。不能把该表当前数据解释为待重试队列。

5. **`cust_user_rel`**  
   仅 1 行。人员问数禁止以其为事实表。

## 低置信度关系

- `cust_project_rel.project_id` 是 `tenant_project.id` 的字符串，JOIN 需 CAST；方言待绑定后确认。
- `ca_fee_order.company_id` 与 `ca_fee_company.id` / `cust_company_info.id` 的对齐未做画像 JOIN 验证。
- 运营对接人 B / 风控 B 可能是 JSON 数组，不能当等值 JOIN 主路径。
- `op_contact_a` = `operation_user.operation_id` 仅为代码路径 proposed。

## 口径冲突（包内已写）

- 有效企业：严格 `BUILD_SUCCESS+EFFECT` vs 部分 Mapper 含 `CUST_CHANGE+CHANGE`。未说明时用严格口径。
- 建档成功时间：无统一审核通过时间，不得用 `create_time`。
- `rule_status`（资金规则）与 `project_status`（租户项目 `0/1/2`）不得混用。

## 未提取（目录已标，不成单元）

清分 / 交e保额度（apaas 无本地表）、工作流引擎内部表、SSO / Job / 影像 / 低代码 / 加解密、菜单 / 短链 / 迁移日志 / 问卷过程、邀请记录 grain、`cust_change_cfg` 配置项本身。

绑定数据源 13 后应重跑范例 SQL，通过后再把对应 pattern 的 `verification.status` 升级；在此之前不要写 `executed: true`。
