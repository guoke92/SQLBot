<p align="center"><img src="https://resource-fit2cloud-com.oss-cn-hangzhou.aliyuncs.com/sqlbot/sqlbot.png" alt="SQLBot" width="300" /></p>
<h3 align="center">基于大模型和 RAG 的智能问数系统</h3>

<p align="center">
  <a href="https://trendshift.io/repositories/14540" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14540" alt="dataease%2FSQLBot | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

<p align="center">
  <a href="https://github.com/dataease/SQLBot/releases/latest"><img src="https://img.shields.io/github/v/release/dataease/SQLBot" alt="Latest release"></a>
  <a href="https://github.com/dataease/SQLBot"><img src="https://img.shields.io/github/stars/dataease/SQLBot?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/dataease/SQLbot"><img src="https://img.shields.io/docker/pulls/dataease/sqlbot?label=downloads" alt="Download"></a><br/>
</p>

<p align="center">
  <a href="README.md"><img alt="中文(简体)" src="https://img.shields.io/badge/中文(简体)-d9d9d9"></a>
  <a href="/docs/README.en.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
</p>
<hr/>


AI智能问数是一款基于大语言模型和 RAG 的智能问数系统，由 DataEase 开源项目组匠心出品。借助 AI智能问数，用户可以实现对话式数据分析（ChatBI），快速提炼获取所需的数据信息及可视化图表，并且支持进一步开展智能分析。

本仓库在上游 SQLBot 上继续开发。公开镜像 `dataease/sqlbot` 不包含这里的问数 Wiki、统一对话图、目录画像和当前的服务器打包发布。维护、操作和发布细节见 [交接文档](docs/交接文档.md)。

## 工作原理

<img width="1153" height="563" alt="image" src="https://github.com/user-attachments/assets/8bc40db1-2602-4b68-9802-b9be36281967" />

## 核心优势

- **开箱即用**：仅需简单配置大模型与数据源，无需复杂开发，即可快速开启智能问数；依托大模型自然语言理解与 SQL 生成能力，结合 RAG 技术，实现高质量 Text-to-SQL 转换。
- **安全可控**：提供工作空间级资源隔离机制，构建清晰数据边界，保障数据访问安全；支持细粒度数据权限配置，强化权限管控能力，确保使用过程合规可控。
- **易于集成**：支持多种集成方式，提供 Web 嵌入、弹窗嵌入、MCP 调用等能力；能够快速嵌入到 n8n、Dify、MaxKB、DataEase 等应用，让各类应用快速拥有智能问数能力。
- **越问越准**：支持自定义提示词、术语库配置，可维护 SQL 示例校准逻辑，精准匹配业务场景；高效运营，基于用户交互数据持续迭代优化，问数效果随使用逐步提升，越问越准。
- **问数 Wiki**：把表、口径、枚举和关系整理成可召回的页面。Wiki 维护对话只提案，确认后才写入页面。
- **过程可核对**：一次提问的思考链、SQL 和结果写在同一条执行记录里，可在智能问数管理中回看。

## 支持的大模型服务商

| 服务商 | API 兼容 |
|--------|----------|
| 阿里云百炼 | OpenAI 兼容 |
| 千帆大模型 | OpenAI 兼容 |
| DeepSeek | OpenAI 兼容 |
| 腾讯混元 | OpenAI 兼容 |
| 讯飞星火 | OpenAI 兼容 |
| Gemini | OpenAI 兼容 |
| OpenAI | 原生 |
| Kimi | OpenAI 兼容 |
| 腾讯云 | OpenAI 兼容 |
| 火山引擎 | OpenAI 兼容 |
| MiniMax | OpenAI 兼容 |
| 通用 OpenAI 兼容 | 自定义 |

## 快速开始

配置在仓库根目录 `.env`（不入库）。密钥、数据库密码和管理员初始密码以该文件为准，单独交接。

### 本地开发

需要 Python 3.11、Node、pnpm，以及本机 PostgreSQL。启动和测试使用 `backend/venv`。

```bash
./sqlbot-dev.sh start all
./sqlbot-dev.sh status
```

- 页面：http://localhost:5173
- 接口：http://localhost:8000 （文档 http://localhost:8000/docs ）
- 日志：`data/logs/backend-dev.log`、`data/logs/frontend-dev.log`

### 服务器发布

在已准备好根目录 `.env` 的机器上打包，再在 Linux 服务器上安装到 `/opt/sqlbot`：

```bash
./package.sh
```

把生成的 `sqlbot-server-*.tar.gz` 放到服务器 `/tmp`，用 root 执行包内 `init.sh`。服务器需要 PostgreSQL、`uv`、`npm`、nginx 和 systemd。对外入口是 nginx `3001`；后端 `8000`、MCP `8001`、图表服务 `3000` 仅本机。步骤、健康检查和升级注意见 [交接文档](docs/交接文档.md)。

`docker run dataease/sqlbot`、1Panel 应用商店和上游离线包安装的是公开镜像，不能代替上面的发布。

### 访问方式

- 本地开发：http://localhost:5173
- 当前服务器部署：http://&lt;服务器&gt;:3001/
- 管理员账号和初始密码见该环境 `.env` 的 `DEFAULT_PWD`

### 联系我们

如你有更多问题，可以加入我们的技术交流群与我们交流。

<img width="180" height="180" alt="contact_me_qr" src="https://github.com/user-attachments/assets/a4b84255-dbe1-43eb-b73f-2bc4ee13f037" />

## UI 展示

  <tr>
    <img alt="q&a" src="https://github.com/user-attachments/assets/55526514-52f3-4cfe-98ec-08a986259280"   />
  </tr>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=dataease/sqlbot&type=Date)](https://www.star-history.com/#dataease/sqlbot&Date)

## 飞致云旗下的其他明星项目

- [DataEase](https://github.com/dataease/dataease/) - 人人可用的开源 BI 工具
- [1Panel](https://github.com/1panel-dev/1panel/) - 现代化、开源的 Linux 服务器运维管理面板
- [MaxKB](https://github.com/1panel-dev/MaxKB/) - 强大易用的企业级智能体平台
- [JumpServer](https://github.com/jumpserver/jumpserver/) - 广受欢迎的开源堡垒机
- [Cordys CRM](https://github.com/1Panel-dev/CordysCRM) - 新一代的开源 AI CRM 系统
- [Halo](https://github.com/halo-dev/halo/) - 强大易用的开源建站工具
- [MeterSphere](https://github.com/metersphere/metersphere/) - 新一代的开源持续测试工具

## License

本仓库遵循 [FIT2CLOUD Open Source License](LICENSE) 开源协议，该许可证本质上是 GPLv3，但有一些额外的限制。

你可以基于 AI智能问数的源代码进行二次开发，但是需要遵守以下规定：

- 不能替换和修改 SQLBot 的 Logo 和版权信息；
- 二次开发后的衍生作品必须遵守 GPL V3 的开源义务。

如需商业授权，请联系 support@fit2cloud.com 。
