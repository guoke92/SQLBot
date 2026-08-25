# pplatform-system-business-data-v11

- 源仓库：`/Users/fanjunwei/IdeaProjects/pplatform-web`
- 源提交：`ee434954e465713176e5bd52119eedde5ebe531b`
- 提取技能：`.cursor/skills/knowledge-extraction`
- 提取方式：**全新提取**，未参考当前仓库已存在的 v2-v10 知识包内容；只从 pplatform-web 源码、Mapper/Service/Controller/Provider/DO/枚举，以及源码项目 docs 下的设计文档提取。
- 包类型：KnowledgePackageV2 场景单元包（`schema_version: "2.0"`）
- 状态：**全量覆盖**，无 `COVERAGE_GAP`

## 单元清单（24 个）

```text
funding-rule                  资金方规则配置与查询
ca-fee                        CA 服务费收费与缴费
exception-resolution          资金方异常解析及建议维护
enterprise-onboarding         企业建档与客户录入
tenant-product-lifecycle      租户产品生命周期
project-approval              项目上线审批
tenant-project-lifecycle      租户项目生命周期
ca-certification              CA 认证
enterprise-certification      企业认证
enterprise-change             企业变更
company-group                 企业集团/关联关系
enterprise-auxiliary          企业辅助信息
survey                        问卷调研
customer-config               客户配置
company-product-auth          企业产品授权
interworking                  互联互通
openapi-access                OpenAPI 访问
user-account                  用户与企业账户
op-user-coverage              运营用户覆盖
tenant-setting                租户配置
project-file                  项目文件
wechat-project-approval       企微项目审批
project-code                  项目编码与邀请
org-manage                    机构管理（休眠登记）
```

## 校验

```bash
cd /Users/fanjunwei/Projects/SQLBot
backend/venv/bin/python scripts/knowledge-package.py scan --strict docs/knowledge-extraction/pplatform-web/system-knowledge-v11
backend/venv/bin/python scripts/knowledge-package.py decompose docs/knowledge-extraction/pplatform-web/system-knowledge-v11
```

当前结果：

- `scan --strict`：通过，`blocking=0`、`advisory=0`
- `coverage.gaps=0`
- `decompose`：`merge_conflicts=0`、`stub_nodes=0`、`concepts_anchored=35/35`

## 休眠表

- `funding_party_rule_cfg/detail/front`
- `tenant_product_ext_field/form`
- `org_manage`

以上由 `extract-callgraph.py` 标记为无入口调用链，按 skill 保留为 `inactive: true + fields: []`，仅登记不参与问数。

## 关键证据来源

- 源码：各模块 DO / Controller / Application / DomainService / Dao / Provider / 枚举
- 文档：源码项目 `docs` 下 V1.30/V1.31/V1.32 相关设计文档
