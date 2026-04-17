# 问题与计划汇总

---

## 🔴 Trouble（严重问题）

> 以下问题需要**立即关注**，可能导致崩溃、数据丢失或严重用户体验问题。

### T1. SystemCompositionSnapshot 缺少 id 字段 ⛔ 已修复
- **文件**: `src/domain/snapshot/snapshots.py:124-144`
- **问题**: 所有 snapshot 都有 `id` 字段，唯独 `SystemCompositionSnapshot` 没有。导致 `update()`/`delete()`/`save()` 无法正常工作。
- **状态**: ⏳ 待修复

### T2. AppContext 允许必需服务为 None ⛔
- **文件**: `src/application/app_context.py:18-21`
- **问题**: `core_db`, `user_db`, `modules` 默认 `None`，运行时访问会 `AttributeError`
- **状态**: ⏳ 待修复

### T3. QtLogHandler.SignalEmitter 空指针崩溃 ⛔
- **文件**: `src/gui/pages/settings_page/controller.py:26-27`
- **问题**: 信号在 `_text_edit` 设置前就被连接，如果 `emit()` 先于 `setTextEdit()` 调用会崩溃
- **状态**: ⏳ 待修复

### T4. C++ 库导入失败导致应用无法启动 ⛔
- **文件**: `src/modules/miedema_module/miedema_module.py:41-44`
- **问题**: `.so` 文件缺失时整个应用无法启动，无优雅降级
- **状态**: ⏳ 待修复（C++ 模块暂不处理）

### T5. Signal 连接后从不断开（内存泄漏）⚠️
- **文件**: 多个 GUI 文件
- **问题**: `language_changed` / `theme_changed` 信号连接后从不断开，累积内存泄漏
- **涉及文件**:
  - `src/gui/background_layer/widget.py:19`
  - `src/gui/sidebar/widget.py:48`
  - `src/gui/menubar/widget.py:23`
  - `src/gui/main_window.py:87`
  - `src/gui/pages/home_page/widget.py:41`
  - `src/gui/pages/simulation_page/widget.py:92-93`
  - `src/gui/pages/settings_page/controller.py:128`
- **状态**: ⏳ 待修复

### T6. 两阶段注入导致时序耦合 ⚠️
- **文件**: `src/application/app_startup.py:85-89`, `src/application/service/module_service.py:14-20`
- **问题**: `ModuleService` 先构造后注入 repositories，如果忘记调用 `setRepositories()` 会静默失败
- **状态**: ⏳ 待修复

---

## ✅ 已解决的问题

> 代码审查中发现并修复的问题。

| # | 问题 | 修复方式 | 状态 |
|---|------|----------|------|
| 1 | 30 个文件格式问题 | `ruff format src/` | ✅ |
| 2 | `__init__.py` F401 未使用导入 | 添加 `__all__` 显式导出（11个文件）| ✅ |
| 3 | `BaseRepository` 默认空 DatabaseManager | `db_manager` 改为必需参数 | ✅ |
| 4 | simulation_page 重复创建 Settings | 改用 `context.settings` 缓存 | ✅ |
| 5 | 直接访问私有成员 `_db_manager` | 在 `UserDbService` 添加 `db_manager` property | ✅ |
| 6 | Settings 缓存不更新 | 添加 `reloadSettings()` 和 `_saveAndReload()` | ✅ |
| 7 | f-string 无占位符 | 移除多余的 `f` 前缀 | ✅ |

---

## 🟡 中等问题

> 可能导致意外行为或性能问题。

### 架构相关

| 问题 | 文件 | 说明 |
|------|------|------|
| SQL LIMIT/OFFSET 直接拼接整数 | `repositories.py:243` | 无运行时验证 |
| 批量操作用循环而非 `executemany` | `repositories.py:117`, `602` | 性能问题 |
| 游标从未关闭（资源泄漏）| `sqlite.py:107`, `postgresql.py:140` | 依赖连接关闭 |
| 无线程安全机制 | `db_manager.py` | 并发访问可能崩溃 |
| Domain 快照无数据验证 | `snapshots.py` | `fraction` 无 0-1 范围检查 |
| Settings 布尔值强制 `"true"` 判断 | `settings.py:46` | `"yes"`/`"1"` 会静默失败 |
| `ConditionSnapshot` 是死代码 | `snapshots.py:196` | 从未使用 |

### GUI 相关

