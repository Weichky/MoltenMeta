import numpy as np

from matplotlib.tri import Triangulation
import matplotlib as mpl

from catalog.plot_style import (
    DEFAULT_TRIANGULAR_COORD_FACTOR,
    DEFAULT_TICK_LINE_WIDTH,
    DEFAULT_TRIANGLE_BORDER_LINE_WIDTH,
    DEFAULT_TICK_HALF_LENGTH_RATIO,
    DEFAULT_SINGLE_TICK_LABEL_OFFSET,
    DEFAULT_ELEMENT_LABEL_OFFSET,
    DEFAULT_APEX_LABEL_OFFSET,
    DEFAULT_LABEL_DISTANCE,
    DEFAULT_COLORBAR_TICK_COUNT,
    COMPOSITION_TOLERANCE_LOW,
    COMPOSITION_TOLERANCE_HIGH,
    DEFAULT_Z_EDGE_EPSILON,
    DEFAULT_NORMALIZED_EPSILON,
    DEFAULT_COLORMAP_RESOLUTION,
    DEFAULT_CONTOUR_TRIANGULAR_LINE_WIDTH,
)

from core.plot.latex_utils import wrap_latex


def drawTriangularAxes(
    ax,
    style,
    h: float,
    xlim: list[float],
    ylim: list[float],
    tick_length: float,
    elem_labels: list[str],
    plane: str = "x_A-x_B",
    gridLabelDensity: float = 1.0,
) -> None:
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_aspect("equal")
    ax.axis("off")

    # Triangle vertices in Cartesian coordinates (equilateral, side=1):
    #   B (left base):    (0,     0)
    #   C (right base):   (1,     0)
    #   A (apex):         (0.5,   sqrt(3)/2)
    # The apex x-coordinate = 0.5 = DEFAULT_TRIANGULAR_COORD_FACTOR
    triangle_x = [0, 1, DEFAULT_TRIANGULAR_COORD_FACTOR, 0]
    triangle_y = [0, 0, h, 0]
    ax.plot(triangle_x, triangle_y, "k-", linewidth=DEFAULT_TRIANGLE_BORDER_LINE_WIDTH)

    # Map element labels to triangle vertices for each projection plane.
    # The plane determines which two composition variables are on the axes,
    # and which element is projected out (the "vertical" axis).
    # x_A-x_B: x_C is height (A apex, B left base, C right base)
    # x_A-x_C: x_B is height (A apex, C left base, B right base) - left/right swapped
    # x_B-x_C: x_A is height (B apex, C left base, A right base) - all positions rotated
    if plane == "x_A-x_B":
        label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
        label_b = elem_labels[1] if len(elem_labels) > 1 else "B"
        label_c = elem_labels[2] if len(elem_labels) > 2 else "C"
    elif plane == "x_A-x_C":
        label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
        label_b = elem_labels[2] if len(elem_labels) > 2 else "C"
        label_c = elem_labels[1] if len(elem_labels) > 1 else "B"
    elif plane == "x_B-x_C":
        label_a = elem_labels[1] if len(elem_labels) > 1 else "B"
        label_b = elem_labels[2] if len(elem_labels) > 2 else "C"
        label_c = elem_labels[0] if len(elem_labels) > 0 else "A"
    else:
        label_a = elem_labels[0] if len(elem_labels) > 0 else "A"
        label_b = elem_labels[1] if len(elem_labels) > 1 else "B"
        label_c = elem_labels[2] if len(elem_labels) > 2 else "C"

    if style.gridMode == "auto":
        n_ticks = DEFAULT_COLORBAR_TICK_COUNT
    elif style.gridMode == "absolute":
        n_ticks = max(1, round(style.gridDensity))
    else:
        n_ticks = max(1, round(style.gridDensity * 10))

    tick_interval = 1.0 / n_ticks

    label_every = max(1, round(gridLabelDensity))
    display_ticks = []
    for i in range(1, n_ticks):
        display_ticks.append((round(i * tick_interval, 2), i % label_every == 0))

    for t, show_label in display_ticks:
        ax.plot([t, t], [-tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO, tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO], "k-", linewidth=DEFAULT_TICK_LINE_WIDTH)
        if show_label:
            ax.text(
                t,
                DEFAULT_SINGLE_TICK_LABEL_OFFSET,
                f"{t:.2f}",
                ha="center",
                va="top",
                fontsize=style.tickFontSize,
            )

    left_nx, left_ny = -h, DEFAULT_TRIANGULAR_COORD_FACTOR
    left_len = (left_nx * left_nx + left_ny * left_ny) ** 0.5
    left_nx, left_ny = left_nx / left_len, left_ny / left_len

    for t, show_label in display_ticks:
        x_on_left = t * DEFAULT_TRIANGULAR_COORD_FACTOR
        y_on_left = t * h
        ax.plot(
            [x_on_left - left_nx * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO, x_on_left + left_nx * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO],
            [y_on_left - left_ny * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO, y_on_left + left_ny * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO],
            "k-",
            linewidth=DEFAULT_TICK_LINE_WIDTH,
        )
        if show_label:
            label_x = x_on_left + left_nx * DEFAULT_LABEL_DISTANCE
            label_y = y_on_left + left_ny * DEFAULT_LABEL_DISTANCE
            ax.text(
                label_x,
                label_y,
                f"{1 - t:.2f}",
                ha="right",
                va="center",
                fontsize=style.tickFontSize,
            )

    right_nx, right_ny = h, DEFAULT_TRIANGULAR_COORD_FACTOR
    right_len = (right_nx * right_nx + right_ny * right_ny) ** 0.5
    right_nx, right_ny = right_nx / right_len, right_ny / right_len

    for t, show_label in display_ticks:
        x_on_right = 1 - t * DEFAULT_TRIANGULAR_COORD_FACTOR
        y_on_right = t * h
        ax.plot(
            [x_on_right - right_nx * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO, x_on_right + right_nx * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO],
            [y_on_right - right_ny * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO, y_on_right + right_ny * tick_length * DEFAULT_TICK_HALF_LENGTH_RATIO],
            "k-",
            linewidth=DEFAULT_TICK_LINE_WIDTH,
        )
        if show_label:
            label_x = x_on_right + right_nx * DEFAULT_LABEL_DISTANCE
            label_y = y_on_right + right_ny * DEFAULT_LABEL_DISTANCE
            ax.text(
                label_x,
                label_y,
                f"{t:.2f}",
                ha="left",
                va="center",
                fontsize=style.tickFontSize,
            )

    ax.text(
        DEFAULT_TRIANGULAR_COORD_FACTOR,
        h + DEFAULT_APEX_LABEL_OFFSET,
        label_a,
        ha="center",
        va="bottom",
        fontsize=style.labelFontSize,
    )
    ax.text(
        DEFAULT_SINGLE_TICK_LABEL_OFFSET,
        DEFAULT_ELEMENT_LABEL_OFFSET,
        label_b,
        ha="right",
        va="top",
        fontsize=style.labelFontSize,
    )
    ax.text(
        1.015,
        DEFAULT_ELEMENT_LABEL_OFFSET,
        label_c,
        ha="left",
        va="top",
        fontsize=style.labelFontSize,
    )


