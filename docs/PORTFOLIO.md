# 简历与面试说明

## 项目名称

**DataPilot — Web-based Autonomous Data Analysis Agent**

## 简历描述（可直接改写）

基于 MIT 开源项目 DeepAnalyze 完成数据分析智能体的产品化复现与二次开发：构建 Next.js + FastAPI 三栏式 Web 工作台，支持多格式数据上传、流式结构化推理、Python 执行、产物预览和 Markdown/PDF 导出；抽象 OpenAI 兼容模型层，实现 mock、远程 API 与未来 vLLM 自托管权重的无缝切换；补充 Nginx/Docker Compose 编排、安全配置、Pytest 与 GitHub Actions，使项目可在无 GPU/无权重情况下完整演示并可继续扩展为真实推理服务。

## 建议强调的个人工作

- 将研究型仓库整理为可运行、可测试、可部署的独立公开项目。
- 保留并整理 DeepAnalyze WebUI v2 界面，同时完成前后端配置解耦。
- 设计服务端 provider 配置与 Secret 管理，支持通用 OpenAI 兼容 API。
- 修复上游 mock 流未结束造成的循环请求问题，完成 CSV 到报告的端到端验证。
- 增加文件路径、上传、代理和执行环境安全控制。
- 建立 Docker Compose 与 GitHub Actions 自动验证流程。

## 诚实边界

- DeepAnalyze-8B 的训练、论文与模型权重不是本人产出。
- 本人的贡献是开源复现、Web 产品化、工程架构、部署与质量保障。
- mock 证明系统链路可运行，不代表真实模型分析质量；真实质量取决于所连接的模型。

## 面试演示脚本

1. 打开 Web 工作台，说明三层架构和模型解耦设计。
2. 上传一个 CSV，展示会话工作区和文件预览。
3. 提问后展示流式标签解析和报告生成。
4. 展示 `.env.example`，解释如何换成远程 API 或未来 GPU vLLM。
5. 展示 GitHub Actions、测试和安全说明。

建议把“未来 GPU 权重部署”明确写成 roadmap，等真实完成并留有可复现命令、显存配置和验证结果后再更新为已完成。