| 问题 | 文件 | 说明 |
|------|------|------|
| PageController Dock Signal 累积 | `page_controller.py:179` | 每次 show/hide 累积 |
| `_onConfigureClicked` 循环调用 | `simulation_page/widget.py:157-160` | 取消后继续执行空计算 |
| 主题切换重复连接信号 | `theme_service.py:181-191` | 旧连接未断开 |
| `_GroupTreeView.dropEvent` 覆盖方式 | `group_tree/widget.py:77` | 绕过 Qt 虚拟方法 |

### Module 相关

| 问题 | 文件 | 说明 |
|------|------|------|
| `sys.path` 导入时修改 | `module_manager.py:18` | 全局副作用 |
| 鸭子类型无接口验证 | `module_manager.py:47` | 延迟到运行时才报错 |
| `calculateSingleBatch` 配置混淆 | `miedema_module.py:279` | 复用 `calculateSingle` 配置 |

---

## 🟢 低优先级

| 问题 | 文件 | 说明 |
|------|------|------|
| PostgreSQL SQL 检测用字符串包含 | `postgresql.py:164` | 脆弱的字符串匹配 |
| 十六进制颜色解析无长度检查 | `color.py:31` | `"#123"` 会 ValueError |
| InvertedIcon CSS 管理脆弱 | `theme_service.py:42-72` | 嵌套大括号语法错误 |
| 顶层窗口遍历图标更新 | `theme_service.py:289` | 嵌套 widget 找不到 |
| `lastRowId` fallback 用 `or` | `base_repository.py:81` | 0 值会误判 |

---

---

## 项目概览

### 项目定位

**MoltenMeta** — 液态金属性质数据库与预报平台

一个灵活的软件平台，整合液态金属属性数据库与预测建模能力，设计上强调可扩展性。

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | PySide6 + Qt-Advanced-Docking-System |
| 后端 | Python 3.14+ |
| 算法引擎 | C++ (miedema_core.so) |
| 数据库 | SQLite (双数据库架构) |

### 架构

```
┌─────────────────────────────────────────────────────────┐
│  UI Layer (gui/)                                        │
│  - PySide6 widgets, pages, components                   │
├─────────────────────────────────────────────────────────┤
│  Application Layer (application/)                         │
│  - Services, use cases                                  │
├─────────────────────────────────────────────────────────┤
│  Domain Layer (domain/)                                  │
│  - Entities, business logic, snapshots                   │
├─────────────────────────────────────────────────────────┤
│  Infrastructure Layer (db/, core/, framework/)             │
│  - Repositories, adapters, utilities                    │
└─────────────────────────────────────────────────────────┘
```

### 数据库架构

| 数据库 | 文件 | 用途 |
|--------|------|------|
| Core | `core.mmdb` (runtime path) | 应用设置、配置 |
| User | (configurable path) | 用户数据、导入材料、计算缓存 |

### 数据库分层设计

```
Language Layer  ──▶  Ontology Layer  ──▶  Concept Layer  ──▶  Fact Layer
(sym, units)        (elements, sys)     (properties,      (property_values,
                                               methods,            conditions)
                                               conditions)
```

**核心表**：
- `symbols`, `units` — 语言层
- `elements`, `systems`, `system_compositions` — 本体层
- `properties`, `methods` — 概念层
- `property_values`, `property_value_conditions` — 事实层
- `meta` — 出处层
- `computation_cache` — **新增** 计算缓存层（模块计算结果）

### 模块系统

模块放在 `runtime/modules/` 目录下，通过 `ModuleManager` 动态发现和加载。**开发时使用软链接指向 `src/modules/`**。

```
runtime/modules/
└── miedema_module -> src/modules/miedema_module (软链接)
    ├── __init__.py
    ├── miedema_module.py
    ├── element_map.py
    ├── config.toml
    ├── lib/miedema_core.so
    └── miedema_element_properties.csv
```

模块通过 `config.toml` 声明：
- 包名、入口类、支持的方法
- 输入/输出定义
- Plot 配置

### 现有页面

| 页面 | 状态 | 功能 |
|------|------|------|
| Home | ✅ | 入口页面 |
| Settings | ✅ | 配置管理 |
| Database | ✅ | 数据浏览/编辑 |
| Simulation | ✅ | 模块计算/绘图 |

### 实现状态

