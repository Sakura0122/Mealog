# Mealog 项目开发约定

## 项目概览

Mealog 是用于记录和回顾日常饮食的微信小程序，采用前后端分离结构：

- `frontend/miniapp/`：Vue 3、TypeScript、uni-app 小程序前端，使用 Wot UI、UnoCSS 和 Pinia。
- `backend/`：Python 3.14、FastAPI、SQLAlchemy 2 异步后端，使用 MySQL、RustFS（S3 兼容对象存储）和微信小程序登录。
- `backend/sql/`：MySQL 初始化及后续数据库脚本，文件按数字顺序命名。
- `prd/`：产品需求文档，页面和交互实现以产品需求及现有页面为依据。

开始修改前先阅读相关目录的现有实现。项目当前存在未提交改动时，只修改任务范围内的文件，不覆盖或回退已有改动。

## 基本原则

- 只实现用户要求的范围，优先采用项目已有的组件、工具函数、目录结构和命名方式。
- 保持改动小而集中，不顺手重构无关代码，不引入单次使用的抽象。
- 新增或修改的代码必须添加简洁、准确的中文注释，重点解释业务规则、数据转换、平台兼容处理和不易从代码本身看出的原因；不要为显然的赋值、循环或组件属性逐行写注释。
- 不编写、不新增、不修改 test 测试用例。验证功能时使用类型检查、静态检查、构建、接口启动和必要的手工验证。
- 不在代码中写入密钥、数据库密码、微信密钥或对象存储凭据；本地配置放在对应目录的 `.env`，提交前确认敏感文件未被跟踪。
- 不生成 `README.md` 或示例文档，除非用户明确要求。
- 新代码默认使用 ASCII 字符；已有中文源码、文档和用户可见文案按项目语言保持中文。

## 目录职责

后端按功能模块组织在 `backend/src/api/<module>/`：

- `router.py`：路由、参数声明和响应模型，不直接堆放复杂业务逻辑。
- `service.py`：业务流程、外部服务调用和事务内的数据处理。
- `schema.py`：Pydantic 请求和响应模型。
- `model.py`：SQLAlchemy ORM 模型。
- `backend/src/common/`：响应包装、分页、错误码和公共异常。
- `backend/src/core/`：配置、数据库、鉴权、密码和日志等基础设施。
- `backend/src/rustfs/`：对象存储客户端、文件存储和公开 URL 构造。

前端页面位于 `frontend/miniapp/src/pages/<page>/index.vue`，可复用组件位于 `src/components/`，布局位于 `src/layouts/`，组合式逻辑位于 `src/composables/`，通用函数位于 `src/utils/`。页面路由由 `@uni-helper/vite-plugin-uni-pages` 根据页面文件生成，新增页面应遵循现有目录命名并确认页面配置能被生成。

## 后端约定

- 使用 `async def` 和 `async/await` 处理异步数据库及 HTTP 调用；复用 `SessionDep` 获取 `AsyncSession`。
- API 统一挂载在 `/api` 下，模块路由使用 `APIRouter(prefix=..., tags=...)`，响应优先使用 `Result.success(...)` 或 `Result.error(...)`。
- 请求校验使用 FastAPI 参数声明和 Pydantic 模型；错误通过 `BusinessException` 与已有异常处理器返回，不在每个路由重复拼装错误响应。
- 分页接口必须直接使用公共 `PageRequest` 接收查询参数，不得在路由中重复声明同名参数后手工组装分页对象。
- 批量删除业务数据必须调用模型的 `soft_delete_by(...)`，禁止在业务代码中直接执行 `delete(...)` 或原生 `DELETE` SQL。
- 业务查询默认遵循 `BaseTable` 的软删除过滤。需要处理已删除数据时，必须显式使用已有的 `include_deleted` 查询选项，并说明原因。
- 新增业务表应继承 `BaseTable`，同步更新 `backend/sql/` 中的数据库脚本、索引和字段注释；用户归属数据必须校验当前用户权限，不能仅凭请求体中的 ID 放行。
- 外部服务（微信、RustFS 等）调用集中在对应 service 或基础设施模块，并将配置从 `src.core.config.settings` 读取。
- 后端格式与静态检查遵循 Ruff，单行长度以 `backend/pyproject.toml` 的 100 为准。

## 前端约定

- 新增 Vue 组件优先使用 `<script setup lang="ts">`；响应式状态使用 `ref`，不要使用 `reactive`。
- 按需在逻辑块或方法附近定义变量，避免在组件顶部集中堆放无关变量；新函数优先使用箭头函数，新异步逻辑优先使用 `async/await`。
- 弹窗的显示状态由弹窗组件内部维护，不通过 props 控制可见性；需要外部触发时，在组件内部使用 `ref` 并通过 `defineExpose` 暴露 `open` 方法。
- 优先复用 Wot UI（`wd-*`、`useToast`、`useDialog`）和已有组件。按钮、表单、弹窗等交互应遵循现有组件用法，并处理加载、空状态和错误状态。
- 样式优先使用项目现有 UnoCSS utility class 与 Wot UI 主题变量，禁止使用 `tw-` 前缀；不要为单个页面引入新的 CSS 框架或重复主题系统。

## API 与数据变更

- 新 API 按现有模块目录新增 `index.ts`/`type.ts`（TypeScript）或沿用目标目录已有形式；优先使用统一对象导出，不为单个请求创建重复封装层。
- 变更数据库字段、状态值、索引或软删除行为时，同时检查 ORM 模型、SQL 脚本、Pydantic schema、service 和前端调用方，避免只改一层。
- 业务时间统一使用不带时区的 `datetime` 和 MySQL `DATETIME`，按请求值原样写入并原样返回，不做 UTC 或用户时区转换。
- 文件上传只保存对象存储 key，公开 URL 通过后端统一构造；不要把本地绝对路径或凭据返回给前端。

## 常用命令

后端在 `backend/` 目录执行：

```bash
uv sync
uv run uvicorn src.main:app --reload
uv run ruff check src
uv run ruff format --check src
uv run ty check src
```

前端在 `frontend/miniapp/` 目录执行：

```bash
pnpm install
pnpm dev:mp-weixin
pnpm lint
pnpm type-check
pnpm build:mp-weixin
```

不执行或添加测试命令；若本地依赖、微信开发者工具、MySQL、微信配置或 RustFS 未准备好，应在结果中明确说明未完成的验证项。

## 完成前检查

1. 确认修改只涉及任务范围，且新增逻辑已按要求添加有意义的中文注释。
2. 检查 API 路径、响应结构、权限校验、软删除过滤和时间字段处理是否与现有约定一致。
3. 对后端运行 Ruff（必要时运行 `ty`），对前端运行 ESLint、类型检查和目标平台构建；不编写测试用例。
4. 检查 `git diff`，确认没有提交 `.env`、密钥、构建产物或无关格式化变更，并在交付说明中列出实际执行的验证命令及结果。
