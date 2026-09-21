---
type: concept
title: 全库表骨架
page_key: catalog_summary
belong: concepts
status: draft
recall: false
aliases: [Catalog Summary, 表目录, 库表一览]
sources: ['database_schema:lowcode_pplatform']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
---

# 全库表骨架

全库表骨架。每表一行：- 表名: 业务定位(核心列/主键/状态)。大宽表与主档保留较全业务维度，小表/关联表/日志表极致精炼。

## ca（2）

- ca_certification_info: 企业CA证书认证记录(企业cust_id, 批次号, 实名JSON)
- ca_cfca_upgrade_report: CFCA证书升级上报(企业ID/统码, 角色, 任务task_id, 异常内容)

## ca_fee（4）

- ca_fee_company: [核心主档] 企业CA服务费管理(企业名称, 统码, 所属租户, 锁定年费标准, 缴费状态PAID/UNPAID, 服务起止日, 首次锁定项目ID)
- ca_fee_order: [核心主档] CA服务费订单与支付(订单号order_no, 企业ID/统码, 触发项目ID, 租户ID, 角色, 支付状态/金额/渠道)
- ca_fee_project_config: 项目级CA收费配置(项目ID, 租户ID, 年费标准, 缴费渠道)
- ca_fee_special_config: 特殊企业年费白名单(项目ID, 统码, 自定年费标准)

## cust（31）

- cust_access_secret: OpenAPI接入秘钥(应用channel, 凭证公私钥)
- cust_account_info: [核心主档] 客户银行账号(账号, 户名, 开户行/联行号, 省市代码, 默认标识, 账户状态)
- cust_app_channel_config: 应用与渠道映射配置(app_id, app_tenant_code(渠道码), enable)
- cust_auth_application: 客户产品开通记录(产品编码, 开通状态, 管理员)
- cust_auth_application_config: 客户产品开通个性配置(企业cust_id, 签署方式)
- cust_build_record: 建档同步中台日志(企业ID, 中台企业ID, 状态)
- cust_certification_info: 企业认证核验记录(企业code, 认证类型, 核验状态)
- cust_change_cfg: 企业变更项配置(变更项item_code, 材料说明)
- cust_change_record: 企业信息变更轨迹(企业ID/名称, 变更类型, 流程号)
- cust_company_info: [核心主档大宽表] 客户企业信息主表(企业code, 统码certification_no, 名称/曾用名, 法人, 认证方式identify_style, 录入方式cust_build_type, 客户/认证状态, 建档时间create_time, 省市地址, 开户账号)
- cust_company_lifecycle_info: 企业冻结/解冻留痕(企业ID/code, 冻结原因及附件)
- cust_company_survey_state: 问卷星活动访问状态(企业ID, 首访用户/时间, 抽奖状态)
- cust_company_survey_whitelist: 问卷调研企业白名单(企业ID, 企业名称)
- cust_config_mapping: 内外编码映射字典(内部编码, 外部编码, 渠道)
- cust_customized_product: 快捷入口导航配置(企业cust_id, 产品名, url)
- cust_group_rel: 集团成员企业层级树(成员企业ID, 父/根企业ID, level, 状态)
- cust_head_company_info: 总公司主档执照(统码, 全称/简称, 法人, 注册地址)
- cust_interworking_product: 跨租户产品授权(企业cust_id, 租户ID, 产品编码, 状态)
- cust_invite_info: 企业建档邀请记录(客户ID, 联系人/手机, 渠道码, 进度)
- cust_message_send_policy: 消息推送开关配置(场景码scenes_type, 消息类型, 开关)
- cust_oper_change_record: 运营对接人变更记录(企业ID, 变更前后运营人员, 原因)
- cust_person_info: [核心主档] 客户联系人与经办人档案(姓名, 手机/邮箱, 证件类型/号码, 建档经办人, 关联用户ID, 实名状态)
- cust_project_code_record: 项目邀请码输入记录(企业ID, 用户ID, 渠道码, 验证状态)
- cust_project_pushcust: SSO跳转默认项目映射(来源/目标SSO渠道, 默认项目ID)
- cust_project_rel: [核心关联大宽表] 客户项目关联表(企业code, 项目ID, 产品ID, 租户code, 渠道码channel_code, 角色(核心/供应商), 关联状态status, 配置模式config_model, 展示标记)
- cust_role_info: 企业产品角色关联(企业code, 产品角色, 状态)
- cust_setting_config: 认证规则与协议配置(变更审核开关, 协议文本, 授权书模式)
- cust_sftp: 客户SFTP对账连接信息(host, 用户名, 渠道)
- cust_shareholder_info: 客户股东出资信息(企业code, 股东名, 证件号, 出资额)
- cust_survey_answer: 问卷调研答卷明细(问卷编码, 企业ID, 题号, 选项内容)
- cust_user_rel: 用户与企业角色归属(用户ID, 企业ID, 客户角色)

## funding（4）

- funding_exception_resolution: 资方报错解析建议(资方标识, 产品code, 报错关键字, 建议)
- funding_rule_detail: 资方准入规则明细(规则头ID rule_info_id, 资方标识, 规则键值)
- funding_rule_front_cfg: 资方规则前端元数据(产品code, 规则层, 前端字段key)
- funding_rule_info: [核心主档] 资方准入规则头(资方标识funding_party_mark, 资方名称, 产品编码product_code, 规则状态ACTIVE/INACTIVE/PENDING, 版本号)