| 状态 | 功能 |
|------|------|
| ✅ 完成 | 核心应用框架、PySide6 + QtADS、双数据库、Repository 模式、Domain snapshots、主题系统、i18n、Home/Settings/Database 页面、Simulation 页面、matplotlib 完全可配置（主题色+取色算法+网格/标签密度解耦）、日志窗口、元素映射表、成分工具、**数据组（Group树+拖拽+右侧联动）** |
| 🚧 进行中 | 数据导出（CSV/Excel）、自定义绘制、报告生成、计算缓存 |

---

## 已完成的设计决策

### 架构决策

- ModuleManager / ModuleService 分层
- config.toml 驱动动态表单
- is_collection 区分单点/批量计算
- 表格头使用 symbol key
- 元素符号输入替代原子序数输入
- 成分输入支持摩尔/质量分数切换
- 模块使用软链接指向源码目录
- **模块间通过符号（symbol）交互，不感知数据来源**
- **计算结果与用户数据分离存储（property_values vs computation_cache）**

### Q 决策汇总

| Q# | 问题 | 决策 |
|----|------|------|
| Q1 | 实验 vs 计算数据选择 | A：用户手动选，默认全部显示 |
| Q2 | 自定义修正量 | 修正量入库，需要新表和溯源机制 |
| Q3 | 数据组优先级 | 手动 > 随手 > 自动 |
| Q4 | 成分输入解析格式 | 支持任意非字母数字分隔符，缺项自动推算 |
| Q5 | 模块数据入库方式 | 混合：静态数据模块私有表，计算结果 computation_cache |
| Q6 | Schema 发现机制 | 模块声明所需表，运行时验证 |
| Q7 | 计算结果存储 | computation_cache 表（独立于 property_values） |
| Q8 | 跨模块复用 | 可以，通过 computation_cache 共享 |

---

## MVP 核心链路

打通数据全链路：
```
数据导入 → 数据组 → 自定义绘制 → 图片导出 + 报告生成
```

**典型用户场景**（研究生工作流）：
```
[实验数据A]  ──┐
     │         │
     ▼         ▼
[模块B计算] ──┐ │
     │         │ │
     └─────────┼─┘
               ▼
          [模块C计算]  ← 数据不足时弹出补充选择框
               │
        ┌──────┴──────┐
        ▼             ▼
   [图表导出]    [报告生成 + 数据导出]
```

### 关键设计原则

1. **符号作为统一接口**：模块按符号查询数据，不关心来源
2. **来源在展示层区分**：图例 + 颜色/线型区分实验/各模块计算
3. **链式计算自动追溯**：run_id → parent_run_id 追踪依赖链
4. **批量选择而非逐行选择**：用户按批次/工况选择数据

---

## Plan

### ✅ P1. matplotlib 完全可配置
- config.toml 扩展 plot 配置（line_style, marker, colorscheme, grid 等）
- fallback 到 settings 中的默认值
- 主题色 + 取色算法（linear/harmonic/colorwheel）
- Settings Plot Tab 完整实现
- **网格线密度与标签密度解耦**（新增 gridLabelDensity）
- 优先级：P1 | **已完成**

### ✅ P2. 元素映射表模块
- 硬编码元素 id ↔ symbol 映射（不用绕数据库）
- 文件：`src/core/element_map.py`
- 接口：`idToSymbol()`, `symbolToId()`, `getAllElements()`
- **模块独立映射**：`src/modules/miedema_module/element_map.py`
- 优先级：P1 | **已完成**

### ✅ P3. 成分工具剥离
- `core/composition.py` 独立维护
- `gui/pages/simulation_page/composition_tool.py` 改为桥接文件
- 支持摩尔/质量分数切换
- 支持缺项自动补全
- 优先级：P1 | **已完成**

### ✅ P4. 成分输入解析增强
- 支持任意非字母数字分隔符
- 摩尔分数：支持 "Al90Si10" (total=100) 和 "Al0.9Si0.1" (total=1)
- 质量分数：自动换算为摩尔分数（通过 atomic_mass）
- 优先级：P1 | **已完成**

### ✅ P5. 日志窗口
- 只读文本框显示日志
- 级别过滤：DEBUG / INFO / WARNING / ERROR
- QtLogHandler 集成到 Settings Page
- 优先级：P1 | **已完成**

---

### ✅ P6. 数据导入
- CSV 解析（自动检测分隔符：逗号/空格/制表符）
- 列映射 UI（用户选择 CSV 列 → 数据库字段）
- 元素符号匹配（CSV 元素名 → database symbol_id）
- 数据校验（数值范围、必填项、格式）
- 批量插入（性能优化）
- **2026-04-15 完成**：参考 `csv_import_implementation_report.md`
- 优先级：P1 | MVP | **已完成**

