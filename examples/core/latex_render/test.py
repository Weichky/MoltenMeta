# Source - https://stackoverflow.com/a/35758817
# Posted by Mad Physicist, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-11, License - CC BY-SA 3.0

import sys
import warnings
from io import BytesIO

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, Qt


def renderLatex(formula, fontsize=8, dpi=300, format='svg', file=None):
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


class LatexViewer(QMainWindow):
    """A Qt window to display rendered LaTeX formulas."""
    
    def __init__(self, svg_data: BytesIO, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LaTeX Formula Viewer")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Load SVG data
        svg_bytes = svg_data.read()
        byte_array = QByteArray(svg_bytes)
        
        # Render SVG using QSvgRenderer with high DPI support
        renderer= QSvgRenderer(byte_array)
        base_size = renderer.defaultSize()
        
        # Scale up for high DPI displays (retina/HiDPI)
        device_pixel_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 1.0
        if device_pixel_ratio < 2.0:
            device_pixel_ratio = 2.0  # At least 2x for crisp rendering
        
        scaled_width = int(base_size.width() * device_pixel_ratio)
        scaled_height = int(base_size.height() * device_pixel_ratio)
        
        # Create high-resolution pixmap
        pixmap = QPixmap(scaled_width, scaled_height)
        pixmap.fill(Qt.transparent)
        pixmap.setDevicePixelRatio(device_pixel_ratio)
        
        # Render at high quality
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        renderer.render(painter)
        painter.end()
        
        # Create label to display SVG
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)

def main():
    app = QApplication(sys.argv)
    
    # Render LaTeX formula
    formula = r'\Delta G=\Delta H-T\Delta S=nu+kT\left[N\ln{\frac{N}{N+n}}+n\ln{\frac{n}{N+n}}\right]'
    print(f"Rendering formula: {formula}")
    
    image_data = renderLatex(formula)
    
    # Save to file as well
    with open('latex_output.svg', 'wb') as f:
        f.write(image_data.getvalue())
    print("Saved SVG to latex_output.svg")
    
    # Reset buffer position for Qt
    image_data.seek(0)
    
    # Create and show viewer window
    viewer= LatexViewer(image_data)
    viewer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
