# Quartz 4 工作流（本地 Markdown -> Git -> Vercel/Netlify -> 静态站）

## 1) 本地写作与预览

```powershell
# 安装依赖（已执行过可跳过）
npm install --engine-strict=false

# 本地预览（默认 http://localhost:8080）
npm run dev
```

- 把笔记放在 `content/` 下（支持多级目录）。
- 例如：`content/2026/我的第一篇笔记.md`

## 2) 绑定你自己的 Git 仓库（GitHub 或 GitLab）

先在 GitHub/GitLab 新建一个空仓库，然后执行：

```powershell
# 把你的仓库地址替换成实际 URL
git remote add origin <YOUR_GIT_REPO_URL>

# 首次推送
git add .
git commit -m "chore: initialize quartz workflow"
git push -u origin main
```

后续日常发布：

```powershell
git add content
git commit -m "docs: update notes"
git push
```

## 3) Vercel 自动拉取构建

本项目已包含 `vercel.json`，构建配置如下：

- Build Command: `npx quartz build`
- Output Directory: `public`

在 Vercel 里导入该 Git 仓库后，推送到 `main` 会自动部署。

建议在 Vercel 项目环境变量里设置：

- `QUARTZ_BASE_URL=你的正式域名`（不带 `https://`，例如 `notes.example.com`）

## 4) Netlify 自动拉取构建

本项目已包含 `netlify.toml`，构建配置如下：

- Build command: `npx quartz build`
- Publish directory: `public`
- Node version: `22.12.0`

在 Netlify 里连接该 Git 仓库后，推送到 `main` 会自动部署。

建议在 Netlify 项目环境变量里设置：

- `QUARTZ_BASE_URL=你的正式域名`（不带 `https://`）

## 5) baseUrl 自动处理说明

`quartz.config.ts` 已配置自动推断 `baseUrl`：

1. `QUARTZ_BASE_URL`
2. `VERCEL_PROJECT_PRODUCTION_URL`
3. `URL`（Netlify）
4. `DEPLOY_PRIME_URL`（Netlify）
5. 回退到 `localhost:8080`

这意味着即使不手动改配置，也能先跑起来；上线时建议显式设置 `QUARTZ_BASE_URL` 以确保 sitemap/RSS 域名稳定。
