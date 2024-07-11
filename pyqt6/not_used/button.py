# Form implementation generated from reading ui file 'listwidget.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1260, 800)
        MainWindow.setStyleSheet("background-color: rgb(222, 221, 218);")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(34, 71, 1061, 201))
        self.listWidget.setStyleSheet("")
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.listWidget.setObjectName("listWidget")
        self.Select_Device = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Select_Device.setGeometry(QtCore.QRect(1130, 130, 101, 61))
        self.Select_Device.setObjectName("Select_Device")
        self.Logs = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Logs.setGeometry(QtCore.QRect(1130, 530, 101, 61))
        self.Logs.setObjectName("Logs")
        self.Exit = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Exit.setGeometry(QtCore.QRect(1130, 630, 101, 61))
        self.Exit.setObjectName("Exit")
        self.Select_Test_Tabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.Select_Test_Tabel.setGeometry(QtCore.QRect(30, 30, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Select_Test_Tabel.setFont(font)
        self.Select_Test_Tabel.setObjectName("Select_Test_Tabel")
        self.Select_all = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Select_all.setGeometry(QtCore.QRect(870, 30, 91, 31))
        self.Select_all.setObjectName("Select_all")
        self.Clear_all = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Clear_all.setGeometry(QtCore.QRect(980, 30, 91, 31))
        self.Clear_all.setObjectName("Clear_all")
        self.Start_Test = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Start_Test.setGeometry(QtCore.QRect(1130, 230, 101, 61))
        self.Start_Test.setStyleSheet("background-color: rgb(143, 240, 164);")
        self.Start_Test.setObjectName("Start_Test")
        self.Stop_Test = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Stop_Test.setGeometry(QtCore.QRect(1130, 330, 101, 61))
        self.Stop_Test.setStyleSheet("background-color: rgb(246, 97, 81);")
        self.Stop_Test.setObjectName("Stop_Test")
        self.Show_Result = QtWidgets.QPushButton(parent=self.centralwidget)
        self.Show_Result.setGeometry(QtCore.QRect(1130, 430, 101, 61))
        self.Show_Result.setObjectName("Show_Result")
        self.About = QtWidgets.QPushButton(parent=self.centralwidget)
        self.About.setGeometry(QtCore.QRect(1130, 30, 101, 61))
        self.About.setObjectName("About")
        self.textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(40, 470, 1061, 281))
        self.textEdit.setStyleSheet("")
        self.textEdit.setObjectName("textEdit")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(35, 301, 341, 17))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.comboBox = QtWidgets.QComboBox(parent=self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(150, 30, 211, 25))
        self.comboBox.setObjectName("comboBox")
        self.Traces = QtWidgets.QLabel(parent=self.centralwidget)
        self.Traces.setGeometry(QtCore.QRect(40, 430, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Traces.setFont(font)
        self.Traces.setObjectName("Traces")
        self.progressBar = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(80, 340, 981, 23))
        self.progressBar.setStyleSheet("")
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.total_completed = QtWidgets.QLabel(parent=self.centralwidget)
        self.total_completed.setGeometry(QtCore.QRect(130, 440, 311, 17))
        self.total_completed.setObjectName("total_completed")
        self.clear_trace_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.clear_trace_button.setGeometry(QtCore.QRect(990, 430, 91, 31))
        self.clear_trace_button.setObjectName("clear_trace_button")
        self.running_test_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.running_test_label.setGeometry(QtCore.QRect(40, 390, 1051, 17))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.running_test_label.setFont(font)
        self.running_test_label.setObjectName("running_test_label")
        self.passed_test_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.passed_test_label.setGeometry(QtCore.QRect(490, 440, 161, 17))
        self.passed_test_label.setObjectName("passed_test_label")
        self.failed_test_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.failed_test_label.setGeometry(QtCore.QRect(730, 440, 171, 17))
        self.failed_test_label.setObjectName("failed_test_label")
        self.img_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.img_label.setGeometry(QtCore.QRect(470, 20, 261, 41))
        self.img_label.setText("")
        self.img_label.setPixmap(QtGui.QPixmap("Abeeway_LOGO_blue-small.png"))
        self.img_label.setScaledContents(True)
        self.img_label.setObjectName("img_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1260, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Select_Device.setText(_translate("MainWindow", "Select Device"))
        self.Logs.setText(_translate("MainWindow", "Logs"))
        self.Exit.setText(_translate("MainWindow", "Exit"))
        self.Select_Test_Tabel.setText(_translate("MainWindow", "Select Test :"))
        self.Select_all.setText(_translate("MainWindow", "Select all"))
        self.Clear_all.setText(_translate("MainWindow", "Clear all"))
        self.Start_Test.setText(_translate("MainWindow", "Start Test"))
        self.Stop_Test.setText(_translate("MainWindow", "Stop Test"))
        self.Show_Result.setText(_translate("MainWindow", "Show Result"))
        self.About.setText(_translate("MainWindow", "About"))
        self.label.setText(_translate("MainWindow", "Total number of test selected :"))
        self.Traces.setText(_translate("MainWindow", "Traces : "))
        self.total_completed.setText(_translate("MainWindow", "Total number of test completed :"))
        self.clear_trace_button.setText(_translate("MainWindow", "Clear Trace"))
        self.running_test_label.setText(_translate("MainWindow", "Running Test : "))
        self.passed_test_label.setText(_translate("MainWindow", "Passed Test : "))
        self.failed_test_label.setText(_translate("MainWindow", "Failed Test : "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
