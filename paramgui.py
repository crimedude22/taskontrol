#!/usr/bin/env python

'''
Define objects to set protocol parameters graphically.

Parameters can set either with:
- Label + LineEdit
- Menu ???

TODO:
- Make both label and text expanding horizontally

'''


__version__ = '0.0.1'
__author__ = 'Santiago Jaramillo <jara@cshl.edu>'
__created__ = '2009-11-14'

import sys
from PyQt4 import QtCore 
from PyQt4 import QtGui 

# FIXME: Add validation of numbers
#NUMERIC_REGEXP = 

class NumericParam(QtGui.QWidget):
    def __init__(self, labelText=QtCore.QString(), value=0, labelWidth=80, parent=None):
        super(NumericParam, self).__init__(parent)

        # -- Define graphical interface --
        self.label = QtGui.QLabel(labelText)
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setAlignment(QtCore.Qt.AlignRight)
        self.label.setBuddy(self.lineEdit)
        #self.lineEdit.setFixedWidth(labelWidth)
        self.label.setFixedWidth(labelWidth)
        layout = QtGui.QHBoxLayout(spacing=0,margin=0)
        layout.addWidget(self.lineEdit)
        layout.addSpacing(4)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # -- Define value --
        self._value = None
        self.setValue(value)

    def setValue(self,value):
        self._value = value
        self.lineEdit.setText(str(value))

    def getValue(self):
        return float(self.lineEdit.text())



class MenuParam(QtGui.QWidget):
    def __init__(self, labelText=QtCore.QString(), menuItems=(), value=0,
                 labelWidth=80, parent=None):
        super(MenuParam, self).__init__(parent)

        # -- Define graphical interface --
        self.label = QtGui.QLabel(labelText)
        self.comboBox = QtGui.QComboBox()
        self.comboBox.addItems(menuItems)
        self.label.setBuddy(self.comboBox)
        #self.comboBox.setFixedWidth(labelWidth)
        self.label.setFixedWidth(labelWidth)
        layout = QtGui.QHBoxLayout(spacing=0,margin=0)
        layout.addWidget(self.comboBox)
        layout.addSpacing(4)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # -- Define value --
        self._value = None
        self._items = menuItems
        self.setValue(value)

    def setValue(self,value):
        self._value = value
        self.comboBox.setCurrentIndex(value)

    def setString(self,newstring):
        # FIXME: graceful warning if wrong string (ValueError exception)
        value = self._items.index(newstring)
        self._value = value
        self.comboBox.setCurrentIndex(value)

    def getValue(self):
        return self.comboBox.currentIndex()

    def getString(self):
        return str(self.comboBox.currentText())

    def getItems(self):
        return self._items


class TestForm(QtGui.QDialog):
    def __init__(self, parent=None):
        super(TestForm, self).__init__(parent)
        # -- Create graphical objects --
        self.resize(400,300)
        #self.value = QtGui.QLineEdit()
        #Orientation=QtCore.Qt.Vertical
        self.value1 = NumericParam('OneParam')
        self.value2 = NumericParam('aVeryVerVeryVeryyLongParam')
        self.val = []
        for ind in range(10):
            self.val.append(NumericParam(str(ind)))
            
        self.menu1 = MenuParam('TheMenu',('One','Two','Three'))

        # -- Create layouts --
        self.group = QtGui.QGroupBox('Section')
        self.group.setFixedWidth(200)
        self.groupLayout = QtGui.QVBoxLayout()
        self.groupLayout.setSpacing(0)
        layout = QtGui.QVBoxLayout()
        layout.addStretch()
        #for ind in range(10):
        #    layout.addWidget(self.val[ind])
        
        #self.groupLayout.addStretch()
        self.groupLayout.addWidget(self.value1)
        self.groupLayout.addWidget(self.value2)
        self.groupLayout.addWidget(self.menu1)
        #self.groupLayout.addStretch()
        self.group.setLayout(self.groupLayout)
        layout.addWidget(self.group)
        #layout.addStretch()
        self.setLayout(layout)

        # Change font to bold
        if 0:
            f=self.group.font()
            f.setBold(True)
            self.group.setFont(f)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    form = TestForm()
    form.show()
    app.exec_()
