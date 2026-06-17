# TestHub 智能测试管理平台 - Ubuntu (WSL2) 本地部署小白教程

本教程专门为您量身定制，指导您如何在 Windows 电脑上使用 **WSL2 (Windows Subsystem for Linux)** 安装 **Ubuntu 22.04 LTS**，并在其上完成 TestHub 平台的一键部署与运行。

使用 WSL2 的好处是：**无需重装系统或配置双系统，直接在 Windows 中以极高性能运行原生的 Ubuntu，且能完美共享电脑的 16GB 内存和 SSD 固态硬盘。**

---

## 🛠️ 第一步：在 Windows 上安装 Ubuntu (WSL2)

### 1. 开启 Windows 的虚拟化与 WSL 功能
1. 在 Windows 搜索框输入 **“启用或关闭 Windows 功能”** 并打开。
2. 在弹出的列表中，勾选以下三项：
   * `适用于 Linux 的 Windows 子系统` (Windows Subsystem for Linux)
   * `虚拟机平台` (Virtual Machine Platform)
   * `Hyper-V`（若您的 Windows 是家庭版，可能没有此项，只需勾选前两项即可）
3. 点击确定，等待系统下载组件，完成后**必须重启电脑**。

### 2. 一键安装 Ubuntu 22.04 并移至非 C 盘（如 E 盘）
由于默认安装会存放在 C 盘，如果您 C 盘空间紧张，可以先以极小磁盘开销完成初始化，然后**一键无损迁移**至您的 E 盘。

1. **下载与初始化（C 盘仅临时占用很小空间）**：
   * 鼠标右键点击 Windows 的“开始”按钮，选择 **“终端(管理员)”** 或 **“PowerShell (管理员)”**。
   * 输入以下命令安装 Ubuntu 22.04：
     ```powershell
     wsl --install -d Ubuntu-22.04
     ```
   * 等待提示设置用户名（如 `testhub`）和密码（盲打输入），看到提示符 `testhub@PC-xxxx:~$` 后，代表初始化成功。
   * 输入 `exit` 退出 Ubuntu，回到 Windows 命令行。

2. **一键迁移至 E 盘**：
   * 在 Windows 命令行（PowerShell）中，先运行以下命令彻底关闭 WSL 虚拟机以释放文件占用：
     ```powershell
     wsl --shutdown
     ```
   * 在您的大容量磁盘（如 E 盘）上，创建一个存放 Linux 系统镜像的文件夹（例如 `E:\WSL\Ubuntu22`）。
   * 运行以下命令，将 Ubuntu 无损移动到 E 盘目录下：
     ```powershell
     wsl --manage Ubuntu-22.04 --move "E:\WSL\Ubuntu22"
     ```
     *(等待搬迁完成。此操作会直接将虚拟磁盘 `.vhdx` 文件转移到 E 盘，以后所有的开发数据、数据库、虚拟环境文件全都会在 E 盘增加，彻底解决 C 盘空间问题！)*
   
   > [!NOTE]
   > 如果您的 Windows 系统版本较旧，提示 `--manage` 为未知参数，可以使用以下传统导出导入法迁移：
   > 1. 关闭虚拟机：`wsl --shutdown`
   > 2. 导出备份：`wsl --export Ubuntu-22.04 E:\WSL\ubuntu22.tar`
   > 3. 注销 C 盘实例：`wsl --unregister Ubuntu-22.04`
   > 4. 导入至 E 盘：`wsl --import Ubuntu-22.04 E:\WSL\Ubuntu22 E:\WSL\ubuntu22.tar --version 2`
   > 5. 删除临时备份：`del E:\WSL\ubuntu22.tar`
   > 6. 设置默认用户：进入 Ubuntu 后修改 `/etc/wsl.conf` 新增 `[user]` 和 `default=您的用户名` 字段，以防每次登录都是 root 用户。

3. **验证与日常进入**：
   * 在 PowerShell 中输入 `wsl`，或在 Windows 开始菜单中搜索并运行 `Ubuntu 22.04 LTS`。
   * 确认能够正常登入系统，即可开始接下来的步骤！


---

## 📦 第二步：在 Ubuntu 中安装基础开发环境

进入 Ubuntu 后，复制并依次执行以下命令，完成软件源更新和 Python、Node.js、MySQL、Redis 的安装。

### 1. 更新系统包列表
```bash
sudo apt update && sudo apt upgrade -y
```
*(提示输入密码时，输入您刚才设置的 Ubuntu 密码即可)*

### 2. 安装 Python 3.12 及其虚拟环境组件
本项目推荐使用 Python 3.12。请执行以下命令通过官方源进行安装：
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev build-essential libmysqlclient-dev pkg-config -y
```

### 3. 安装 Node.js 18 及 npm
用于前端项目的依赖安装与启动：
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```
安装完成后，验证版本：
```bash
node -v # 应该显示 v18.x.x
npm -v  # 应该显示 9.x.x 或 10.x.x
```

### 4. 安装 MySQL 8.0 并初始化
1. 安装 MySQL 服务端：
   ```bash
   sudo apt install mysql-server -y
   ```
2. 启动 MySQL 服务：
   ```bash
   sudo service mysql start
   ```
