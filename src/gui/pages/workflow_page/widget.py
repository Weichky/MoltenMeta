from PySide6 import QtWidgets, QtCore
import numpy as np
from matplotlib.tri import Triangulation

from .controller import WorkflowController
from gui.pages.simulation_page.plot_panel.panel import PlotPanel
from core.plot import PlotStyleService


class WorkflowPage(QtWidgets.QWidget):
    def __init__(self, context):
        super().__init__(parent=None)
        self._context = context
        self._logger = context.log.getLogger(__name__)
        self._i18n = context.i18n
        self._theme_service = context.theme
        self._controller = WorkflowController(context)
        self._plot_style_service = PlotStyleService()

        self._current_workflow = None
        self._current_method = None
        self._method_configs = {}
        self._pending_inputs = None
        self._current_result = None
        self._workflow_module = None
        self._suppress_signals = True

        self._setupUi()
        self._connectSignals()
        self._populateWorkflows()
        self._suppress_signals = False

        settings = context.settings
        grid = settings.plot_grid if settings.plot_grid is not None else True
        grid_mode = settings.plot_grid_mode or "auto"
        grid_density = settings.plot_grid_density or 1.0
        grid_label_density = settings.plot_grid_label_density or 1.0
        self._plot_panel.applyPlaceholder(
            grid, grid_mode, grid_density, grid_label_density
        )

    def _setupUi(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        header = QtWidgets.QLabel()
        header.setObjectName("headerLabel")
        header.setText(self._i18n.tr("Workflow"))
        main_layout.addWidget(header)

        controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QFormLayout(controls_widget)
        controls_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.workflowCombo = QtWidgets.QComboBox()
        self.workflowCombo.setObjectName("workflowCombo")

        self.methodCombo = QtWidgets.QComboBox()
        self.methodCombo.setObjectName("methodCombo")

        self.configureButton = QtWidgets.QPushButton()
        self.configureButton.setObjectName("configureButton")
        self.configureButton.setText(self._i18n.tr("Configure"))

        self.runButton = QtWidgets.QPushButton()
        self.runButton.setObjectName("runButton")
        self.runButton.setText(self._i18n.tr("Run"))

        controls_layout.addRow(self._i18n.tr("Workflow:"), self.workflowCombo)
        controls_layout.addRow(self._i18n.tr("Method:"), self.methodCombo)
        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.configureButton)
        button_row.addWidget(self.runButton)
        controls_layout.addRow("", button_row)

        main_layout.addWidget(controls_widget)

        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setObjectName("statusLabel")
        main_layout.addWidget(self.statusLabel)

        plot_container = QtWidgets.QWidget()
        plot_layout = QtWidgets.QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        self._plot_panel = PlotPanel()
        plot_layout.addWidget(self._plot_panel)
        main_layout.addWidget(plot_container, stretch=1)

        self.resultLabel = QtWidgets.QLabel()
        self.resultLabel.setObjectName("resultLabel")
        main_layout.addWidget(self.resultLabel)

        main_layout.addStretch()

    def _connectSignals(self) -> None:
        self.workflowCombo.currentIndexChanged.connect(self._onWorkflowChanged)
        self.methodCombo.currentIndexChanged.connect(self._onMethodChanged)
        self.configureButton.clicked.connect(self._onConfigureClicked)
        self.runButton.clicked.connect(self._onRunClicked)
        self._i18n.language_changed.connect(self._retranslateUi)

    def _populateWorkflows(self) -> None:
        self.workflowCombo.currentIndexChanged.disconnect(self._onWorkflowChanged)
        self.workflowCombo.clear()
        workflows = self._controller.getWorkflows()
        for w in workflows:
            self.workflowCombo.addItem(
                w.get("name", w["package_name"]), w["package_name"]
            )
        self._suppress_signals = False
        if self.workflowCombo.count() > 0:
            self._onWorkflowChanged(0)
        self.workflowCombo.currentIndexChanged.connect(self._onWorkflowChanged)

    def _onWorkflowChanged(self, index: int) -> None:
        if index < 0 or self._suppress_signals:
            return
        self._current_workflow = self.workflowCombo.currentData()
        self._loadMethods(self._current_workflow)
        self._workflow_module = self._controller.getWorkflowModule(
            self._current_workflow
        )

    def _loadMethods(self, package_name: str) -> None:
        self.methodCombo.currentIndexChanged.disconnect(self._onMethodChanged)
        self.methodCombo.clear()
        self._method_configs = {}
        methods = self._controller.getMethods(package_name)
        for method in methods:
            config = self._controller.getModuleConfig(package_name)
            method_cfg = config.get(method, {}) if config else {}
            self._method_configs[method] = method_cfg
            self.methodCombo.addItem(method)
        if self.methodCombo.count() > 0:
            self._current_method = self.methodCombo.itemText(0)
            self._pending_inputs = None
            self._current_result = None
            self.statusLabel.setText("")
            self._plot_panel.clear()
            self.resultLabel.setText("")
        self.methodCombo.currentIndexChanged.connect(self._onMethodChanged)

    def _onMethodChanged(self, index: int) -> None:
        if index < 0 or self._suppress_signals:
            return
        self._current_method = self.methodCombo.currentText()
        self._pending_inputs = None
        self._current_result = None
        self.statusLabel.setText("")
        self._plot_panel.clear()
        self.resultLabel.setText("")

    def _onConfigureClicked(self):
        self._logger.info(
            f"Configure clicked: workflow={self._current_workflow}, method={self._current_method}"
        )
        if not self._current_workflow or not self._current_method:
            self.statusLabel.setText("No workflow or method selected")
            return

        has_widget = self._controller.hasModuleWidget(self._current_workflow)
        self._logger.info(f"hasModuleWidget={has_widget}")
        if has_widget:
            dialog = self._controller.getModuleWidget(
                self._current_workflow, self._current_method
            )
            if dialog is None:
                self.statusLabel.setText("Error: No wizard for this method")
                return
            dialog.resultReady.connect(self._onWizardConfigured)
            dialog.exec()
        else:
            self.statusLabel.setText("Error: No wizard available for this module")

    def _onWizardConfigured(self, params: dict) -> None:
        self._pending_inputs = params
        self.statusLabel.setText(f"Configured: {len(params)} parameters")

    def _onRunClicked(self):
        if not self._current_workflow or not self._current_method:
            return

        if not self._pending_inputs:
            self._onConfigureClicked()
            return

        try:
            inputs = dict(self._pending_inputs)
            method_name = inputs.pop("method_name", self._current_method)
            self._logger.info(f"callWorkflow: {self._current_workflow}.{method_name}")
            result = self._controller.callWorkflow(
                self._current_workflow, method_name, **inputs
            )
            self._current_result = result
            self._displayResult(result)
            self.statusLabel.setText("Execution complete")
        except Exception as e:
            self._logger.error(f"Workflow execution failed: {e}")
            self.statusLabel.setText(f"Error: {e}")

    def _getPlotConfig(self):
        settings = self._context.settings
        return self._plot_style_service.buildConfig({}, {}, settings)

    def _displayResult(self, result: dict) -> None:
        if not result:
            return

        plot_config = self._getPlotConfig()

        if self._current_workflow == "viscosity_workflow":
            self._displayViscosityResult(result, plot_config)
        elif self._current_workflow == "surface_workflow":
            self._displaySurfaceResult(result, plot_config)
        else:
            self._displayGenericResult(result, plot_config)

    def _displayViscosityResult(self, result: dict | list, plot_config) -> None:
        if isinstance(result, list) and len(result) > 1:
            self._plotViscosityPredictContour(
                {
                    "eta": [r.get("eta") for r in result],
                    "params": result[0] if result else {},
                },
                plot_config,
            )
            self.resultLabel.setText("Ternary Viscosity Prediction (Batch)")
        elif isinstance(result, dict) and "vi_md_grid" in result:
            self._plotViscosityPredictContour(result, plot_config)
            self.resultLabel.setText("Ternary Viscosity Prediction")
        elif isinstance(result, dict) and result.get("eta") is not None:
            eta = result.get("eta")
            if isinstance(eta, list) and len(eta) > 1:
                self._plotViscosityPredictContour(result, plot_config)
                self.resultLabel.setText("Ternary Viscosity Prediction")
            elif isinstance(eta, (int, float)):
                self._plot_single_viscosity_point(result, plot_config)
                self.resultLabel.setText(
                    f"η = {result['eta']:.4f} Pa·s at T = {result.get('T', '?')} K"
                )
        elif isinstance(result, dict) and "binary_results" in result:
            self._plotFitResults(result, plot_config)
            self.resultLabel.setText("Ternary Viscosity Fit Analysis")
        else:
            self.resultLabel.setText(str(result))

    def _plotFitResults(self, result: dict, plot_config) -> None:
        md_data = result.get("md_data", {})
        x_Al = np.array(md_data.get("x_Al", []))
        x_Ni = np.array(md_data.get("x_Ni", []))
        vi_md = np.array(md_data.get("vi", []))
        binary_results = result.get("binary_results", {})

        fig = self._plot_panel._figure
        fig.clear()

        color1 = "#C0794A"
        color2 = "#1B3A5C"

        ax1 = fig.add_subplot(2, 2, 1)
        if len(vi_md) == 0:
            ax1.text(
                0.5,
                0.5,
                "No MD data",
                ha="center",
                va="center",
                transform=ax1.transAxes,
            )
            fig.tight_layout()
            self._plot_panel._canvas.draw()
            return

        h_factor = 0.866
        x_cart = x_Al + 0.5 * x_Ni
        y_cart = h_factor * x_Ni
        ax1.scatter(x_cart, y_cart, c=np.array(vi_md), cmap="turbo", s=30, alpha=0.8)
        ax1.set_xlabel("x (cartesian)")
        ax1.set_ylabel("y (cartesian)")
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, h_factor)
        ax1.grid(True, alpha=0.3, linestyle="--")
        ax1.set_aspect("equal")
        cb = fig.colorbar(ax1.collections[0], ax=ax1, shrink=0.8)
        cb.set_label("η (Pa·s)")

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.hist(vi_md, bins=20, alpha=0.5, color=color1)
        ax2.set_xlabel("Viscosity / (Pa·s)")
        ax2.set_ylabel("Count")
        ax2.grid(True, alpha=0.3, linestyle="--")

        ax3 = fig.add_subplot(2, 2, 3, projection="3d")
        ax3.scatter(x_cart, y_cart, vi_md, c=color1, s=10, alpha=0.5)
        ax3.set_xlabel("x")
        ax3.set_ylabel("y")
        ax3.set_zlabel("η (Pa·s)")

        ax4 = fig.add_subplot(2, 2, 4)
        names = list(binary_results.keys())
        rmse_vals = [binary_results[n].get("rmse", 0) for n in names]
        ax4.bar(names, rmse_vals, color=color2, alpha=0.7)
        ax4.set_ylabel("RMSE (Pa·s)")
        ax4.set_title("Binary Model RMSE")
        ax4.grid(True, alpha=0.3, linestyle="--")

        fig.tight_layout()
        self._plot_panel._canvas.draw()
        self.resultLabel.setText("Ternary Viscosity Fit Analysis")
        binary_results = result.get("binary_results", {})
        names = list(binary_results.keys())
        rmse_vals = [binary_results[n].get("rmse", 0) for n in names]
        ax4.bar(names, rmse_vals, color=color2, alpha=0.7)
        ax4.set_ylabel("RMSE (mPa·s)")
        ax4.set_title("Binary Model RMSE")
        ax4.grid(True, alpha=0.3, linestyle="--")

        fig.tight_layout()
        self._plot_panel._canvas.draw()

    def _plotViscosityPredictContour(self, result: dict, plot_config) -> None:
        if not self._workflow_module or not hasattr(self._workflow_module, "is_fitted"):
            self.resultLabel.setText("Workflow module not available")
            return

        if not self._workflow_module.is_fitted:
            self.resultLabel.setText("Workflow not fitted")
            return

        grid_data = self._workflow_module.predictOnGrid(
            n_points=30, include_ternary_gp=True
        )
        vi_md_grid = np.array(grid_data["vi_md_grid"])
        vi_binary = np.array(grid_data["vi_binary"])
        vi_full = np.array(grid_data["vi_full"])
        gp_correction = np.array(grid_data["gp_correction"])
        x_cart_g = np.array(grid_data["x_cart_g"])
        y_cart_g = np.array(grid_data["y_cart_g"])
        x_cart_md = np.array(grid_data["x_cart_md"])
        y_cart_md = np.array(grid_data["y_cart_md"])

        triang = Triangulation(x_cart_g, y_cart_g)

        fig = self._plot_panel._figure
        fig.clear()

        datasets = [
            ("MD Data", vi_md_grid, "viscosity"),
            ("Binary Model", vi_binary, "viscosity"),
            ("Total (Binary + Ternary GP)", vi_full, "viscosity"),
            ("GP Correction", gp_correction, "correction"),
        ]

        VISC_VMIN, VISC_VMAX = 0.5, 3.0
        n_levels_v = 22
        levels_v = np.linspace(VISC_VMIN, VISC_VMAX, n_levels_v)
        sqrt3_2 = np.sqrt(3) / 2

        axes = fig.subplots(2, 2, subplot_kw={"aspect": "equal"})
        axes_flat = axes.ravel()

        for idx, ax in enumerate(axes_flat):
            label_text, vals, vtype = datasets[idx]

            vals = np.asarray(vals)
            if vals.size == 0:
                ax.text(
                    0.5,
                    0.5,
                    "No data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                continue

            valid = np.isfinite(vals)
            if not valid.all():
                t_tri = Triangulation(x_cart_g[valid], y_cart_g[valid])
                vals_plot = vals[valid]
            else:
                t_tri = triang
                vals_plot = vals

            if vtype == "viscosity":
                c = ax.tricontourf(t_tri, vals_plot, levels=levels_v, cmap="turbo")
                cs = ax.tricontour(
                    t_tri, vals_plot, levels=levels_v, colors="k", linewidths=0.3
                )
                ax.clabel(cs, levels_v[1::2], inline=True, fontsize=7, fmt="%.2f")
                cb = fig.colorbar(c, ax=ax, shrink=0.8, pad=0.05)
                cb.set_label("Viscosity / (mPa·s)")
            else:
                vlim = max(abs(vals_plot.min()), abs(vals_plot.max()))
                lev = np.linspace(-vlim, vlim, 21)
                c = ax.tricontourf(t_tri, vals_plot, levels=lev, cmap="RdBu_r")
                cs = ax.tricontour(
                    t_tri, vals_plot, levels=lev, colors="k", linewidths=0.3
                )
                ax.clabel(cs, lev[1::2], inline=True, fontsize=7, fmt="%.2f")
                cb = fig.colorbar(c, ax=ax, shrink=0.8, pad=0.05)
                cb.set_label("Δ Viscosity / (mPa·s)")

            tri_x = [0, 1, 0.5, 0]
            tri_y = [0, 0, sqrt3_2, 0]
            ax.plot(tri_x, tri_y, "k-", linewidth=0.8)

            ax.text(0, -0.04, "Ti", ha="center", va="top", fontsize=12)
            ax.text(1, -0.04, "Al", ha="center", va="top", fontsize=12)
            ax.text(0.5, sqrt3_2 + 0.03, "Ni", ha="center", va="bottom", fontsize=12)

            ax.set_xlim(-0.05, 1.05)
            ax.set_ylim(-0.05, sqrt3_2 + 0.08)
            ax.axis("off")

            ax.scatter(
                x_cart_md, y_cart_md, c="white", s=8, alpha=0.4, edgecolors="none"
            )

            label = chr(97 + idx)
            ax.text(
                0.5,
                -0.18,
                f"({label}) {label_text}",
                transform=ax.transAxes,
                ha="center",
                fontsize=11,
            )

        fig.tight_layout()
        self._plot_panel._canvas.draw()
        self.resultLabel.setText("Ternary Viscosity Contour (2x2)")

    def _plot_single_viscosity_point(self, result: dict, plot_config) -> None:
        eta = result.get("eta", 0)
        x_A = result.get("x_A", 0)
        x_B = result.get("x_B", 0)
        x_C = result.get("x_C", 0)

        self._plot_panel.plotSinglePoint(
            plot_config, 0, eta, x_label="Ti-Al-Ni", y_label="η (Pa·s)"
        )
        self.resultLabel.setText(
            f"η = {eta:.4f} Pa·s at x = ({x_A:.2f}, {x_B:.2f}, {x_C:.2f})"
        )

    def _displaySurfaceResult(self, result: dict, plot_config) -> None:
        if "x_bulk_A" in result and isinstance(result["x_bulk_A"], list):
            self._plotSurfaceCurve(result, plot_config)
        elif "sigma" in result:
            self._plot_single_point(
                plot_config, 0, result["sigma"], x_label="", y_label="σ (N/m)"
            )
            self.resultLabel.setText(
                f"σ = {result['sigma']:.4f} N/m, x_A^s = {result.get('x_A_surface', '?')}"
            )
        else:
            self.resultLabel.setText(str(result))

    def _plotSurfaceCurve(self, result: dict, plot_config) -> None:
        x_bulk_A = np.array(result["x_bulk_A"])
        sigma = np.array(result["sigma"])
        x_A_surface = np.array(result.get("x_A_surface", []))

        fig = self._plot_panel._figure
        fig.clear()

        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x_bulk_A, sigma, "b-", linewidth=1.5, label="σ")
        ax.set_xlabel("x_bulk_A")
        ax.set_ylabel("σ (N/m)")
        ax.grid(True, alpha=0.3)

        if len(x_A_surface) > 0:
            ax2 = ax.twinx()
            ax2.plot(x_bulk_A, x_A_surface, "r--", linewidth=1.0, label="x_A^s")
            ax2.set_ylabel("x_A^s", color="r")

        ax.legend()

        fig.tight_layout()
        self._plot_panel._canvas.draw()
        self.resultLabel.setText(
            f"Surface Tension Isotherm at T={result.get('T', '?')} K"
        )

    def _plot_single_point(
        self, plot_config, x: float, y: float, x_label: str, y_label: str
    ) -> None:
        self._plot_panel.plotSinglePoint(plot_config, x, y, x_label, y_label)

    def _displayGenericResult(self, result: dict, plot_config) -> None:
        self.resultLabel.setText(str(result))

    def _retranslateUi(self):
        self.configureButton.setText(self._i18n.tr("Configure"))
        self.runButton.setText(self._i18n.tr("Run"))
