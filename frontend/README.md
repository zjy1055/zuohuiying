# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## 项目启动说明

### 前置条件
确保已安装Node.js LTS版本。如果未安装，可以通过以下方式安装：

```bash
winget install OpenJS.NodeJS.LTS --accept-source-agreements
```

### 安装依赖

**重启系统后的简化方法（推荐）：**

如果系统已重启，直接在frontend目录下执行：

```powershell
cd d:\zuohuiying-main\frontend
npm install
```

**如果未重启系统，使用完整路径执行：**

```powershell
cd 'C:\Program Files\nodejs' ; .\node node_modules\npm\bin\npm-cli.js install --prefix 'd:\zuohuiying-main\frontend'
```

**注意：** 安装完Node.js后，重启系统可以解决路径问题，使node和npm命令在任何目录下直接可用。这是因为系统重启后，所有新的PowerShell会话都会加载更新后的环境变量。

### 启动前端开发服务器

**重启系统后的简化方法（推荐）：**

```powershell
cd d:\zuohuiying-main\frontend
npm run dev
```

**如果未重启系统，使用完整路径执行：**

```powershell
cd 'd:\zuohuiying-main\frontend' ; & 'C:\Program Files\nodejs\node' node_modules\vite\bin\vite.js
```

服务器启动后，可通过 http://localhost:5173/ 访问前端应用。

### 后端服务配置

前端项目已配置API代理，将所有 `/api` 请求代理到 http://127.0.0.1:8000 后端服务。请确保后端服务已启动。

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).