3. 配置 MySQL root 密码并创建项目的 `testhub` 数据库：
   ```bash
   # 以管理员身份免密登录 MySQL
   sudo mysql
   ```
   在打开的 `mysql>` 终端中，**一行一行**执行以下 SQL 语句（注意将 `123456` 替换为您想设置的数据库密码）：
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';
   CREATE DATABASE testhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   FLUSH PRIVILEGES;
   EXIT;
   ```

### 5. 安装 Redis 并配置密码
因为平台后端配置了默认带密码的 Redis 链接，所以我们需要为 Redis 配置密码：
1. 安装 Redis：
   ```bash
   sudo apt install redis-server -y
   ```
2. 启动 Redis 服务：
   ```bash
   sudo service redis-server start
   ```
3. 将 Redis 密码设置为 `1234`（与项目 `settings.py` 默认配置保持一致）：
   ```bash
   sudo sed -i 's/# requirepass foobared/requirepass 1234/' /etc/redis/redis.conf
   sudo service redis-server restart
   ```

---

## 📂 第三步：将项目代码导入 Ubuntu

为了获得极佳的读写性能，强烈建议将项目文件放在 WSL 的 Linux 原生系统目录下（例如 `~/projects/`），而不是 Windows 挂载的目录下（如 `/mnt/e/...`）。

### 方法 A：使用 Git 直接从 GitHub 克隆（推荐）
1. 在 Ubuntu 中创建项目存放目录：
   ```bash
   mkdir -p ~/projects
   cd ~/projects
   ```
2. 从您的 GitHub 仓库克隆代码：
   ```bash
   git clone https://github.com/1103753960wjm-creator/AutoTest.git
   cd AutoTest
   ```

### 方法 B：直接拷贝您当前 Windows 上的代码到 Ubuntu 中
如果您不想通过网络拉取，可以直接在 Ubuntu 中将 Windows 的 E 盘文件复制过去：
```bash
mkdir -p ~/projects
# 复制 E 盘对应文件夹的所有内容（需要一两分钟，请耐心等待）
cp -r /mnt/e/testhub_platform-main/testhub_platform-main ~/projects/AutoTest
cd ~/projects/AutoTest
```

---

## 🐍 第四步：配置并启动后端服务

现在，我们已经在 `~/projects/AutoTest` 目录下了。

### 1. 创建并激活 Python 虚拟环境
```bash
python3.12 -m venv venv
source venv/bin/activate
```
*(激活后，命令行开头会出现 `(venv)` 标识)*

### 2. 安装 Python 依赖包
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置环境变量
1. 复制环境配置模板：
   ```bash
   cp .env.example .env
   ```
2. 编辑 `.env` 文件来填入您刚才设置的数据库密码：
   ```bash
   nano .env
   ```
   * 在编辑器中，使用上下键找到 `DB_PASSWORD=your-database-password` 这一行。
   * 修改为您设置的数据库密码，例如：`DB_PASSWORD=123456`
   * 同时找到 `REDIS_URL=redis://127.0.0.1:6379/0`，将其修改为带密码的连接：`REDIS_URL=redis://:1234@127.0.0.1:6379/0`
   * 按下 `Ctrl + O`，回车保存；按下 `Ctrl + X` 退出编辑器。

### 4. 执行数据库迁移与初始化
依次在命令行中运行以下 6 行命令：
```bash
# 1. 基础数据迁移
python manage.py makemigrations
python manage.py migrate

# 2. 数据工厂数据迁移
python manage.py makemigrations data_factory
python manage.py migrate data_factory

# 3. 初始化 UI 自动化定位策略
python manage.py init_locator_strategies

# 4. 初始化 App 自动化组件库
python manage.py load_component_pack
```

### 5. 创建管理员（超级用户）账号
运行以下命令，按提示输入您的**用户名、邮箱、密码**（密码同样是盲打，需要输入 8 位以上且不要太简单）：
```bash
python manage.py createsuperuser
```

### 6. 运行后端服务
```bash
python manage.py runserver 0.0.0.0:8000
```
*(后端服务启动成功，会占用当前终端窗口，日志会在这里实时输出。)*

---

## ⚡ 第五步：配置并启动前端服务

由于后端服务占用了当前的终端，我们需要新建一个 Ubuntu 窗口来运行前端。

### 1. 打开一个新终端窗口
* 在 Windows 终端工具中，点击右上角 `+` 号下拉菜单，选择 `Ubuntu-22.04` 打开一个新标签页。
* 或者在 Windows 中重新打开一个 `Ubuntu` 快捷方式。

### 2. 进入项目前端目录
```bash
cd ~/projects/AutoTest/frontend
```

### 3. 安装前端依赖
```bash
npm install
```

### 4. 启动前端开发服务器
```bash
npm run dev
```
启动成功后，控制台会输出类似如下的地址：
```bash
  VITE v4.4.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

## 🎉 第六步：在 Windows 浏览器中访问！

现在，前后端服务全部启动成功。虽然它们在 Ubuntu 虚拟机中运行，但在 Windows 上您可以通过浏览器直接访问：

* **前端系统地址（主入口）**: [http://localhost:3000](http://localhost:3000)
  *(使用您在第四步第 5 小节中创建的超级用户账号即可登录)*
* **后端 Django 管理后台**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
* **接口 API 文档 (Swagger)**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

---

## 💡 常用维护与重启指令

由于 WSL2 在您电脑关机时会自动关闭，下次开机您只需要输入以下指令启动对应服务：

1. **启动 MySQL 和 Redis 服务**：
   ```bash
   sudo service mysql start
   sudo service redis-server start
   ```
2. **启动后端程序**：
   ```bash
   cd ~/projects/AutoTest
   source venv/bin/activate
   python manage.py runserver
   ```
3. **启动前端程序**：
   ```bash
   cd ~/projects/AutoTest/frontend
   npm run dev
   ```
