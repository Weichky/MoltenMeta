from matplotlib.figure import Figure


def wrap_latex(text: str) -> str:
    if not text:
        return text
    if not any(c in text for c in ("\\", "^", "_", "{")):
        return text
    fig = Figure()
    ax = fig.add_subplot(111)
    try:
        ax.set_xlabel(f"${text}$")
        ax.set_ylabel(f"${text}$")
    except ValueError:
        return text
    return f"${text}$"
