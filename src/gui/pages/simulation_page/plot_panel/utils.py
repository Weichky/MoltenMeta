from core.plot.latex_utils import wrap_latex


def resolveLabels(
    x_label: str | None,
    y_label: str | None,
    config,
) -> tuple[str, str]:
    final_x = x_label if x_label is not None else (config.xLabel or config.x)
    final_y = (
        y_label
        if y_label is not None
        else (
            config.yLabels[0]
            if config.yLabels
            else (config.y[0] if config.y else "")
        )
    )
    return final_x, final_y


def setupAxis(ax, style, color: str) -> None:
    ax.set_xlabel(wrap_latex(""), fontsize=style.labelFontSize)
    ax.set_ylabel(wrap_latex(""), fontsize=style.labelFontSize)
    ax.tick_params(axis="both", labelsize=style.tickFontSize)
