from qtpy.QtWidgets import QApplication
from pydm.widgets.label import PyDMLabel

app = QApplication([])
label = PyDMLabel(init_channel='ca://TEST:MAIN:SCALE_RBV')
label.show()
app.exec_()