### P7. 数据导出
- 最小化导出：单表
- 全数据导出：所有牵连表
- CSV / Excel 格式
- 优先级：P1 | MVP | **待完成**

### P8. 图片导出
- 格式：PNG / SVG / PDF
- 单个图表导出
- 可配置 DPI / 分辨率（Settings Plot Tab 已部分支持）
- 优先级：P1 | MVP | **待完成**

### P9. 自定义数据绘制
- **符号统一查询 API**：按符号查询，不问来源
- **X/Y 列选择器**：用户选择绑定数据列
- **多系列绑定**：同一图上绑多个 Y 列
- **来源区分展示**：图例 + 颜色/线型区分实验/计算
- **数据不足时的补充选择对话框**：Module 数据不足时弹出
- 优先级：P1 | MVP | **待完成**

### ✅ P10. 数据组 (Group)
- Group 创建/编辑 UI（用户手动创建分组）
- 自动分组规则（按 source_file、时间等）
- Group 管理界面（查看、合并、删除）
- Group 过滤（按 Group 筛选数据）
- **2026-04-17 完成**：完整实现包括树形管理、拖拽、右侧面板联动
- 优先级：P1 | MVP | **已完成**

### P11. 报告生成
- 模板化报告：PDF / DOCX
- 包含：图表、数据表、参数、meta
- 可追溯计算来源（B → C 链式计算可视化）
- 原始数据引用记录
- 优先级：P1 | MVP | **待完成**

---

### ✅ P12. 主题跟随系统
- 检测系统是 dark mode 还是 light mode
- PlotPanel figure facecolor 跟随
- 不硬编码白色
- theme_service.scheme + theme_changed signal + setScheme 已连接
- Settings Plot Tab 有 "Follow" 选项
- 优先级：P2 | **已完成**

### P13. statusLabel 推广
- Widget 基类添加 statusLabel
- DataPage 等其他页面也加上
- 统一的错误/状态信息展示
- 优先级：P2 | **待完成**

### P14. 侧边栏/菜单栏更新
- HomePage 有 Project, Database, Simulation, Settings 按钮
- 菜单项需与已实现功能同步
- 优先级：P2 | **待完成**

### ✅ P15. 动态取色算法
- 色相环均匀取色（多系列时）
- 支持 colorscheme：default / vibrant / pastel
- ColorGenerator 实现 linear/harmonic/colorwheel 三种算法
- 优先级：P2 | **已完成**（P1 的一部分）

### P16. LaTeX 标记方案
- 类似 HTML class 的方式标记哪些 Label 需要 LaTeX 渲染
- 当前仅有 PlotPanel 内部 `_wrapLatex()`，非通用方案
- 参考 `core/latex_render.py` 的实现
- 优先级：P2 | **待完成**

---

### P17. 计算历史
- 记录所有计算（run_id 批次管理）
- 可追溯、重算、对比
- 搜索和过滤
- 优先级：P2 | **待完成**

### P18. 模块自带数据入库
- 模块首次运行时自动创建所需的私有表
- 静态数据（元素属性等）存模块私有表
- 计算结果存 computation_cache（跨模块共享）
- 优先级：P2 | **待完成**

---

### P19. computation_cache 表（底层支撑）
- 存储模块计算结果，与 property_values 分离
- 字段：run_id, module_id, system_id, property_id, value, conditions_json, parent_run_id, source, created_at
- 支持链式计算追溯
- 自动过期清理策略
- 优先级：P1 | **底层支撑 | 待完成**

### P20. 属性符号表扩展（底层支撑）
- symbols.csv 新增 Cp, H, T, P, ρ, λ 等物理量符号
- units 表完善单位映射
- properties 表关联符号与单位
- 优先级：P1 | **底层支撑 | 待完成**

### P21. 数据补充选择对话框（底层支撑）
- Module 数据不足时自动弹出
- 用户选择补充数据来源（实验数据或其他模块结果）
- 一键确认，自动继续计算
- 优先级：P1 | **待完成**

---

## 代码质量（待完成）

### 模块系统

| 问题 | 优先级 | 说明 |
|------|--------|------|
| 线程安全问题 | 高 | `_modules` 字典无同步保护 |
| 全局 sys.path 修改 | 中 | `ModuleManager._ensureRuntimeInPath()` 影响全局 |
| Bare `except Exception` | 低 | 捕获所有异常包括 KeyboardInterrupt |
| 字典访问无验证 | 中 | `config["module"]["package_name"]` 可能 KeyError |
| `callMethod` 无特定异常处理 | 中 | 异常缺少模块/方法上下文 |

