# MoltenMeta 开发者指南

MoltenMeta 是一个面向液态合金热力学的计算与可视化平台，支持热力学计算、不确定性量化和模块化扩展。

---

## 核心概念

### 架构分层

```
UI (PySide6) → Application Services → Modules (plugins) → Data (SQLite)
```

**依赖注入**：通过 `AppContext` 获取服务（`context.modules`、`context.user_db` 等），避免全局单例。

**两阶段初始化**：
- `bootstrap()`：创建核心服务（Log、I18n、Theme）
- `initApp()`：加载数据库和模块

**双数据库**：
- `core.mmdb`：应用设置
- `user DB`：元素、系统、属性值等业务数据

### 模块系统

模块通过 `config.toml` 配置，无需继承基类（duck typing）。

```
runtime/modules/
├── kohler_module/
│   └── config.toml
├── toop_module/
│   └── config.toml
└── ...
```

**数据源注册**：模块通过 `DataSourceRegistry.register(tag, factory)` 注册数据源，供其他模块查询。

---

## 模块索引

| 模块 | 入口类 | 说明 | 数据标签 |
|------|--------|------|----------|
| [Kohler](/modules/kohler) | `KohlerCalc` | 对称几何模型 | — |
| [Toop](/modules/toop) | `ToopCalc` | 非对称几何模型 | — |
| [Maggianu](/modules/maggianu) | `MaggianuCalc` | 体积分数修正 | — |
| [HillertToop](/modules/hillert-toop) | `HillertToopCalc` | 混合几何模型 | — |
| [Miedema](/modules/miedema) | `MiedemaCalc` | ΔH_mix 计算 | `Delta_H_mix`, `Miedema`, `binary_data` |
| [GP](/modules/gp) | `GPCalc` | 高斯过程回归 | `GP` |
| [RK](/modules/rk) | `RKCalc` | Redlich-Kister 多项式 | `R-K` |
| [Butler](/modules/butler) | `ButlerCalc` | 表面张力计算 | `sigma`, `Butler` |

---

## 安装配置

### 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.12 / 3.14 | Windows 打包用 3.12，源文件运行用 3.14 |
| C++ 编译器 | C++17 | 用于编译 Pybind11 扩展 |
| uv | 最新 | Python 包管理 |

### 快速开始

```bash
# 安装依赖
uv sync

# 运行应用
uv run python src/main.py --runtime-path ./runtime
```

### C++ 扩展编译

计算密集型模块使用 C++ 编写，通过 Pybind11 绑定：

```
module_name_module/
├── module_name_module.py    # Python wrapper
├── module_name_algorithm.cpp # C++ 实现
├── CMakeLists.txt
└── lib/
    └── module_name_algorithm.so  # 编译产物
```

`.so`（Linux）/ `.pyd`（Windows）/ `.dylib`（macOS）文件放入 `lib/` 目录，Python 通过 `importlib` 动态加载。

---

## 核心 API

### BinaryDataProvider

二元数据提供者接口。几何模型通过此接口获取二元数据。

```python
# src/framework/binary_provider.py
class BinaryDataProvider(ABC):
    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        """获取二元属性值数组"""
```

**实现示例（MiedemaProvider）**：

```python
class MiedemaProvider:
    def __init__(self, module_service):
        self._module_service = module_service

    def get_values(self, elem_1: int, elem_2: int, x_array: list[float]) -> list[float]:
        result = self._module_service.callMethod(
            "miedema_module", "calculateSingleBatch",
            elem_A=elem_1, elem_B=elem_2, x_array=x_array,
        )
        return result["values"]
```

### DataSourceRegistry

数据源工厂注册表。通过标签查找数据源。

```python
class DataSourceRegistry:
    @classmethod
    def register(cls, tag: str, factory: Callable) -> None: ...
    
    @classmethod
    def findByTag(cls, required_tags, accepted_tags, module_service=None) -> list: ...
```

### ModuleService

模块加载和调用的核心服务。

```python
class ModuleService:
    def callMethod(self, module_name: str, method_name: str, **kwargs) -> dict: ...
    
    def setProvider(self, module_name: str, provider: BinaryDataProvider) -> None: ...
```

---

## 几何模型

### 参数约定

AB → AC → BC（按字母序）

### 四种模型

**Kohler（对称）**：
```
Z_ABC = (x_A+x_B)²·Z_AB(x_A/(x_A+x_B)) 
      + (x_B+x_C)²·Z_BC(x_B/(x_B+x_C)) 
      + (x_A+x_C)²·Z_AC(x_A/(x_A+x_C))
```

**Toop（非对称，A 为溶剂）**：
```
Z_ABC = x_B/(x_B+x_C)·Z_AB(x_A) + x_C/(x_B+x_C)·Z_AC(x_A) 
      + (x_B+x_C)²·Z_BC(x_B/(x_B+x_C))
```

**Maggianu（体积分数修正）**：
```
V_ij = (1 + x_i - x_j) / 2
Z_ABC = x_A·x_B/(V_AB·V_BA)·Z_AB(V_AB) + ...
```

**Hillert-Toop（混合）**：
```
Z_ABC = x_B/(x_B+x_C)·Z_AB(x_A) + x_C/(x_B+x_C)·Z_AC(x_A) 
      + x_B·x_C/(V_BC·V_CB)·Z_BC(V_BC)
```

---

## 计算链路

### GP → RK → Butler

```
实验数据 → GP.fit() → GP.predict() → 残差预测
    ↓
二元数据 → RK.fit() → L_coeffs + Σ_L
                ↓
          get_GE_functions()
                ↓
ButlerConfig ← sigma_i_func, density_func, element_props_get_M
                ↓
         ButlerCalc.solve() → σ(x, T)
                ↓
         sample() → Monte Carlo 不确定性传播
```

