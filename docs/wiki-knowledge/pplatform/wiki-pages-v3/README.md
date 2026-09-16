# pplatform wiki-pages-v3（预览语料）

> 日期：2026-09-14 · 状态：**效果预览，未切运行时**  
> 不修改 `wiki-pages/`（v1）与 `wiki-pages-v2/`。不要把 `KNOWLEDGE_WIKI_PAGES_DIRS` 指到本目录，除非明确切流。

组织与生成纪律（后续场景必须同一套）：[`Wiki知识提取规范指南-v1.md` §11.4](../../Wiki知识提取规范指南-v1.md)。运行时 hop / 切流门槛：[`问数知识链路契约.md`](../../问数知识链路契约.md)。

## 已落地场景

企业与认证：

1. [[company_build]] — 企业建档（主档 `cust_company_info`）
2. [[company_contact]] — 经办人与联系人（主档 `cust_person_info`）
3. [[company_change]] — 企业变更（主档 `cust_change_record`）
4. [[oper_change]] — 运营人员变更（主档 `cust_oper_change_record`）
5. [[ca_cert]] — CA 证书认证（主档 `ca_certification_info`）
6. [[ca_fee]] — CA 证书收费（主档 `ca_fee_company`）

产品与项目：

7. [[product_activation]] — 企业产品开通（主档 `cust_auth_application`）
8. [[company_role]] — 企业角色与端口（主档 `cust_role_info`）
9. [[platform_product]] — 平台产品配置（主档 `platform_product`）
10. [[tenant_product]] — 租户通用产品（主档 `tenant_product`）
11. [[interworking_product]] — 互通产品（主档 `tenant_interworking_product`）
12. [[tenant_project]] — 租户项目（主档 `tenant_project`）
13. [[wechat_project_stats]] — 企微立项统计（主档 `wechat_project_approval_apply`）
14. [[project_online_approval]] — 项目上线审批（主档 `tenant_project_approval`）
15. [[company_project]] — 企业项目绑定（主档 `cust_project_rel`）

账户 / 渠道 / 协议：

16. [[bank_account]] — 企业银行账户（主档 `cust_account_info`）
17. [[company_group]] — 企业集团关系（主档 `cust_group_rel`）
18. [[channel_access]] — 渠道接入（主档 `cust_access_secret`，含 SFTP）
19. [[authorization]] — 授权协议（主档 `authorization_agreement`）

租户与运营：

20. [[tenant_config]] — 租户配置（主档 `tenant_setting_config`，含短链与异步任务）
21. [[tenant_migration]] — 租户迁移（主档 `tenant_migarory_log`）
22. [[funding_rules]] — 资金规则（主档 `funding_rule_info`）
23. [[company_survey]] — 问卷与学习活动（主档 `cust_company_survey_state`）

`cust_company_info` 在建档是主档，在其余多数场景里是身份或状态源。表页与库列对齐（含创建/更新时间等 always 列）；场景窗划分见各表页「场景字段划分」。catalog 只是生成基线，运行时只读 wiki。目录见 [_index.md](_index.md)。

## page-plan 未独立成问数场景

| topic | 原因 |
|---|---|
| 微信生态/小程序/扫脸 | 计划无表；扫脸落在联系人认证字段 / CA |
| 外部渠道与银行对接 | 计划无表；渠道密钥见 [[channel_access]] |
| DBAss/SSO 登录与通道 | `open_sso_channel` 无业务写入；登录不靠本库主档 |
| 平台事件监听与同步 | `client_api_sync_error` 是内部重试队列 |
| 平台内部服务对接 | `lc_sql_init_log` 休眠 |
| 数据权限与组织 | `org_manage` 库空；运营人员并入 [[oper_change]] |
| 自动审核与工作流 | 落库主档是企业产品开通 [[product_activation]]，不是独立审核表 |

休眠/空表在对应场景正文里点过，不建独立页：`cust_user_rel`、`cust_auth_application_config`、`cust_app_channel_config`、`cust_message_send_policy`、`tenant_migarory_log_bak`、`tenant_project_approval_flow_comment`、`ca_cfca_upgrade_report`。