### 模拟页面

| 问题 | 优先级 | 说明 |
|------|--------|------|
| 取消流程逻辑问题 | 中 | 用户取消后循环调用配置对话框 |
| `loadModuleConfig` 返回 None | 中 | 调用方未检查 |
| Bare `except Exception` | 低 | widget.py 中捕获所有异常 |

---

## 深度分析

### 一、数据分层存储架构

```
┌─────────────────────────────────────────────────────────────┐
│  用户数据层（property_values）                               │
│  - 用户手动导入的实验数据                                    │
│  - 少量、精确、需要追溯来源                                  │
│  - 不关心来源（实验/计算），只关心量纲                        │
├─────────────────────────────────────────────────────────────┤
│  模块计算缓存层（computation_cache）                          │
│  - 模块计算结果的临时存储                                    │
│  - 大量、可过期清理、生命周期=计算会话或一定时间            │
│  - 通过 run_id / parent_run_id 支持链式追溯                  │
│  - 不污染 property_values                                    │
├─────────────────────────────────────────────────────────────┤
│  符号统一查询层（Symbol-based Query）                        │
│  - 合并两个来源按符号查询                                    │
│  - 按量纲/条件筛选                                          │
│  - 模块不感知数据来自哪里                                    │
├─────────────────────────────────────────────────────────────┤
│  展示层（Plot / Report）                                     │
│  - 通过图例区分来源（实验 vs 模块B vs 模块C）               │
│  - 用户选择批次/工况，不逐行选择                             │
└─────────────────────────────────────────────────────────────┘
```

### 二、chain Calculation 追溯

```sql
-- Module B 计算结果
INSERT INTO computation_cache (run_id, module_id, system_id, property_id, value, created_at)
VALUES ('uuid-B', 'miedema_module', 1, 5, 1234.5, datetime('now'));

-- Module C 依赖 B 的结果
INSERT INTO computation_cache (run_id, module_id, system_id, property_id, value, parent_run_id, created_at)
VALUES ('uuid-C', 'other_module', 1, 6, 5678.9, 'uuid-B', datetime('now'));
```

追溯查询：
```sql
WITH RECURSIVE chain AS (
    SELECT run_id, module_id, parent_run_id, 1 as depth
    FROM computation_cache WHERE run_id = 'uuid-C'
    UNION ALL
    SELECT c.run_id, c.module_id, c.parent_run_id, chain.depth + 1
    FROM computation_cache c
    JOIN chain ON c.run_id = chain.parent_run_id
)
SELECT * FROM chain;
```

### 三、用户选择粒度设计

```
用户不需要逐行选择数据，而是：

条件筛选 → 范围选择 → 批次勾选
     ↓
系统判断：数据量 < N → 全量使用
    数据量 > N → 提示用户选择或自动采样

┌─────────────────────────────────────────────┐
│  来源：[全部 ▼] [实验] [模块B] [模块C]        │
│  体系：[输入搜索...]                          │
│  性质：[焓(H) ▼] [热容(Cp) ▼] [密度(ρ) ▼]   │
│  日期：[最近30天 ▼]                          │
├─────────────────────────────────────────────┤
│  ☑ 批次 2024-04-10 14:30 | 模块C | Al-Si    │
│  ☑ 批次 2024-04-10 14:28 | 模块B | Al-Si    │
│  ☐ 批次 2024-04-09 10:15 | 实验 | Fe-Ni    │
│  ...                                        │
├─────────────────────────────────────────────┤
│  已选择 2 批次，共 ~120 条记录    [下一步 →] │
└─────────────────────────────────────────────┘
```

### 四、依赖关系图（更新）