## platform（3）

- platform_product: [核心主档] 平台产品基础配置(平台编码, 产品编码product_code, 产品名称, 默认菜单, 多项目/多角色支持)
- platform_product_client: 平台产品客户端配置(产品ID, 客户端类型, 跳转url, 状态)
- platform_product_cust_role: 平台产品企业角色字典(产品编码product_code, 企业角色编码)

## project（1）

- project_file_info: 项目运营文档管理(项目ID, 标题, 模块类型)

## tenant（18）

- tenant_interworking_product: 租户互通产品授权与额度(租户ID, 产品ID, 状态, 融资额度/期限上限)
- tenant_interworking_project: 租户互通产品项目绑定(租户ID, 产品ID, 项目ID)
- tenant_migarory_log: 租户项目迁移流水(产品编码, 批次号, 状态, 请求报文)
- tenant_migarory_log_bak: 租户迁移日志备份(产品编码, 批次号, 状态)
- tenant_product: [核心主档] 租户引入产品配置(租户ID, 平台产品ID, 产品名称/类型, 目标客群, 融资额度/期限上限, 增信措施)
- tenant_product_menu: 租户产品功能菜单(产品code, 角色, 菜单ID)
- tenant_product_menu_res: 租户产品菜单按钮权限(产品code, 菜单ID, 按钮资源ID)
- tenant_project: [核心主档大宽表] 租户项目全量运营配置(项目ID/编码, 名称, 渠道码channel_code, 平台产品编码, 项目状态, 企微审批号wechat_audit_no, 立项审批通过时间, 运营/查验/风控对接人A/B及组别, 方案/业务经理, 首笔落地时间, 自定义字段一/二/三)
- tenant_project_approval: [核心主档] 租户项目审批主单(审批号approval_no, 关联项目code, 审批类型, 工作流状态, 方案经理, 企微号sp_no, 简易/低风险)
- tenant_project_approval_business_info: 审批项目业务推送详情(产品编码, 来源系统, 配置版本, 费率规则)
- tenant_project_approval_flow: 项目审批流程节点实例(关联审批单, 节点编码/名称/顺序, 节点状态, 审批人)
- tenant_project_approval_flow_comment: 项目审批评论抄送(关联审批单, 备注内容, 抄送人)
- tenant_project_approval_flow_config: 项目审批流程模板配置(流程编码flow_code, 节点编码/名称, 顺序)
- tenant_project_approval_flow_credit: [核心主档] 项目审批授信额度明细(核心企业/资方ID及名称, 授信额度, 集团额度标识, 额度起止日, 循环标识)
- tenant_project_approval_flow_file: 项目审批影像附件(业务key, 影像分类, 文件名/ID/url, 审批节点)
- tenant_project_approval_flow_node: 项目审批节点操作记录(关联审批单, 节点编码, 操作/审批类型, 操作人)
- tenant_setting_config: [核心配置大宽表] 贴牌租户主配置(租户code/名称, 平台名, 统码, 接入模式access_mode(STANDARD/DIRECT_INIT), 客服电话, 小程序/公众号, 默认项目, 协议签署配置, 业务开关)
- tenant_setting_config_share: [核心配置大宽表] 共享租户配置(租户名称, 平台名, 统码, 客服信息/二维码, 小程序/公众号, 域名/展示配置)

## wec（2）

- wec_project_cust_operation_rel: 微企链企业运营对接(关联ID, 企业ID, 角色, 运营对接人A/B。历史关系)
- wec_project_operation_rel: 微企链历史关联运营配置(历史项目ID, 运营/查验/风控对接人。新配置已收敛至tenant_project)

## wechat（2）

- wechat_project_approval_apply: [核心主档大宽表] 企微立项审批流申请(企微审批号sp_no, 立项名称, 主项目/上线名, 资方全称/分支行, 核心企业全称, 产品类型, 审批时间/类型)
- wechat_project_approval_field_history: 企微立项字段变更历史(立项apply_id, 审批号sp_no, 字段名/标签, 变更前后值)

## other（11）

- argeement_migratory_record: 协议电子化迁移记录(客户ID, 产品编码, 协议名/编号, 状态)
- async_io_task: 异步任务处理日志(任务号task_no, 任务名称/类型, 发起人, 状态)
- authorization_agreement: 管理员授权确认书签署表(企业ID/名称, 管理员ID/姓名, 授权状态)
- client_api_sync_error: API调用失败重试队列表(服务类名, 重试次数)
- gpt_learn_poster_log: 审核卡片引流埋点日志
- lc_sql_init_log: 底层插件SQL初始化记录
- migratory_user_record: 账号体系迁移记录(用户ID user_id, 登录状态is_login)
- open_sso_channel: 开放登录SSO渠道配置(渠道码channel_code, tenant_code/db_tenant_code产融租户标识, appId, channel_kind LOCAL_SYS/STANDARD, SSO clientId/secret)
- operation_user: 运营人员基础信息(姓名, 运营中台ID operation_id, 组别, 状态)
- org_manage: 组织机构行政层级树(机构编码code, 机构名称, 机构号org_no, 状态)
- short_link: 外链短链生成与重定向(短链编号, 源长链source_url, 永久有效标识)
