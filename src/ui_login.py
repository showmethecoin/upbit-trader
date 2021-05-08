# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(450, 764)
        Form.setMinimumSize(QtCore.QSize(0, 0))
        Form.setStyleSheet("background-color: #31363b;\n"
                           "color: rgb(200, 200, 200);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.top_frame = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.top_frame.sizePolicy().hasHeightForWidth())
        self.top_frame.setSizePolicy(sizePolicy)
        self.top_frame.setMinimumSize(QtCore.QSize(300, 40))
        self.top_frame.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.top_frame.setFont(font)
        self.top_frame.setAutoFillBackground(False)
        self.top_frame.setStyleSheet("background-color: rgb(40,40,40);\n"
                                     "\n"
                                     "")
        self.top_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_frame.setObjectName("top_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.top_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.top_label = QtWidgets.QFrame(self.top_frame)
        self.top_label.setStyleSheet("")
        self.top_label.setObjectName("top_label")
        self.frame_label_top_btn_2 = QtWidgets.QHBoxLayout(self.top_label)
        self.frame_label_top_btn_2.setContentsMargins(4, 0, 0, 0)
        self.frame_label_top_btn_2.setSpacing(0)
        self.frame_label_top_btn_2.setObjectName("frame_label_top_btn_2")
        self.toplabel_icon = QtWidgets.QFrame(self.top_label)
        self.toplabel_icon.setMinimumSize(QtCore.QSize(0, 0))
        self.toplabel_icon.setMaximumSize(QtCore.QSize(30, 30))
        self.toplabel_icon.setSizeIncrement(QtCore.QSize(0, 0))
        self.toplabel_icon.setStyleSheet("background-image: url(./src/asset/icons/16x16/cil-chart-line.png);\n"
                                         "background-position: center;\n"
                                         "background-repeat: no-repeat;\n"
                                         "")
        self.toplabel_icon.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.toplabel_icon.setFrameShadow(QtWidgets.QFrame.Raised)
        self.toplabel_icon.setObjectName("toplabel_icon")
        self.frame_label_top_btn_2.addWidget(self.toplabel_icon)
        self.toplabel_title = QtWidgets.QLabel(self.top_label)
        self.toplabel_title.setSizeIncrement(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.toplabel_title.setFont(font)
        self.toplabel_title.setStyleSheet("margin-left: 3px;")
        self.toplabel_title.setScaledContents(False)
        self.toplabel_title.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.toplabel_title.setWordWrap(False)
        self.toplabel_title.setOpenExternalLinks(False)
        self.toplabel_title.setObjectName("toplabel_title")
        self.frame_label_top_btn_2.addWidget(self.toplabel_title)
        self.horizontalLayout.addWidget(self.top_label)
        self.frame_btn_right = QtWidgets.QFrame(self.top_frame)
        self.frame_btn_right.setEnabled(True)
        self.frame_btn_right.setMaximumSize(QtCore.QSize(120, 16777215))
        self.frame_btn_right.setStyleSheet("")
        self.frame_btn_right.setObjectName("frame_btn_right")
        self.frame_btn_2 = QtWidgets.QHBoxLayout(self.frame_btn_right)
        self.frame_btn_2.setContentsMargins(0, 0, 0, 0)
        self.frame_btn_2.setSpacing(0)
        self.frame_btn_2.setObjectName("frame_btn_2")
        self.minimize_btn = QtWidgets.QPushButton(self.frame_btn_right)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.minimize_btn.sizePolicy().hasHeightForWidth())
        self.minimize_btn.setSizePolicy(sizePolicy)
        self.minimize_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.minimize_btn.setMaximumSize(QtCore.QSize(40, 40))
        self.minimize_btn.setStatusTip("")
        self.minimize_btn.setWhatsThis("")
        self.minimize_btn.setAccessibleName("")
        self.minimize_btn.setStyleSheet("QPushButton {    \n"
                                        "    border: none;\n"
                                        "    background-color: transparent;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(52, 59, 72);\n"
                                        "}\n"
                                        "QPushButton:pressed {    \n"
                                        "    background-color: rgb(85, 170, 255);\n"
                                        "}")
        self.minimize_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            "./src/asset/icons/16x16/cil-window-minimize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimize_btn.setIcon(icon)
        self.minimize_btn.setObjectName("minimize_btn")
        self.frame_btn_2.addWidget(self.minimize_btn)
        self.maximize_btn = QtWidgets.QPushButton(self.frame_btn_right)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.maximize_btn.sizePolicy().hasHeightForWidth())
        self.maximize_btn.setSizePolicy(sizePolicy)
        self.maximize_btn.setMaximumSize(QtCore.QSize(40, 40))
        self.maximize_btn.setStyleSheet("QPushButton {    \n"
                                        "    border: none;\n"
                                        "    background-color: transparent;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(52, 59, 72);\n"
                                        "}\n"
                                        "QPushButton:pressed {    \n"
                                        "    background-color: rgb(85, 170, 255);\n"
                                        "}")
        self.maximize_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            "./src/asset/icons/16x16/cil-window-maximize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.maximize_btn.setIcon(icon1)
        self.maximize_btn.setObjectName("maximize_btn")
        self.frame_btn_2.addWidget(self.maximize_btn)
        self.close_btn = QtWidgets.QPushButton(self.frame_btn_right)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.close_btn.sizePolicy().hasHeightForWidth())
        self.close_btn.setSizePolicy(sizePolicy)
        self.close_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.close_btn.setMaximumSize(QtCore.QSize(40, 40))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.close_btn.setFont(font)
        self.close_btn.setStyleSheet("QPushButton {    \n"
                                     "    border: none;\n"
                                     "    background-color: transparent;\n"
                                     "}\n"
                                     "QPushButton:hover {\n"
                                     "    background-color: rgb(52, 59, 72);\n"
                                     "}\n"
                                     "QPushButton:pressed {    \n"
                                     "    background-color: rgb(85, 170, 255);\n"
                                     "}")
        self.close_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(
            "./src/asset/icons/16x16/cil-x.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.close_btn.setIcon(icon2)
        self.close_btn.setIconSize(QtCore.QSize(20, 20))
        self.close_btn.setObjectName("close_btn")
        self.frame_btn_2.addWidget(self.close_btn)
        self.horizontalLayout.addWidget(self.frame_btn_right)
        self.verticalLayout.addWidget(self.top_frame)
        self.content = QtWidgets.QFrame(Form)
        self.content.setStyleSheet("")
        self.content.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.content.setFrameShadow(QtWidgets.QFrame.Raised)
        self.content.setObjectName("content")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.content)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.login_area = QtWidgets.QFrame(self.content)
        self.login_area.setMaximumSize(QtCore.QSize(450, 550))
        self.login_area.setStyleSheet("border-radius: 10px;")
        self.login_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.login_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.login_area.setObjectName("login_area")
        self.avatar = QtWidgets.QFrame(self.login_area)
        self.avatar.setGeometry(QtCore.QRect(150, 130, 121, 121))
        self.avatar.setStyleSheet("QFrame {\n"
                                  "    border-radius: 60px;\n"
                                  "    border: 10px solid rgb(85, 170, 255);\n"
                                  "    background-position: center;\n"
                                  "}\n"
                                  "\n"
                                  "")
        self.avatar.setObjectName("avatar")
        self.label_2 = QtWidgets.QLabel(self.avatar)
        self.label_2.setGeometry(QtCore.QRect(4, 0, 117, 121))
        font = QtGui.QFont()
        font.setPointSize(45)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color : rgb(85, 170, 255);\n"
                                   "border: 0px solid rgb(85, 170, 255);\n"
                                   "background-position: center;\n"
                                   "background: transparent;")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.lineEdit_access = QtWidgets.QLineEdit(self.login_area)
        self.lineEdit_access.setGeometry(QtCore.QRect(80, 290, 271, 50))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.lineEdit_access.setFont(font)
        self.lineEdit_access.setStyleSheet("QLineEdit {\n"
                                           "    border: 2px solid rgb(45, 45, 45);\n"
                                           "    border-radius: 5px;\n"
                                           "    padding: 15px;\n"
                                           "    background-color: rgb(30, 30, 30);    \n"
                                           "    color: rgb(100, 100, 100);\n"
                                           "}\n"
                                           "\n"
                                           "QLineEdit:focus {\n"
                                           "    border: 2px solid rgb(85, 170, 255);\n"
                                           "    color: rgb(0, 200, 200);\n"
                                           "}")
        self.lineEdit_access.setText("")
        self.lineEdit_access.setMaxLength(50)
        self.lineEdit_access.setObjectName("lineEdit_access")
        self.lineEdit_secret = QtWidgets.QLineEdit(self.login_area)
        self.lineEdit_secret.setGeometry(QtCore.QRect(80, 360, 271, 50))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.lineEdit_secret.setFont(font)
        self.lineEdit_secret.setStyleSheet("QLineEdit {\n"
                                           "    border: 2px solid rgb(45, 45, 45);\n"
                                           "    border-radius: 5px;\n"
                                           "    padding: 15px;\n"
                                           "    background-color: rgb(30, 30, 30);    \n"
                                           "    color: rgb(100, 100, 100);\n"
                                           "}\n"
                                           "\n"
                                           "QLineEdit:focus {\n"
                                           "    border: 2px solid rgb(85, 170, 255);\n"
                                           "    color: rgb(200, 200, 200);\n"
                                           "}")
        self.lineEdit_secret.setMaxLength(50)
        self.lineEdit_secret.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_secret.setObjectName("lineEdit_secret")
        self.checkBox_save_user = QtWidgets.QCheckBox(self.login_area)
        self.checkBox_save_user.setGeometry(QtCore.QRect(80, 440, 281, 22))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_save_user.setFont(font)
        self.checkBox_save_user.setStyleSheet("QCheckBox::indicator {\n"
                                              "    border: 3px solid rgb(100, 100, 100);\n"
                                              "    width: 15px;\n"
                                              "    height: 15px;\n"
                                              "    border-radius: 10px;    \n"
                                              "    background-color: rgb(135, 135, 135);\n"
                                              "}\n"
                                              "QCheckBox::indicator:checked {\n"
                                              "    border: 3px solid rgb(85, 170, 255);\n"
                                              "    background-color: rgb(85, 120, 255);\n"
                                              "}")
        self.checkBox_save_user.setObjectName("checkBox_save_user")
        self.pushButton_connect = QtWidgets.QPushButton(self.login_area)
        self.pushButton_connect.setGeometry(QtCore.QRect(80, 490, 271, 50))
        self.pushButton_connect.setStyleSheet("QPushButton {    \n"
                                              "    background-color: rgb(30, 30, 30);\n"
                                              "    border: 2px solid rgb(60, 60, 60);\n"
                                              "    border-radius: 5px;\n"
                                              "}\n"
                                              "QPushButton:hover {    \n"
                                              "    background-color: rgb(60, 60, 60);\n"
                                              "    border: 2px solid rgb(70, 70, 70);\n"
                                              "}\n"
                                              "QPushButton:pressed {    \n"
                                              "    background-color: rgb(85, 170, 255);\n"
                                              "    border: 2px solid rgb(85, 170, 255);\n"
                                              "    color: rgb(35, 35, 35);\n"
                                              "}")
        self.pushButton_connect.setObjectName("pushButton_connect")
        self.label = QtWidgets.QLabel(self.login_area)
        self.label.setGeometry(QtCore.QRect(30, 10, 361, 101))
        font = QtGui.QFont()
        font.setFamily("Masque")
        font.setPointSize(40)
        self.label.setFont(font)
        self.label.setStyleSheet("color : rgb(85, 170, 255);")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.login_area)
        self.verticalLayout.addWidget(self.content)
        self.bottom = QtWidgets.QFrame(Form)
        self.bottom.setMaximumSize(QtCore.QSize(16777215, 35))
        self.bottom.setStyleSheet("background-color: rgb(15, 15, 15)")
        self.bottom.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.bottom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.bottom.setObjectName("bottom")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.bottom)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_credits = QtWidgets.QLabel(self.bottom)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.label_credits.setFont(font)
        self.label_credits.setStyleSheet("color: rgb(75, 75, 75);")
        self.label_credits.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_credits.setObjectName("label_credits")
        self.verticalLayout_2.addWidget(self.label_credits)
        self.verticalLayout.addWidget(self.bottom)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.toplabel_title.setText(_translate("Form", "ShowMeTheCoin v1.0"))
        self.minimize_btn.setToolTip(_translate("Form", "Minimize"))
        self.maximize_btn.setToolTip(_translate("Form", "Maximize"))
        self.close_btn.setToolTip(_translate("Form", "Close"))
        self.label_2.setText(_translate("Form", "₿"))
        self.lineEdit_access.setPlaceholderText(
            _translate("Form", "Access Key"))
        self.lineEdit_secret.setPlaceholderText(
            _translate("Form", "Secret Key"))
        self.checkBox_save_user.setText(_translate("Form", "SAVE USER"))
        self.pushButton_connect.setText(_translate("Form", "CONNECT"))
        self.label.setText(_translate("Form", "SIGN IN"))
        self.label_credits.setText(_translate(
            "Form", "Created by: Wanderson M. Pimenta"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())