```
                     ┌─────────────────────────────────────────────┐
                     │                                             │
     ┌─────────┐     │     ┌─────────────────────────────────┐   │
     │   P2    │────▶│     │                                 │   │
     │ 元素映射 │     │     │   P19 computation_cache 表      │   │
     └─────────┘     │     │   P20 属性符号表扩展            │   │
           │         │     │   P21 数据补充选择对话框         │   │
           │         │     └─────────────────────────────────┘   │
           │         │              │           │                │
           ▼         │              ▼           ▼                │
     ┌─────────┐     │         ┌─────────┐ ┌─────────┐         │
     │   P3    │     │         │   P6    │ │   P9    │         │
     │ 成分工具 │     │         │ 数据导入 │ │自定义绘制│         │
     └─────────┘     │         └─────────┘ └─────────┘         │
           │         │              │           │                │
           ▼         │              ▼           ▼                │
     ┌─────────┐     │         ┌─────────────────────┐          │
     │   P4    │     │         │        P11          │          │
     │ matplotlib│    │         │      报告生成        │          │
     └─────────┘     │         └─────────────────────┘          │
           │         │                                             │
           ▼         │                                             │
     ┌─────────┐     │                                             │
     │   P5    │     │                                             │
     │ 日志窗口 │     │                                             │
     └─────────┘     │                                             │
           │         │                                             │
           ▼         │                                             │
     ┌─────────┐     │                                             │
     │   P1    │     │                                             │
     │matplotlib│    │                                             │
     │完全可配置│     │                                             │
     └─────────┘     │                                             │
           │         │                                             │
           ▼         │                                             │
     ┌─────────┐     │                                             │
     │  P12    │     │                                             │
     │主题跟随  │     │                                             │
     └─────────┘     │                                             │
                     └─────────────────────────────────────────────┘
```

---

## 分阶段实施策略

### 阶段一：底层支撑（必须先完成）

| 项目 | 状态 | 说明 |
|------|------|------|
| P19 computation_cache 表 | ⏳ 待完成 | 链式计算追溯基础 |
| P20 属性符号表扩展 | ⏳ 待完成 | 物理量符号统一接口 |
| P21 数据补充选择对话框 | ⏳ 待完成 | Module 数据不足时触发 |
| P1 matplotlib 配置 | ✅ 已完成 | 包含网格/标签密度解耦 |

**预计时间**：2-3 人天

---

### 阶段二：数据流（核心 MVP）

| 项目 | 状态 | 说明 |
|------|------|------|
| P6 数据导入 | ✅ 已完成 | CSV 解析、列映射、批量插入 |
| P9 自定义绘制 | ⏳ 待完成 | 符号查询、X/Y 选择、来源区分 |
| P10 数据组 | ✅ 已完成 | Group 树、拖拽、过滤、右侧联动 |

**预计时间**：5-8 人天

---

### 阶段三：输出

| 项目 | 状态 | 说明 |
|------|------|------|
| P8 图片导出 | ⏳ 待完成 | PNG/SVG/PDF、DPI 配置 |
| P11 报告生成 | ⏳ 待完成 | 模板、参数、追溯图、数据表 |

**预计时间**：3-5 人天

---

### 阶段四：收尾

| 项目 | 状态 | 说明 |
|------|------|------|
| P7 数据导出 | ⏳ 待完成 | CSV/Excel、对称于导入 |
| P13 statusLabel 推广 | ⏳ 待完成 | Widget 基类 |
| P14 侧边栏/菜单栏 | ⏳ 待完成 | 与功能同步 |
| P16 LaTeX 标记 | ⏳ 待完成 | 通用方案 |
| P17 计算历史 | ⏳ 待完成 | 完整追溯 UI |

**预计时间**：3-4 人天

---

## 工作量估算

| 阶段 | 项目数 | 预计人天 |
|------|--------|----------|
| 阶段一：底层支撑 | 4 | 2-3 |
| 阶段二：数据流 | 3 | 5-8 |
| 阶段三：输出 | 2 | 3-5 |
| 阶段四：收尾 | 5 | 3-4 |
| **MVP 总计** | **9** | **13-20** |

---

## 已完成决策汇总

1. **Q1（实验 vs 计算选择）**：默认全部显示，用户手动筛选
2. **Q2（自定义修正量）**：修正量入库，需要新表和溯源机制
3. **Q3（数据组优先级）**：手动 > 随手 > 自动
4. **Q4（成分输入格式）**：支持任意非字母数字分隔符，缺项自动推算
5. **Q5（模块数据入库）**：混合模式（静态数据私有表，计算结果 computation_cache）
6. **Q6（Schema 发现）**：模块声明所需表，运行时验证
7. **Q7（计算结果存储）**：computation_cache 表（独立于 property_values）
8. **Q8（跨模块复用）**：可以，通过 computation_cache 共享
9. **元素输入**：使用元素符号输入（如 "Al"），而非原子序数
10. **模块映射表**：模块独立维护，不依赖主程序
11. **数据选择粒度**：按批次/工况选择，不逐行选择
12. **符号作为统一接口**：模块按符号查询，不关心数据来源
