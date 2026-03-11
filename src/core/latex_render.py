# Source - https://stackoverflow.com/a/35758817
# Posted by Mad Physicist, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-05, License - CC BY-SA 3.0

# Modified by Weichky
from io import BytesIO
import warnings
import matplotlib.pyplot as plt

def renderLatex(formula, fontsize=12, dpi=300, format='svg', file=None):

    """Renders LaTeX formula into image or prints to file.
    """
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, u'${}$'.format(formula), fontsize=fontsize)

    output = BytesIO() if file is None else file
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning)
        fig.savefig(output, dpi=dpi, transparent=True, format=format,
                    bbox_inches='tight', pad_inches=0.0)

    plt.close(fig)

    if file is None:
        output.seek(0)
        return output