### GP 模块

```python
class GPCalc:
    def train(self, data_points, target_mode, prior, kernel_type, alpha) -> dict:
        """训练 GP 模型
        - target_mode: "direct" 或 "residual"
        - kernel_type: "RBF" 或 "Matern"
        """

    def predict(self, features_array) -> dict:
        """返回 target_array 和 var_array（方差）"""
```

### RK 模块

```python
class RKCalc:
    def fit(self, points, order, use_variance_weighting) -> dict:
        """加权最小二乘拟合"""

    def get_GE_functions(self) -> tuple[GE_func, dGE_dx_func]:
        """返回 G^E 和偏导数函数，供 Butler 使用"""
```

多项式形式：
```
G^E(x,T) = x(1-x) · Σ[L_k(T) · δ^k]
δ = 2·(x - 0.5)
L_k(T) = a_k + b_k·T
```

### Butler 模块

```python
@dataclass(frozen=True)
class ButlerConfig:
    sigma_i_func: Callable[[int, float], float]   # 纯元素表面张力 σ_i(T)
    density_func: Callable[[int, float], float]  # 密度 ρ_i(T)
    element_props_get_M: Callable[[int], float]  # 原子量 M_i
    elem_A: int
    elem_B: int

class ButlerCalc:
    def solve(self, T: float, x_bulk_A: float) -> dict:
        """解 Butler 方程组，返回 sigma 和表面组成"""

    def sample(self, T, x_bulk_A, n_samples, Sigma_L, L_coeffs) -> dict:
        """Monte Carlo 不确定性传播"""
```

Butler 方程：
```
σ = σ_i + (RT/S_i)·ln(x_i^s/x_i^b) + (G_i^E,s - G_i^E,b)/S_i
```

关键常数：
```python
R = 8.314462618           # J/(mol·K)
N_A = 6.02214076e23
S_CONSTANT = 1.091
BETA = 0.75
```

---

## 数据持久化

### Snapshot 模式

数据实体使用 `frozen=True` 的 dataclass，确保不可变。

```python
class SnapshotBase(ABC):
    id: int | None

    @classmethod
    def fromRow(cls, row) -> "SnapshotBase": ...

    def toRecord(self) -> dict: ...
```

**快照映射**：

| Snapshot | 表 |
|----------|-----|
| `ElementSnapshot` | `elements` |
| `SystemSnapshot` | `systems` |
| `PropertySnapshot` | `properties` |
| `PropertyValueSnapshot` | `property_values` |

### Repository 模式

```python
class BaseRepository(ABC, Generic[T]):
    def insert(self, entity: T) -> int: ...
    def findById(self, id: int) -> T | None: ...
    def findAll(self) -> List[T]: ...
    def update(self, entity: T) -> bool: ...
    def delete(self, id: int) -> bool: ...
```

---

## config.toml 参考

```toml
[module]
package_name = "kohler_module"
entry_class = "KohlerCalc"
all_methods = ["calculateSingleProperty", "calculateScatter", "calculateContour"]
type = "simulation"
category = "geometric_model"

[calculateSingleProperty.inputs]
symbol = ["elem_A", "elem_B", "elem_C", "x_A", "x_B", "x_C", "Z_AB", "Z_BC", "Z_AC"]
input_method = "raw"

[calculateSingleProperty.outputs]
symbol = ["Z_ABC"]
is_virtual = true

[calculateSingleProperty.plot]
plotType = "scatter_3d"
```

---

## 常见问题

### Linux Wayland 问题

**问题**：Qt-Advanced-Docking-System 在 Wayland 会话下停靠和拖拽异常。

**解决**：使用 X11 会话（登录界面选择 "GNOME on Xorg"）。

### 模块加载失败

**检查项**：
1. `config.toml` 存在且格式正确
2. `entry_class` 拼写正确
3. 模块目录在 `runtime/modules/` 下
4. `registerDataSources()` 正确注册

### 数据源查询返回空

**检查项**：
1. 数据源已注册到 `DataSourceRegistry`
2. 标签匹配（`required_tags` 和 `accepted_tags`）
3. 数据库中已有数据

### C++ 扩展加载失败

**检查项**：
1. 编译产物（`.so`/`.pyd`/`.dylib`）在 `lib/` 目录
2. Python 版本与扩展编译版本匹配
3. `importlib.util.spec_from_file_location` 路径正确

### GP 训练不收敛

**建议**：
- 使用 `kernel_type="Matern"` 而非 `"RBF"`（更稳健）
- 调整 `alpha` 参数（越小越容易过拟合）
- 小数据集（< 30 点）考虑固定 `length_scale`

---

## 目录结构

```
src/
├── application/
│   ├── service/           # 应用服务
│   └── app_startup.py     # 两阶段初始化
├── db/                    # 数据库层
│   ├── snapshot/          # 数据实体
│   └── user/repo/         # 用户数据仓库
├── framework/
│   ├── module_manager.py  # 模块管理
│   ├── data_source_registry.py  # 数据源注册
│   ├── binary_provider.py # 二元提供者接口
│   └── data_source.py     # 数据源抽象
├── modules/
│   ├── kohler_module/
│   ├── toop_module/
│   ├── miedema_module/
│   ├── gp_module/
│   ├── rk_module/
│   └── butler_module/
└── gui/pages/             # UI 页面
```

---

## 相关链接

* [GitHub Issues](https://github.com/...)
* 技术支持：support@moltenmeta.com