def renderTriangularContour(
    figure,
    ax,
    config,
    values: list[dict],
    conditions: dict | None = None,
    title: str | None = None,
    z_label: str | None = None,
    levels: int | None = None,
    plane: str = "x_A-x_B",
) -> None:
    style = config.style
    generator = config.colorGenerator
    h = config.triangular_height_factor
    xlim = config.triangular_xlim
    ylim = config.triangular_ylim
    tick_positions = config.triangular_tick_positions
    tick_length = config.triangular_tick_length
    plot_levels = levels if levels is not None else config.triangular_levels
    contour_alpha = config.triangular_alpha
    grid_alpha = config.triangular_grid_alpha
    grid_line_width = config.triangular_grid_line_width

    if conditions:
        elem_labels = [
            conditions.get("elem_A", "A"),
            conditions.get("elem_B", "B"),
            conditions.get("elem_C", "C"),
        ]
        plane = conditions.get("plane", plane)
    else:
        elem_labels = config.triangular_elem_labels

    final_colorbar_label = z_label if z_label else config.triangular_colorbar_label

    x_A_arr = np.array([v.get("x_A", 0) for v in values])
    x_B_arr = np.array([v.get("x_B", 0) for v in values])
    x_C_arr = np.array([v.get("x_C", 0) for v in values])
    z_key = next((k for k in values[0] if k not in ("x_A", "x_B", "x_C")), "Z_ABC")
    z_arr = np.array([v.get(z_key, 0) for v in values])

    if len(x_A_arr) == 0 or len(x_B_arr) == 0 or len(x_C_arr) == 0:
        return

    # Filter out NaN z-values, out-of-range compositions, and compositions
    # that don't sum to ~1 (within the tolerance band).
    # The tolerance band handles numerical noise from interpolation.
    valid_mask = (
        ~np.isnan(z_arr)
        & (x_A_arr >= 0)
        & (x_A_arr <= 1)
        & (x_B_arr >= 0)
        & (x_B_arr <= 1)
        & (x_C_arr >= 0)
        & (x_C_arr <= 1)
        & (x_A_arr + x_B_arr + x_C_arr > COMPOSITION_TOLERANCE_LOW)
        & (x_A_arr + x_B_arr + x_C_arr < COMPOSITION_TOLERANCE_HIGH)
    )

    if not np.any(valid_mask):
        return

    x_A_valid = x_A_arr[valid_mask]
    x_B_valid = x_B_arr[valid_mask]
    x_C_valid = x_C_arr[valid_mask]
    z_valid = z_arr[valid_mask]

    # Convert ternary fractions (x_A, x_B, x_C) to Cartesian coordinates.
    # For an equilateral triangle with side=1 and height h=sqrt(3)/2:
    #   x_cart positions the "in-plane" component along the base
    #   y_cart = h * (vertical component) gives height above the base
    #
    # x_A-x_B plane: x_C is "vertical" (projected out of page)
    #   x_cart = x_C + 0.5*x_A  (base position of x_C + offset from x_A)
    #   y_cart = h * x_A        (height due to x_A)
    # x_A-x_C plane: x_B is "vertical"
    #   x_cart = x_B + 0.5*x_A
    #   y_cart = h * x_A
    # x_B-x_C plane: x_A is "vertical"
    #   x_cart = x_A + 0.5*x_B
    #   y_cart = h * x_B
    if plane == "x_A-x_B":
        x_cart = x_C_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_A_valid
        y_cart = h * x_A_valid
    elif plane == "x_A-x_C":
        x_cart = x_B_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_A_valid
        y_cart = h * x_A_valid
    elif plane == "x_B-x_C":
        x_cart = x_A_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_B_valid
        y_cart = h * x_B_valid
    else:
        x_cart = x_C_valid + DEFAULT_TRIANGULAR_COORD_FACTOR * x_A_valid
        y_cart = h * x_A_valid

    triang = Triangulation(x_cart, y_cart)

    z_min = np.min(z_valid)
    z_max = np.max(z_valid)
    if z_min == z_max:
        z_min = z_min - DEFAULT_Z_EDGE_EPSILON
        z_max = z_max + DEFAULT_Z_EDGE_EPSILON
    contour_levels = np.linspace(z_min, z_max, plot_levels)

    if generator:
        n_cmap = DEFAULT_COLORMAP_RESOLUTION
        cmap_colors = [generator.getColorAt(i / (n_cmap - 1)) for i in range(n_cmap)]
        cmap = mpl.colors.ListedColormap(cmap_colors)
        cmap.set_under("white")
        cmap.set_over("white")
        z_normalized = (z_valid - z_min) / (z_max - z_min + DEFAULT_NORMALIZED_EPSILON)
        cf = ax.tricontourf(
            triang,
            z_normalized,
            levels=np.linspace(0, 1, plot_levels),
            cmap=cmap,
            alpha=contour_alpha,
            extend="neither",
        )
        ax.tricontour(
            triang, z_valid, levels=contour_levels, colors="white", linewidths=DEFAULT_CONTOUR_TRIANGULAR_LINE_WIDTH
        )
    else:
        cf = ax.tricontourf(
            triang,
            z_valid,
            levels=contour_levels,
            cmap="viridis",
            alpha=contour_alpha,
        )

    cbar = figure.colorbar(cf, ax=ax)
    cbar.set_label(
        wrap_latex(final_colorbar_label), fontsize=style.labelFontSize
    )
    cbar.ax.tick_params(labelsize=style.tickFontSize)

    if style.gridMode == "auto":
        cbar_ticks = DEFAULT_COLORBAR_TICK_COUNT
    elif style.gridMode == "absolute":
        cbar_ticks = max(1, round(style.gridDensity))
    else:
        cbar_ticks = max(1, round(style.gridDensity * 10))

    label_every = max(1, round(style.gridLabelDensity))
    tick_positions = np.linspace(0, 1, cbar_ticks)
    tick_vals = np.linspace(z_min, z_max, cbar_ticks)
    labels = [f"{v:.4g}" if i % label_every == 0 else "" for i, v in enumerate(tick_vals)]
    cbar.set_ticks(tick_positions)
    cbar.set_ticklabels(labels)

    # Overlay triangular grid lines at composition intervals t = k/grid_n.
    # Grid lines are drawn for the x_A-x_B plane orientation.
    if style.grid:
        if style.gridMode == "auto":
            grid_n = DEFAULT_COLORBAR_TICK_COUNT
        elif style.gridMode == "absolute":
            grid_n = int(round(style.gridDensity))
        else:
            grid_n = int(round(style.gridDensity * 10))

        for k in range(1, grid_n):
            t = k / grid_n

            # Horizontal lines (constant x_A, parallel to base BC):
            #   Left endpoint:  (t/2, t*h)
            #   Right endpoint: (1 - t/2, t*h)
            y_grid = t * h
            x_left = t / 2
            x_right = 1 - t / 2
            ax.plot([x_left, x_right], [y_grid, y_grid], "k-", alpha=grid_alpha, linewidth=grid_line_width)

            # Line AB (constant x_C, from left side to right side):
            #   Start: midpoint of left edge at height (1-t)
            #   End: right base vertex
            x_start_ab = (1 - t) / 2
            y_start_ab = h * (1 - t)
            x_end_bc = 1 - t
            y_end_bc = 0
            ax.plot([x_start_ab, x_end_bc], [y_start_ab, y_end_bc], "k-", alpha=grid_alpha, linewidth=grid_line_width)

            # Line AC (constant x_B, from apex-adjacent to left base):
            #   Start: right of center at height (1-t)
            #   End: left base vertex
            x_start_ac = t + DEFAULT_TRIANGULAR_COORD_FACTOR * (1 - t)
            y_start_ac = h * (1 - t)
            x_end_bc = t
            y_end_bc = 0
            ax.plot([x_start_ac, x_end_bc], [y_start_ac, y_end_bc], "k-", alpha=grid_alpha, linewidth=grid_line_width)

    drawTriangularAxes(
        ax,
        style,
        h,
        xlim,
        ylim,
        tick_length,
        elem_labels,
        plane,
        style.gridLabelDensity,
    )

    final_title = title if title else config.title
    if final_title:
        ax.set_title(
            wrap_latex(final_title), fontsize=style.titleFontSize
        )
