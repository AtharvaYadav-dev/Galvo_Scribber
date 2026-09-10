# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interfacewhFvqA.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLCDNumber, QLabel, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTextEdit, QVBoxLayout,
    QWidget)

from Custom_Widgets.QCustomSlideMenu import QCustomSlideMenu
from Custom_Widgets.Widgets import QCustomStackedWidget
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(862, 577)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(862, 577))
        self.centralwidget.setStyleSheet(u"*{\n"
"	border: none;\n"
"	background-color:transparent;\n"
"	padding: 0;\n"
"	margin: 0;\n"
"	color: #fff;\n"
"}\n"
"\n"
"#centralwidget {\n"
"	background-color: rgb(31, 35, 42);\n"
"}\n"
"\n"
"#leftMenuSubContainer {	\n"
"	background-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"#leftMenuSubContainer QPushButton {\n"
"	text-align: left;\n"
"	padding: 5px 10px;\n"
"	border-top-left-radius: 10px;\n"
"	border-bottom-left-radius: 10px;\n"
"}\n"
"\n"
"#centerMenuFrame {\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-radius: 20px;\n"
"}\n"
"\n"
"#notifySubContainer {	\n"
"	background-color: rgb(22, 25, 29);\n"
"	border-radius: 10px;\n"
"}\n"
"\n"
"#headerContainer, #footerContainer {\n"
"	background-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"#centerSlideMenu {\n"
"	background-color: rgb(167, 198, 229);	\n"
"}\n"
"\n"
"#helpLabel, #infoLabel, #settingsLabel, #profileLabel {\n"
"	color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"#mainBodyContent {\n"
"	background-color: rgb(144, 170, 197);\n"
"}\n"
"\n"
"#infoSubFrame, #comFrame"
                        ", #jogFrame, #setFrame, #profilesubFrame {\n"
"	background-color: rgb(144, 170, 197);\n"
"	border-radius: 20px;\n"
"}\n"
"\n"
"#jogFrame, #laserconfFrame, #programFrame, #recipeFrame, #printFrame, #terminalFrame, #cameraFrame {\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-radius: 20px;\n"
"}\n"
"\n"
"#homeFrame, #stepsFrame, #xyFrame, #zFrame, #axisposFrame, #setfocusFrame, #flaserFrame, #zfocusFrame, #fsetFrame, #loffsetFrame, #offlaserFrame, #xyoffsetFrame, #xyposFrame, #offsetFrame, #offbtnFrame, #progFrame, #rcpFrame, #printimgFrame, #printopFrame, #printprogramFrame, #printprogressFrame, #camFrame, #cameraxyoffFrame, #objheightFrame{\n"
"	background-color: rgb(144, 170, 197);\n"
"	border-radius: 20px;\n"
"	border: 2px solid rgb(16, 42, 131);\n"
"}\n"
"")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenuContainer = QCustomSlideMenu(self.centralwidget)
        self.leftMenuContainer.setObjectName(u"leftMenuContainer")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leftMenuContainer.sizePolicy().hasHeightForWidth())
        self.leftMenuContainer.setSizePolicy(sizePolicy)
        self.leftMenuContainer.setMaximumSize(QSize(45, 16777215))
        self.verticalLayout = QVBoxLayout(self.leftMenuContainer)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenuSubContainer = QWidget(self.leftMenuContainer)
        self.leftMenuSubContainer.setObjectName(u"leftMenuSubContainer")
        self.verticalLayout_3 = QVBoxLayout(self.leftMenuSubContainer)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.topFrame = QFrame(self.leftMenuSubContainer)
        self.topFrame.setObjectName(u"topFrame")
        self.topFrame.setMinimumSize(QSize(0, 40))
        self.topFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.topFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_2 = QVBoxLayout(self.topFrame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.menuPushButton = QPushButton(self.topFrame)
        self.menuPushButton.setObjectName(u"menuPushButton")
        self.menuPushButton.setMinimumSize(QSize(0, 34))
        icon = QIcon()
        icon.addFile(u":/icons/icons/align-justify.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.menuPushButton.setIcon(icon)
        self.menuPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_2.addWidget(self.menuPushButton)


        self.verticalLayout_3.addWidget(self.topFrame)

        self.middleFrame = QFrame(self.leftMenuSubContainer)
        self.middleFrame.setObjectName(u"middleFrame")
        self.middleFrame.setMinimumSize(QSize(0, 120))
        self.middleFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.middleFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_5 = QVBoxLayout(self.middleFrame)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.homePushButton = QPushButton(self.middleFrame)
        self.homePushButton.setObjectName(u"homePushButton")
        self.homePushButton.setMinimumSize(QSize(0, 34))
        font = QFont()
        font.setPointSize(12)
        self.homePushButton.setFont(font)
        self.homePushButton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.homePushButton.setStyleSheet(u"background-color: rgb(144, 170, 197);")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/home.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.homePushButton.setIcon(icon1)
        self.homePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.homePushButton)

        self.laserPushButton = QPushButton(self.middleFrame)
        self.laserPushButton.setObjectName(u"laserPushButton")
        self.laserPushButton.setMinimumSize(QSize(0, 34))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.laserPushButton.setFont(font1)
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons/loader.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.laserPushButton.setIcon(icon2)
        self.laserPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.laserPushButton)

        self.programsPushButton = QPushButton(self.middleFrame)
        self.programsPushButton.setObjectName(u"programsPushButton")
        self.programsPushButton.setMinimumSize(QSize(0, 34))
        self.programsPushButton.setFont(font)
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons/list.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.programsPushButton.setIcon(icon3)
        self.programsPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.programsPushButton)

        self.recipePushButton = QPushButton(self.middleFrame)
        self.recipePushButton.setObjectName(u"recipePushButton")
        self.recipePushButton.setMinimumSize(QSize(0, 34))
        self.recipePushButton.setFont(font)
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons/book-open.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.recipePushButton.setIcon(icon4)
        self.recipePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.recipePushButton)

        self.printPushButton = QPushButton(self.middleFrame)
        self.printPushButton.setObjectName(u"printPushButton")
        self.printPushButton.setMinimumSize(QSize(0, 34))
        self.printPushButton.setFont(font)
        icon5 = QIcon()
        icon5.addFile(u":/icons/icons/printer.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.printPushButton.setIcon(icon5)
        self.printPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.printPushButton)

        self.cameraPushButton = QPushButton(self.middleFrame)
        self.cameraPushButton.setObjectName(u"cameraPushButton")
        self.cameraPushButton.setMinimumSize(QSize(0, 34))
        self.cameraPushButton.setFont(font)
        icon6 = QIcon()
        icon6.addFile(u":/icons/icons/camera.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cameraPushButton.setIcon(icon6)
        self.cameraPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.cameraPushButton)

        self.cameraonoffoffsetPushButton = QPushButton(self.middleFrame)
        self.cameraonoffoffsetPushButton.setObjectName(u"cameraonoffoffsetPushButton")
        self.cameraonoffoffsetPushButton.setMinimumSize(QSize(0, 34))
        self.cameraonoffoffsetPushButton.setFont(font)
        icon7 = QIcon()
        icon7.addFile(u":/icons/icons/eye.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cameraonoffoffsetPushButton.setIcon(icon7)
        self.cameraonoffoffsetPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.cameraonoffoffsetPushButton)

        self.terminalPushButton = QPushButton(self.middleFrame)
        self.terminalPushButton.setObjectName(u"terminalPushButton")
        self.terminalPushButton.setMinimumSize(QSize(0, 34))
        self.terminalPushButton.setFont(font)
        icon8 = QIcon()
        icon8.addFile(u":/icons/icons/monitor.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.terminalPushButton.setIcon(icon8)
        self.terminalPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_5.addWidget(self.terminalPushButton)


        self.verticalLayout_3.addWidget(self.middleFrame)

        self.verticalSpacer = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.bottomFrame = QFrame(self.leftMenuSubContainer)
        self.bottomFrame.setObjectName(u"bottomFrame")
        self.bottomFrame.setMinimumSize(QSize(0, 120))
        self.bottomFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.bottomFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_4 = QVBoxLayout(self.bottomFrame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.comPushButton = QPushButton(self.bottomFrame)
        self.comPushButton.setObjectName(u"comPushButton")
        self.comPushButton.setMinimumSize(QSize(0, 34))
        self.comPushButton.setFont(font)
        icon9 = QIcon()
        icon9.addFile(u":/icons/icons/link.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.comPushButton.setIcon(icon9)
        self.comPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.comPushButton)

        self.settingsPushButton = QPushButton(self.bottomFrame)
        self.settingsPushButton.setObjectName(u"settingsPushButton")
        self.settingsPushButton.setMinimumSize(QSize(0, 34))
        self.settingsPushButton.setFont(font)
        icon10 = QIcon()
        icon10.addFile(u":/icons/icons/settings.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settingsPushButton.setIcon(icon10)
        self.settingsPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.settingsPushButton)

        self.infoPushButton = QPushButton(self.bottomFrame)
        self.infoPushButton.setObjectName(u"infoPushButton")
        self.infoPushButton.setMinimumSize(QSize(0, 34))
        self.infoPushButton.setFont(font)
        icon11 = QIcon()
        icon11.addFile(u":/icons/icons/info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.infoPushButton.setIcon(icon11)
        self.infoPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.infoPushButton)


        self.verticalLayout_3.addWidget(self.bottomFrame)


        self.verticalLayout.addWidget(self.leftMenuSubContainer)


        self.horizontalLayout.addWidget(self.leftMenuContainer)

        self.centerSlideMenu = QCustomSlideMenu(self.centralwidget)
        self.centerSlideMenu.setObjectName(u"centerSlideMenu")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centerSlideMenu.sizePolicy().hasHeightForWidth())
        self.centerSlideMenu.setSizePolicy(sizePolicy1)
        self.centerSlideMenu.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout_6 = QVBoxLayout(self.centerSlideMenu)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.centerMenuSubContainer = QWidget(self.centerSlideMenu)
        self.centerMenuSubContainer.setObjectName(u"centerMenuSubContainer")
        self.centerMenuSubContainer.setMinimumSize(QSize(0, 0))
        self.verticalLayout_18 = QVBoxLayout(self.centerMenuSubContainer)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.centerMenuFrame = QFrame(self.centerMenuSubContainer)
        self.centerMenuFrame.setObjectName(u"centerMenuFrame")
        self.centerMenuFrame.setMinimumSize(QSize(0, 50))
        self.centerMenuFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.centerMenuFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_2 = QHBoxLayout(self.centerMenuFrame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.centerMenuLabel = QLabel(self.centerMenuFrame)
        self.centerMenuLabel.setObjectName(u"centerMenuLabel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.centerMenuLabel.sizePolicy().hasHeightForWidth())
        self.centerMenuLabel.setSizePolicy(sizePolicy2)
        font2 = QFont()
        font2.setPointSize(14)
        font2.setBold(True)
        self.centerMenuLabel.setFont(font2)
        self.centerMenuLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.centerMenuLabel)

        self.closeCenterMenuPushButton = QPushButton(self.centerMenuFrame)
        self.closeCenterMenuPushButton.setObjectName(u"closeCenterMenuPushButton")
        self.closeCenterMenuPushButton.setMinimumSize(QSize(0, 30))
        icon12 = QIcon()
        icon12.addFile(u":/icons/icons/x-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeCenterMenuPushButton.setIcon(icon12)
        self.closeCenterMenuPushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.closeCenterMenuPushButton, 0, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout_18.addWidget(self.centerMenuFrame)

        self.centerMenuPages = QCustomStackedWidget(self.centerMenuSubContainer)
        self.centerMenuPages.setObjectName(u"centerMenuPages")
        font3 = QFont()
        font3.setFamilies([u"Alef"])
        font3.setPointSize(9)
        font3.setBold(False)
        self.centerMenuPages.setFont(font3)
        self.comPage = QWidget()
        self.comPage.setObjectName(u"comPage")
        self.comPage.setStyleSheet(u"color: rgb(16, 42, 131);")
        self.verticalLayout_20 = QVBoxLayout(self.comPage)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.comLabel = QLabel(self.comPage)
        self.comLabel.setObjectName(u"comLabel")
        font4 = QFont()
        font4.setPointSize(16)
        font4.setBold(True)
        self.comLabel.setFont(font4)
        self.comLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_20.addWidget(self.comLabel)

        self.comFrame = QFrame(self.comPage)
        self.comFrame.setObjectName(u"comFrame")
        self.comFrame.setMinimumSize(QSize(0, 250))
        self.comFrame.setSizeIncrement(QSize(0, 250))
        self.comFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.comFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_19 = QVBoxLayout(self.comFrame)
        self.verticalLayout_19.setSpacing(5)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(5, 5, 5, 5)
        self.portFrame = QFrame(self.comFrame)
        self.portFrame.setObjectName(u"portFrame")
        self.portFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.portFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.portFrame)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.portLabel = QLabel(self.portFrame)
        self.portLabel.setObjectName(u"portLabel")
        self.portLabel.setMinimumSize(QSize(0, 30))
        font5 = QFont()
        font5.setPointSize(12)
        font5.setBold(True)
        self.portLabel.setFont(font5)

        self.horizontalLayout_12.addWidget(self.portLabel)

        self.mainportComboBox = QComboBox(self.portFrame)
        self.mainportComboBox.setObjectName(u"mainportComboBox")
        self.mainportComboBox.setMinimumSize(QSize(0, 30))
        self.mainportComboBox.setFont(font)
        self.mainportComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_12.addWidget(self.mainportComboBox)

        self.horizontalLayout_12.setStretch(0, 1)
        self.horizontalLayout_12.setStretch(1, 2)

        self.verticalLayout_19.addWidget(self.portFrame)

        self.baudFrame = QFrame(self.comFrame)
        self.baudFrame.setObjectName(u"baudFrame")
        self.baudFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.baudFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_13 = QHBoxLayout(self.baudFrame)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.baudLabel = QLabel(self.baudFrame)
        self.baudLabel.setObjectName(u"baudLabel")
        self.baudLabel.setMinimumSize(QSize(0, 30))
        self.baudLabel.setFont(font5)

        self.horizontalLayout_13.addWidget(self.baudLabel)

        self.mainbaudComboBox = QComboBox(self.baudFrame)
        self.mainbaudComboBox.setObjectName(u"mainbaudComboBox")
        self.mainbaudComboBox.setMinimumSize(QSize(0, 30))
        self.mainbaudComboBox.setFont(font)
        self.mainbaudComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_13.addWidget(self.mainbaudComboBox)

        self.horizontalLayout_13.setStretch(0, 1)
        self.horizontalLayout_13.setStretch(1, 2)

        self.verticalLayout_19.addWidget(self.baudFrame)

        self.mainconnectPushButton = QPushButton(self.comFrame)
        self.mainconnectPushButton.setObjectName(u"mainconnectPushButton")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.mainconnectPushButton.sizePolicy().hasHeightForWidth())
        self.mainconnectPushButton.setSizePolicy(sizePolicy3)
        self.mainconnectPushButton.setMinimumSize(QSize(0, 40))
        self.mainconnectPushButton.setMaximumSize(QSize(16777215, 60))
        self.mainconnectPushButton.setFont(font2)
        self.mainconnectPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_19.addWidget(self.mainconnectPushButton)

        self.mainrefreshPushButton = QPushButton(self.comFrame)
        self.mainrefreshPushButton.setObjectName(u"mainrefreshPushButton")
        sizePolicy3.setHeightForWidth(self.mainrefreshPushButton.sizePolicy().hasHeightForWidth())
        self.mainrefreshPushButton.setSizePolicy(sizePolicy3)
        self.mainrefreshPushButton.setMinimumSize(QSize(0, 40))
        self.mainrefreshPushButton.setMaximumSize(QSize(16777215, 60))
        self.mainrefreshPushButton.setFont(font2)
        self.mainrefreshPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_19.addWidget(self.mainrefreshPushButton)


        self.verticalLayout_20.addWidget(self.comFrame)

        self.verticalSpacer_8 = QSpacerItem(20, 51, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_20.addItem(self.verticalSpacer_8)

        self.centerMenuPages.addWidget(self.comPage)
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        self.verticalLayout_51 = QVBoxLayout(self.settingsPage)
        self.verticalLayout_51.setObjectName(u"verticalLayout_51")
        self.settingsLabel = QLabel(self.settingsPage)
        self.settingsLabel.setObjectName(u"settingsLabel")
        font6 = QFont()
        font6.setFamilies([u"Segoe UI"])
        font6.setPointSize(16)
        font6.setBold(True)
        self.settingsLabel.setFont(font6)
        self.settingsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_51.addWidget(self.settingsLabel)

        self.setFrame = QFrame(self.settingsPage)
        self.setFrame.setObjectName(u"setFrame")
        self.setFrame.setSizeIncrement(QSize(0, 250))
        self.setFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_50 = QVBoxLayout(self.setFrame)
        self.verticalLayout_50.setSpacing(5)
        self.verticalLayout_50.setObjectName(u"verticalLayout_50")
        self.verticalLayout_50.setContentsMargins(5, 5, 5, 5)
        self.widget = QWidget(self.setFrame)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_45 = QVBoxLayout(self.widget)
        self.verticalLayout_45.setSpacing(0)
        self.verticalLayout_45.setObjectName(u"verticalLayout_45")
        self.verticalLayout_45.setContentsMargins(0, 0, 0, 0)
        self.indexFrame = QFrame(self.widget)
        self.indexFrame.setObjectName(u"indexFrame")
        self.verticalLayout_26 = QVBoxLayout(self.indexFrame)
        self.verticalLayout_26.setSpacing(5)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(15, 5, 5, 5)
        self.indexLabel = QLabel(self.indexFrame)
        self.indexLabel.setObjectName(u"indexLabel")
        self.indexLabel.setFont(font5)
        self.indexLabel.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_26.addWidget(self.indexLabel)

        self.indexLineEdit = QLineEdit(self.indexFrame)
        self.indexLineEdit.setObjectName(u"indexLineEdit")
        sizePolicy2.setHeightForWidth(self.indexLineEdit.sizePolicy().hasHeightForWidth())
        self.indexLineEdit.setSizePolicy(sizePolicy2)
        self.indexLineEdit.setMinimumSize(QSize(0, 30))
        self.indexLineEdit.setMaximumSize(QSize(120, 16777215))
        self.indexLineEdit.setFont(font5)
        self.indexLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.indexLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_26.addWidget(self.indexLineEdit)


        self.verticalLayout_45.addWidget(self.indexFrame)

        self.machinesetFrame = QFrame(self.widget)
        self.machinesetFrame.setObjectName(u"machinesetFrame")
        self.verticalLayout_35 = QVBoxLayout(self.machinesetFrame)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.feedLabel_2 = QLabel(self.machinesetFrame)
        self.feedLabel_2.setObjectName(u"feedLabel_2")
        self.feedLabel_2.setFont(font5)
        self.feedLabel_2.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_35.addWidget(self.feedLabel_2)

        self.cameraoffsetPushButton = QPushButton(self.machinesetFrame)
        self.cameraoffsetPushButton.setObjectName(u"cameraoffsetPushButton")
        self.cameraoffsetPushButton.setFont(font5)
        self.cameraoffsetPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_35.addWidget(self.cameraoffsetPushButton)


        self.verticalLayout_45.addWidget(self.machinesetFrame)


        self.verticalLayout_50.addWidget(self.widget)


        self.verticalLayout_51.addWidget(self.setFrame)

        self.verticalSpacer_5 = QSpacerItem(20, 9, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_51.addItem(self.verticalSpacer_5)

        self.centerMenuPages.addWidget(self.settingsPage)
        self.infoPage = QWidget()
        self.infoPage.setObjectName(u"infoPage")
        self.verticalLayout_10 = QVBoxLayout(self.infoPage)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.infoLabel = QLabel(self.infoPage)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setFont(font4)
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_10.addWidget(self.infoLabel)

        self.infoSubFrame = QFrame(self.infoPage)
        self.infoSubFrame.setObjectName(u"infoSubFrame")
        self.infoSubFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.infoSubFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_34 = QHBoxLayout(self.infoSubFrame)
        self.horizontalLayout_34.setSpacing(5)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.horizontalLayout_34.setContentsMargins(5, 5, 5, 5)
        self.infoSubPages = QStackedWidget(self.infoSubFrame)
        self.infoSubPages.setObjectName(u"infoSubPages")
        self.infoSubPages.setMinimumSize(QSize(0, 250))
        self.infoSubPages.setSizeIncrement(QSize(0, 250))
        self.optionPage = QWidget()
        self.optionPage.setObjectName(u"optionPage")
        self.optionPage.setMinimumSize(QSize(0, 0))
        self.optionPage.setMaximumSize(QSize(16777215, 150))
        self.verticalLayout_9 = QVBoxLayout(self.optionPage)
        self.verticalLayout_9.setSpacing(5)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(5, 5, 5, 5)
        self.aboutPushButton = QPushButton(self.optionPage)
        self.aboutPushButton.setObjectName(u"aboutPushButton")
        sizePolicy3.setHeightForWidth(self.aboutPushButton.sizePolicy().hasHeightForWidth())
        self.aboutPushButton.setSizePolicy(sizePolicy3)
        self.aboutPushButton.setMinimumSize(QSize(0, 30))
        self.aboutPushButton.setMaximumSize(QSize(16777215, 60))
        self.aboutPushButton.setFont(font2)
        self.aboutPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.aboutPushButton.setIcon(icon11)
        self.aboutPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_9.addWidget(self.aboutPushButton)

        self.helpPushButton = QPushButton(self.optionPage)
        self.helpPushButton.setObjectName(u"helpPushButton")
        sizePolicy3.setHeightForWidth(self.helpPushButton.sizePolicy().hasHeightForWidth())
        self.helpPushButton.setSizePolicy(sizePolicy3)
        self.helpPushButton.setMinimumSize(QSize(0, 30))
        self.helpPushButton.setMaximumSize(QSize(16777215, 60))
        self.helpPushButton.setFont(font2)
        self.helpPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        icon13 = QIcon()
        icon13.addFile(u":/icons/icons/help-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.helpPushButton.setIcon(icon13)
        self.helpPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_9.addWidget(self.helpPushButton)

        self.infoSubPages.addWidget(self.optionPage)
        self.aboutPage = QWidget()
        self.aboutPage.setObjectName(u"aboutPage")
        self.horizontalLayout_38 = QHBoxLayout(self.aboutPage)
        self.horizontalLayout_38.setSpacing(5)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.horizontalLayout_38.setContentsMargins(5, 5, 5, 5)
        self.frame_9 = QFrame(self.aboutPage)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_44 = QVBoxLayout(self.frame_9)
        self.verticalLayout_44.setSpacing(0)
        self.verticalLayout_44.setObjectName(u"verticalLayout_44")
        self.verticalLayout_44.setContentsMargins(0, 0, 0, 0)
        self.label_20 = QLabel(self.frame_9)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setFont(font2)
        self.label_20.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    border: none;\n"
"}")
        self.label_20.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_44.addWidget(self.label_20)

        self.verticalSpacer_4 = QSpacerItem(20, 142, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_44.addItem(self.verticalSpacer_4)

        self.back1PushButton = QPushButton(self.frame_9)
        self.back1PushButton.setObjectName(u"back1PushButton")
        self.back1PushButton.setFont(font)
        self.back1PushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        icon14 = QIcon()
        icon14.addFile(u":/icons/icons/arrow-left.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.back1PushButton.setIcon(icon14)
        self.back1PushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_44.addWidget(self.back1PushButton)


        self.horizontalLayout_38.addWidget(self.frame_9)

        self.infoSubPages.addWidget(self.aboutPage)
        self.helpPage = QWidget()
        self.helpPage.setObjectName(u"helpPage")
        self.horizontalLayout_33 = QHBoxLayout(self.helpPage)
        self.horizontalLayout_33.setSpacing(5)
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.horizontalLayout_33.setContentsMargins(5, 5, 5, 5)
        self.frame_12 = QFrame(self.helpPage)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_43 = QVBoxLayout(self.frame_12)
        self.verticalLayout_43.setSpacing(0)
        self.verticalLayout_43.setObjectName(u"verticalLayout_43")
        self.verticalLayout_43.setContentsMargins(0, 0, 0, 0)
        self.label_21 = QLabel(self.frame_12)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setFont(font2)
        self.label_21.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    border: none;\n"
"}")
        self.label_21.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_43.addWidget(self.label_21)

        self.verticalSpacer_2 = QSpacerItem(20, 142, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_43.addItem(self.verticalSpacer_2)

        self.back2PushButton = QPushButton(self.frame_12)
        self.back2PushButton.setObjectName(u"back2PushButton")
        self.back2PushButton.setFont(font)
        self.back2PushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.back2PushButton.setIcon(icon14)
        self.back2PushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_43.addWidget(self.back2PushButton)


        self.horizontalLayout_33.addWidget(self.frame_12)

        self.infoSubPages.addWidget(self.helpPage)

        self.horizontalLayout_34.addWidget(self.infoSubPages)


        self.verticalLayout_10.addWidget(self.infoSubFrame)

        self.verticalSpacer_3 = QSpacerItem(20, 307, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_3)

        self.centerMenuPages.addWidget(self.infoPage)
        self.profilePage = QWidget()
        self.profilePage.setObjectName(u"profilePage")
        self.verticalLayout_54 = QVBoxLayout(self.profilePage)
        self.verticalLayout_54.setObjectName(u"verticalLayout_54")
        self.profileLabel = QLabel(self.profilePage)
        self.profileLabel.setObjectName(u"profileLabel")
        self.profileLabel.setFont(font4)
        self.profileLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_54.addWidget(self.profileLabel)

        self.profilesubFrame = QFrame(self.profilePage)
        self.profilesubFrame.setObjectName(u"profilesubFrame")
        self.profilesubFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.profilesubFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_53 = QVBoxLayout(self.profilesubFrame)
        self.verticalLayout_53.setSpacing(5)
        self.verticalLayout_53.setObjectName(u"verticalLayout_53")
        self.verticalLayout_53.setContentsMargins(5, 5, 5, 5)
        self.userFrame = QFrame(self.profilesubFrame)
        self.userFrame.setObjectName(u"userFrame")
        self.userFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.userFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_33 = QVBoxLayout(self.userFrame)
        self.verticalLayout_33.setSpacing(5)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.verticalLayout_33.setContentsMargins(5, 5, 5, 5)
        self.userLabel = QLabel(self.userFrame)
        self.userLabel.setObjectName(u"userLabel")
        self.userLabel.setFont(font5)
        self.userLabel.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.userLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_33.addWidget(self.userLabel)

        self.userComboBox = QComboBox(self.userFrame)
        self.userComboBox.setObjectName(u"userComboBox")
        self.userComboBox.setFont(font5)
        self.userComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"	color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_33.addWidget(self.userComboBox)


        self.verticalLayout_53.addWidget(self.userFrame)

        self.passwordFrame = QFrame(self.profilesubFrame)
        self.passwordFrame.setObjectName(u"passwordFrame")
        self.passwordFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.passwordFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_52 = QVBoxLayout(self.passwordFrame)
        self.verticalLayout_52.setSpacing(5)
        self.verticalLayout_52.setObjectName(u"verticalLayout_52")
        self.verticalLayout_52.setContentsMargins(5, 5, 5, 5)
        self.passwordLabel = QLabel(self.passwordFrame)
        self.passwordLabel.setObjectName(u"passwordLabel")
        self.passwordLabel.setFont(font5)
        self.passwordLabel.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.passwordLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_52.addWidget(self.passwordLabel)

        self.passwordLineEdit = QLineEdit(self.passwordFrame)
        self.passwordLineEdit.setObjectName(u"passwordLineEdit")
        self.passwordLineEdit.setFont(font)
        self.passwordLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_52.addWidget(self.passwordLineEdit)


        self.verticalLayout_53.addWidget(self.passwordFrame)

        self.profilesetPushButton = QPushButton(self.profilesubFrame)
        self.profilesetPushButton.setObjectName(u"profilesetPushButton")
        self.profilesetPushButton.setMinimumSize(QSize(0, 40))
        self.profilesetPushButton.setFont(font2)
        self.profilesetPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_53.addWidget(self.profilesetPushButton)


        self.verticalLayout_54.addWidget(self.profilesubFrame)

        self.verticalSpacer_6 = QSpacerItem(20, 82, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_54.addItem(self.verticalSpacer_6)

        self.centerMenuPages.addWidget(self.profilePage)

        self.verticalLayout_18.addWidget(self.centerMenuPages)

        self.logoLabel = QLabel(self.centerMenuSubContainer)
        self.logoLabel.setObjectName(u"logoLabel")
        sizePolicy3.setHeightForWidth(self.logoLabel.sizePolicy().hasHeightForWidth())
        self.logoLabel.setSizePolicy(sizePolicy3)
        self.logoLabel.setPixmap(QPixmap(u":/logo/logo/SPPL-logo-sq.png"))
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_18.addWidget(self.logoLabel)


        self.verticalLayout_6.addWidget(self.centerMenuSubContainer)


        self.horizontalLayout.addWidget(self.centerSlideMenu)

        self.mainBodyContainer = QWidget(self.centralwidget)
        self.mainBodyContainer.setObjectName(u"mainBodyContainer")
        self.verticalLayout_11 = QVBoxLayout(self.mainBodyContainer)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.headerContainer = QWidget(self.mainBodyContainer)
        self.headerContainer.setObjectName(u"headerContainer")
        self.headerContainer.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_6 = QHBoxLayout(self.headerContainer)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, -1, 0, -1)
        self.profileFrame = QFrame(self.headerContainer)
        self.profileFrame.setObjectName(u"profileFrame")
        self.profileFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.profileFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_29 = QHBoxLayout(self.profileFrame)
        self.horizontalLayout_29.setSpacing(0)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.profilePushButton = QPushButton(self.profileFrame)
        self.profilePushButton.setObjectName(u"profilePushButton")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.profilePushButton.sizePolicy().hasHeightForWidth())
        self.profilePushButton.setSizePolicy(sizePolicy4)
        self.profilePushButton.setMinimumSize(QSize(0, 22))
        icon15 = QIcon()
        icon15.addFile(u":/icons/icons/user.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.profilePushButton.setIcon(icon15)
        self.profilePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_29.addWidget(self.profilePushButton)


        self.horizontalLayout_6.addWidget(self.profileFrame)

        self.titleFrame = QFrame(self.headerContainer)
        self.titleFrame.setObjectName(u"titleFrame")
        sizePolicy2.setHeightForWidth(self.titleFrame.sizePolicy().hasHeightForWidth())
        self.titleFrame.setSizePolicy(sizePolicy2)
        self.titleFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.titleFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_8 = QHBoxLayout(self.titleFrame)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(5, 3, 5, 3)
        self.titleLabel = QLabel(self.titleFrame)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setFont(font4)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_8.addWidget(self.titleLabel)


        self.horizontalLayout_6.addWidget(self.titleFrame)

        self.notifyFrame = QFrame(self.headerContainer)
        self.notifyFrame.setObjectName(u"notifyFrame")
        self.notifyFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.notifyFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_9 = QHBoxLayout(self.notifyFrame)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 10, 0)

        self.horizontalLayout_6.addWidget(self.notifyFrame)

        self.windowFrame = QFrame(self.headerContainer)
        self.windowFrame.setObjectName(u"windowFrame")
        self.windowFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.windowFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_7 = QHBoxLayout(self.windowFrame)
        self.horizontalLayout_7.setSpacing(6)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(5, 0, 5, 0)
        self.notifyPushButton = QPushButton(self.windowFrame)
        self.notifyPushButton.setObjectName(u"notifyPushButton")
        icon16 = QIcon()
        icon16.addFile(u":/icons/icons/bell.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.notifyPushButton.setIcon(icon16)
        self.notifyPushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.notifyPushButton)

        self.minimizePushButton = QPushButton(self.windowFrame)
        self.minimizePushButton.setObjectName(u"minimizePushButton")
        icon17 = QIcon()
        icon17.addFile(u":/icons/icons/minus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizePushButton.setIcon(icon17)
        self.minimizePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.minimizePushButton)

        self.restorePushButton = QPushButton(self.windowFrame)
        self.restorePushButton.setObjectName(u"restorePushButton")
        icon18 = QIcon()
        icon18.addFile(u":/icons/icons/square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.restorePushButton.setIcon(icon18)
        self.restorePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.restorePushButton)

        self.closePushButton = QPushButton(self.windowFrame)
        self.closePushButton.setObjectName(u"closePushButton")
        icon19 = QIcon()
        icon19.addFile(u":/icons/icons/x.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closePushButton.setIcon(icon19)
        self.closePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.closePushButton)


        self.horizontalLayout_6.addWidget(self.windowFrame)

        self.horizontalLayout_6.setStretch(1, 6)

        self.verticalLayout_11.addWidget(self.headerContainer)

        self.mainBodyContent = QWidget(self.mainBodyContainer)
        self.mainBodyContent.setObjectName(u"mainBodyContent")
        self.horizontalLayout_10 = QHBoxLayout(self.mainBodyContent)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.mainContentContainer = QWidget(self.mainBodyContent)
        self.mainContentContainer.setObjectName(u"mainContentContainer")
        self.horizontalLayout_11 = QHBoxLayout(self.mainContentContainer)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.mainPages = QCustomStackedWidget(self.mainContentContainer)
        self.mainPages.setObjectName(u"mainPages")
        self.mainPages.setMinimumSize(QSize(0, 30))
        self.jogPage = QWidget()
        self.jogPage.setObjectName(u"jogPage")
        self.verticalLayout_15 = QVBoxLayout(self.jogPage)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.page1Label = QLabel(self.jogPage)
        self.page1Label.setObjectName(u"page1Label")
        self.page1Label.setMinimumSize(QSize(0, 20))
        self.page1Label.setMaximumSize(QSize(16777215, 20))
        self.page1Label.setFont(font2)
        self.page1Label.setFrameShadow(QFrame.Shadow.Raised)
        self.page1Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_15.addWidget(self.page1Label)

        self.jogFrame = QFrame(self.jogPage)
        self.jogFrame.setObjectName(u"jogFrame")
        self.jogFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.jogFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_17 = QVBoxLayout(self.jogFrame)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.axisposFrame = QFrame(self.jogFrame)
        self.axisposFrame.setObjectName(u"axisposFrame")
        self.axisposFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.axisposFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_14 = QHBoxLayout(self.axisposFrame)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.xposLCDNumber = QLCDNumber(self.axisposFrame)
        self.xposLCDNumber.setObjectName(u"xposLCDNumber")
        font7 = QFont()
        font7.setPointSize(14)
        self.xposLCDNumber.setFont(font7)
        self.xposLCDNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.xposLCDNumber.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_14.addWidget(self.xposLCDNumber)

        self.yposLCDNumber = QLCDNumber(self.axisposFrame)
        self.yposLCDNumber.setObjectName(u"yposLCDNumber")
        self.yposLCDNumber.setFont(font7)
        self.yposLCDNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.yposLCDNumber.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_14.addWidget(self.yposLCDNumber)

        self.zposLCDNumber = QLCDNumber(self.axisposFrame)
        self.zposLCDNumber.setObjectName(u"zposLCDNumber")
        self.zposLCDNumber.setFont(font7)
        self.zposLCDNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.zposLCDNumber.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_14.addWidget(self.zposLCDNumber)


        self.verticalLayout_17.addWidget(self.axisposFrame)

        self.jogbtnFrame = QFrame(self.jogFrame)
        self.jogbtnFrame.setObjectName(u"jogbtnFrame")
        self.jogbtnFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.jogbtnFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.jogbtnFrame)
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.homeFrame = QFrame(self.jogbtnFrame)
        self.homeFrame.setObjectName(u"homeFrame")
        self.homeFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.homeFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_22 = QVBoxLayout(self.homeFrame)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(-1, 4, -1, -1)
        self.homeLabel = QLabel(self.homeFrame)
        self.homeLabel.setObjectName(u"homeLabel")
        self.homeLabel.setMinimumSize(QSize(0, 20))
        self.homeLabel.setMaximumSize(QSize(16777215, 20))
        self.homeLabel.setFont(font5)
        self.homeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_22.addWidget(self.homeLabel)

        self.xhomePushButton = QPushButton(self.homeFrame)
        self.xhomePushButton.setObjectName(u"xhomePushButton")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.xhomePushButton.sizePolicy().hasHeightForWidth())
        self.xhomePushButton.setSizePolicy(sizePolicy5)
        self.xhomePushButton.setMinimumSize(QSize(0, 0))
        self.xhomePushButton.setFont(font2)
        self.xhomePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.xhomePushButton.setIcon(icon1)
        self.xhomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_22.addWidget(self.xhomePushButton)

        self.yhomePushButton = QPushButton(self.homeFrame)
        self.yhomePushButton.setObjectName(u"yhomePushButton")
        sizePolicy5.setHeightForWidth(self.yhomePushButton.sizePolicy().hasHeightForWidth())
        self.yhomePushButton.setSizePolicy(sizePolicy5)
        self.yhomePushButton.setMinimumSize(QSize(0, 0))
        self.yhomePushButton.setFont(font2)
        self.yhomePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.yhomePushButton.setIcon(icon1)
        self.yhomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_22.addWidget(self.yhomePushButton)

        self.zhomePushButton = QPushButton(self.homeFrame)
        self.zhomePushButton.setObjectName(u"zhomePushButton")
        sizePolicy5.setHeightForWidth(self.zhomePushButton.sizePolicy().hasHeightForWidth())
        self.zhomePushButton.setSizePolicy(sizePolicy5)
        self.zhomePushButton.setMinimumSize(QSize(0, 0))
        self.zhomePushButton.setFont(font2)
        self.zhomePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.zhomePushButton.setIcon(icon1)
        self.zhomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_22.addWidget(self.zhomePushButton)

        self.allhomePushButton = QPushButton(self.homeFrame)
        self.allhomePushButton.setObjectName(u"allhomePushButton")
        sizePolicy5.setHeightForWidth(self.allhomePushButton.sizePolicy().hasHeightForWidth())
        self.allhomePushButton.setSizePolicy(sizePolicy5)
        self.allhomePushButton.setMinimumSize(QSize(0, 0))
        self.allhomePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.allhomePushButton.setIcon(icon1)
        self.allhomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_22.addWidget(self.allhomePushButton)


        self.horizontalLayout_15.addWidget(self.homeFrame)

        self.jogSubFrame = QFrame(self.jogbtnFrame)
        self.jogSubFrame.setObjectName(u"jogSubFrame")
        self.jogSubFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.jogSubFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_21 = QVBoxLayout(self.jogSubFrame)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(9, 0, 0, 0)
        self.stepsFrame = QFrame(self.jogSubFrame)
        self.stepsFrame.setObjectName(u"stepsFrame")
        self.stepsFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.stepsFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_25 = QVBoxLayout(self.stepsFrame)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(-1, 4, -1, -1)
        self.label_3 = QLabel(self.stepsFrame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 15))
        self.label_3.setFont(font5)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_25.addWidget(self.label_3, 0, Qt.AlignmentFlag.AlignTop)

        self.frame_7 = QFrame(self.stepsFrame)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy6)
        self.frame_7.setMinimumSize(QSize(0, 35))
        self.frame_7.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.travel100_RadioButton = QRadioButton(self.frame_7)
        self.travel100_RadioButton.setObjectName(u"travel100_RadioButton")
        self.travel100_RadioButton.setFont(font2)

        self.horizontalLayout_20.addWidget(self.travel100_RadioButton)

        self.travel50_RadioButton = QRadioButton(self.frame_7)
        self.travel50_RadioButton.setObjectName(u"travel50_RadioButton")
        self.travel50_RadioButton.setFont(font2)

        self.horizontalLayout_20.addWidget(self.travel50_RadioButton)

        self.travel10_RadioButton = QRadioButton(self.frame_7)
        self.travel10_RadioButton.setObjectName(u"travel10_RadioButton")
        self.travel10_RadioButton.setFont(font2)

        self.horizontalLayout_20.addWidget(self.travel10_RadioButton)

        self.travel1_RadioButton = QRadioButton(self.frame_7)
        self.travel1_RadioButton.setObjectName(u"travel1_RadioButton")
        self.travel1_RadioButton.setFont(font2)

        self.horizontalLayout_20.addWidget(self.travel1_RadioButton)


        self.verticalLayout_25.addWidget(self.frame_7)


        self.verticalLayout_21.addWidget(self.stepsFrame)

        self.xyzFrame = QFrame(self.jogSubFrame)
        self.xyzFrame.setObjectName(u"xyzFrame")
        self.xyzFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.xyzFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_16 = QHBoxLayout(self.xyzFrame)
        self.horizontalLayout_16.setSpacing(9)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.xyFrame = QFrame(self.xyzFrame)
        self.xyFrame.setObjectName(u"xyFrame")
        self.xyFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.xyFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_24 = QVBoxLayout(self.xyFrame)
        self.verticalLayout_24.setSpacing(5)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(5, 2, 5, 5)
        self.frame_4 = QFrame(self.xyFrame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(0, 30))
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_17.setSpacing(0)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.frame_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 0))
        self.label_2.setMaximumSize(QSize(16777215, 20))
        self.label_2.setFont(font5)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_17.addWidget(self.label_2)


        self.verticalLayout_24.addWidget(self.frame_4)

        self.frame_5 = QFrame(self.xyFrame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(0, 0))
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_18.setSpacing(5)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(79, 19, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer)

        self.yplusPushButton = QPushButton(self.frame_5)
        self.yplusPushButton.setObjectName(u"yplusPushButton")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.yplusPushButton.sizePolicy().hasHeightForWidth())
        self.yplusPushButton.setSizePolicy(sizePolicy7)
        self.yplusPushButton.setMinimumSize(QSize(0, 0))
        self.yplusPushButton.setFont(font2)
        self.yplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_18.addWidget(self.yplusPushButton)

        self.horizontalSpacer_2 = QSpacerItem(79, 19, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_2)


        self.verticalLayout_24.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.xyFrame)
        self.frame_6.setObjectName(u"frame_6")
        font8 = QFont()
        font8.setPointSize(10)
        self.frame_6.setFont(font8)
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_19.setSpacing(5)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.xminusPushButton = QPushButton(self.frame_6)
        self.xminusPushButton.setObjectName(u"xminusPushButton")
        sizePolicy7.setHeightForWidth(self.xminusPushButton.sizePolicy().hasHeightForWidth())
        self.xminusPushButton.setSizePolicy(sizePolicy7)
        self.xminusPushButton.setMinimumSize(QSize(0, 0))
        self.xminusPushButton.setFont(font2)
        self.xminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_19.addWidget(self.xminusPushButton)

        self.xycenterPushButton = QPushButton(self.frame_6)
        self.xycenterPushButton.setObjectName(u"xycenterPushButton")
        sizePolicy7.setHeightForWidth(self.xycenterPushButton.sizePolicy().hasHeightForWidth())
        self.xycenterPushButton.setSizePolicy(sizePolicy7)
        self.xycenterPushButton.setMinimumSize(QSize(0, 0))
        self.xycenterPushButton.setFont(font2)
        self.xycenterPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_19.addWidget(self.xycenterPushButton)

        self.xplusPushButton = QPushButton(self.frame_6)
        self.xplusPushButton.setObjectName(u"xplusPushButton")
        sizePolicy7.setHeightForWidth(self.xplusPushButton.sizePolicy().hasHeightForWidth())
        self.xplusPushButton.setSizePolicy(sizePolicy7)
        self.xplusPushButton.setMinimumSize(QSize(0, 0))
        self.xplusPushButton.setFont(font2)
        self.xplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_19.addWidget(self.xplusPushButton)


        self.verticalLayout_24.addWidget(self.frame_6)

        self.frame_8 = QFrame(self.xyFrame)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_21 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_21.setSpacing(4)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_3 = QSpacerItem(79, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_3)

        self.yminusPushButton = QPushButton(self.frame_8)
        self.yminusPushButton.setObjectName(u"yminusPushButton")
        sizePolicy7.setHeightForWidth(self.yminusPushButton.sizePolicy().hasHeightForWidth())
        self.yminusPushButton.setSizePolicy(sizePolicy7)
        self.yminusPushButton.setMinimumSize(QSize(0, 0))
        self.yminusPushButton.setFont(font2)
        self.yminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_21.addWidget(self.yminusPushButton)

        self.horizontalSpacer_4 = QSpacerItem(79, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_4)


        self.verticalLayout_24.addWidget(self.frame_8)


        self.horizontalLayout_16.addWidget(self.xyFrame)

        self.zFrame = QFrame(self.xyzFrame)
        self.zFrame.setObjectName(u"zFrame")
        self.zFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.zFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_23 = QVBoxLayout(self.zFrame)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(-1, 5, -1, -1)
        self.label = QLabel(self.zFrame)
        self.label.setObjectName(u"label")
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)
        self.label.setMinimumSize(QSize(0, 20))
        self.label.setMaximumSize(QSize(16777215, 0))
        self.label.setFont(font5)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.label, 0, Qt.AlignmentFlag.AlignTop)

        self.zplusPushButton = QPushButton(self.zFrame)
        self.zplusPushButton.setObjectName(u"zplusPushButton")
        sizePolicy5.setHeightForWidth(self.zplusPushButton.sizePolicy().hasHeightForWidth())
        self.zplusPushButton.setSizePolicy(sizePolicy5)
        self.zplusPushButton.setMinimumSize(QSize(0, 0))
        self.zplusPushButton.setFont(font2)
        self.zplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_23.addWidget(self.zplusPushButton)

        self.zcenterPushButton = QPushButton(self.zFrame)
        self.zcenterPushButton.setObjectName(u"zcenterPushButton")
        sizePolicy5.setHeightForWidth(self.zcenterPushButton.sizePolicy().hasHeightForWidth())
        self.zcenterPushButton.setSizePolicy(sizePolicy5)
        self.zcenterPushButton.setMinimumSize(QSize(0, 0))
        self.zcenterPushButton.setFont(font2)
        self.zcenterPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}\n"
"")

        self.verticalLayout_23.addWidget(self.zcenterPushButton)

        self.zminusPushButton = QPushButton(self.zFrame)
        self.zminusPushButton.setObjectName(u"zminusPushButton")
        sizePolicy5.setHeightForWidth(self.zminusPushButton.sizePolicy().hasHeightForWidth())
        self.zminusPushButton.setSizePolicy(sizePolicy5)
        self.zminusPushButton.setMinimumSize(QSize(0, 0))
        self.zminusPushButton.setFont(font2)
        self.zminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_23.addWidget(self.zminusPushButton)


        self.horizontalLayout_16.addWidget(self.zFrame)

        self.horizontalLayout_16.setStretch(0, 2)
        self.horizontalLayout_16.setStretch(1, 1)

        self.verticalLayout_21.addWidget(self.xyzFrame)

        self.verticalLayout_21.setStretch(0, 1)
        self.verticalLayout_21.setStretch(1, 2)

        self.horizontalLayout_15.addWidget(self.jogSubFrame)

        self.horizontalLayout_15.setStretch(0, 1)
        self.horizontalLayout_15.setStretch(1, 4)

        self.verticalLayout_17.addWidget(self.jogbtnFrame)

        self.verticalLayout_17.setStretch(0, 1)
        self.verticalLayout_17.setStretch(1, 3)

        self.verticalLayout_15.addWidget(self.jogFrame)

        self.mainPages.addWidget(self.jogPage)
        self.laserconfPage = QWidget()
        self.laserconfPage.setObjectName(u"laserconfPage")
        self.verticalLayout_36 = QVBoxLayout(self.laserconfPage)
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.page3Label_3 = QLabel(self.laserconfPage)
        self.page3Label_3.setObjectName(u"page3Label_3")
        self.page3Label_3.setMinimumSize(QSize(0, 30))
        self.page3Label_3.setMaximumSize(QSize(16777215, 30))
        self.page3Label_3.setFont(font2)
        self.page3Label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_36.addWidget(self.page3Label_3)

        self.laserconfFrame = QFrame(self.laserconfPage)
        self.laserconfFrame.setObjectName(u"laserconfFrame")
        self.verticalLayout_37 = QVBoxLayout(self.laserconfFrame)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.verticalLayout_37.setContentsMargins(9, 9, 9, 9)
        self.setfocusFrame = QFrame(self.laserconfFrame)
        self.setfocusFrame.setObjectName(u"setfocusFrame")
        self.setfocusFrame.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")
        self.setfocusFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.setfocusFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_38 = QVBoxLayout(self.setfocusFrame)
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.label_4 = QLabel(self.setfocusFrame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font5)

        self.verticalLayout_38.addWidget(self.label_4)

        self.widget_5 = QWidget(self.setfocusFrame)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_22 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.objheightFrame = QFrame(self.widget_5)
        self.objheightFrame.setObjectName(u"objheightFrame")
        self.objheightFrame.setStyleSheet(u"")
        self.objheightFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.objheightFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_61 = QVBoxLayout(self.objheightFrame)
        self.verticalLayout_61.setObjectName(u"verticalLayout_61")
        self.label_24 = QLabel(self.objheightFrame)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setMinimumSize(QSize(50, 0))
        self.label_24.setMaximumSize(QSize(140, 16777215))
        self.label_24.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")
        self.label_24.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_61.addWidget(self.label_24)

        self.objheightLineEdit = QLineEdit(self.objheightFrame)
        self.objheightLineEdit.setObjectName(u"objheightLineEdit")
        sizePolicy3.setHeightForWidth(self.objheightLineEdit.sizePolicy().hasHeightForWidth())
        self.objheightLineEdit.setSizePolicy(sizePolicy3)
        self.objheightLineEdit.setMinimumSize(QSize(120, 20))
        self.objheightLineEdit.setMaximumSize(QSize(120, 16777215))
        self.objheightLineEdit.setFont(font5)
        self.objheightLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.objheightLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_61.addWidget(self.objheightLineEdit)


        self.horizontalLayout_22.addWidget(self.objheightFrame)

        self.flaserFrame = QFrame(self.widget_5)
        self.flaserFrame.setObjectName(u"flaserFrame")
        self.flaserFrame.setMaximumSize(QSize(230, 16777215))
        self.flaserFrame.setStyleSheet(u"")
        self.flaserFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.flaserFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_39 = QVBoxLayout(self.flaserFrame)
        self.verticalLayout_39.setObjectName(u"verticalLayout_39")
        self.verticalLayout_39.setContentsMargins(0, 0, 0, 0)
        self.widget_6 = QWidget(self.flaserFrame)
        self.widget_6.setObjectName(u"widget_6")
        sizePolicy6.setHeightForWidth(self.widget_6.sizePolicy().hasHeightForWidth())
        self.widget_6.setSizePolicy(sizePolicy6)
        self.widget_6.setMaximumSize(QSize(220, 16777215))
        self.horizontalLayout_25 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_7 = QLabel(self.widget_6)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMaximumSize(QSize(90, 16777215))
        self.label_7.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")

        self.horizontalLayout_25.addWidget(self.label_7)

        self.flaserComboBox = QComboBox(self.widget_6)
        self.flaserComboBox.setObjectName(u"flaserComboBox")
        self.flaserComboBox.setEnabled(True)
        self.flaserComboBox.setFont(font)
        self.flaserComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"	color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_25.addWidget(self.flaserComboBox)

        self.horizontalLayout_25.setStretch(0, 1)
        self.horizontalLayout_25.setStretch(1, 3)

        self.verticalLayout_39.addWidget(self.widget_6)

        self.widget_7 = QWidget(self.flaserFrame)
        self.widget_7.setObjectName(u"widget_7")
        self.widget_7.setMaximumSize(QSize(220, 16777215))
        self.horizontalLayout_36 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.flaserPushButton = QPushButton(self.widget_7)
        self.flaserPushButton.setObjectName(u"flaserPushButton")
        self.flaserPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.flaserPushButton.sizePolicy().hasHeightForWidth())
        self.flaserPushButton.setSizePolicy(sizePolicy6)
        self.flaserPushButton.setMinimumSize(QSize(100, 0))
        self.flaserPushButton.setMaximumSize(QSize(16777215, 150))
        self.flaserPushButton.setFont(font2)
        self.flaserPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_36.addWidget(self.flaserPushButton)


        self.verticalLayout_39.addWidget(self.widget_7)

        self.verticalLayout_39.setStretch(0, 2)
        self.verticalLayout_39.setStretch(1, 1)

        self.horizontalLayout_22.addWidget(self.flaserFrame)

        self.zfocusFrame = QFrame(self.widget_5)
        self.zfocusFrame.setObjectName(u"zfocusFrame")
        self.zfocusFrame.setStyleSheet(u"")
        self.zfocusFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.zfocusFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_40 = QVBoxLayout(self.zfocusFrame)
        self.verticalLayout_40.setSpacing(10)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.fplusPushButton = QPushButton(self.zfocusFrame)
        self.fplusPushButton.setObjectName(u"fplusPushButton")
        sizePolicy6.setHeightForWidth(self.fplusPushButton.sizePolicy().hasHeightForWidth())
        self.fplusPushButton.setSizePolicy(sizePolicy6)
        self.fplusPushButton.setMinimumSize(QSize(100, 0))
        self.fplusPushButton.setMaximumSize(QSize(16777215, 120))
        self.fplusPushButton.setFont(font2)
        self.fplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_40.addWidget(self.fplusPushButton)

        self.fminusPushButton = QPushButton(self.zfocusFrame)
        self.fminusPushButton.setObjectName(u"fminusPushButton")
        sizePolicy6.setHeightForWidth(self.fminusPushButton.sizePolicy().hasHeightForWidth())
        self.fminusPushButton.setSizePolicy(sizePolicy6)
        self.fminusPushButton.setMinimumSize(QSize(100, 0))
        self.fminusPushButton.setMaximumSize(QSize(16777215, 120))
        self.fminusPushButton.setFont(font2)
        self.fminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_40.addWidget(self.fminusPushButton)


        self.horizontalLayout_22.addWidget(self.zfocusFrame)

        self.fsetFrame = QFrame(self.widget_5)
        self.fsetFrame.setObjectName(u"fsetFrame")
        self.fsetFrame.setStyleSheet(u"")
        self.fsetFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.fsetFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_41 = QVBoxLayout(self.fsetFrame)
        self.verticalLayout_41.setObjectName(u"verticalLayout_41")
        self.focusLCDNumber = QLCDNumber(self.fsetFrame)
        self.focusLCDNumber.setObjectName(u"focusLCDNumber")
        sizePolicy6.setHeightForWidth(self.focusLCDNumber.sizePolicy().hasHeightForWidth())
        self.focusLCDNumber.setSizePolicy(sizePolicy6)
        self.focusLCDNumber.setMinimumSize(QSize(100, 0))

        self.verticalLayout_41.addWidget(self.focusLCDNumber)

        self.fsetPushButton = QPushButton(self.fsetFrame)
        self.fsetPushButton.setObjectName(u"fsetPushButton")
        self.fsetPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.fsetPushButton.sizePolicy().hasHeightForWidth())
        self.fsetPushButton.setSizePolicy(sizePolicy6)
        self.fsetPushButton.setMinimumSize(QSize(100, 0))
        self.fsetPushButton.setMaximumSize(QSize(16777215, 150))
        self.fsetPushButton.setFont(font2)
        self.fsetPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_41.addWidget(self.fsetPushButton)

        self.verticalLayout_41.setStretch(0, 2)
        self.verticalLayout_41.setStretch(1, 1)

        self.horizontalLayout_22.addWidget(self.fsetFrame)


        self.verticalLayout_38.addWidget(self.widget_5)


        self.verticalLayout_37.addWidget(self.setfocusFrame)

        self.loffsetFrame = QFrame(self.laserconfFrame)
        self.loffsetFrame.setObjectName(u"loffsetFrame")
        self.loffsetFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.loffsetFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_42 = QVBoxLayout(self.loffsetFrame)
        self.verticalLayout_42.setObjectName(u"verticalLayout_42")
        self.verticalLayout_42.setContentsMargins(9, -1, -1, -1)
        self.label_16 = QLabel(self.loffsetFrame)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setFont(font5)
        self.label_16.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_42.addWidget(self.label_16, 0, Qt.AlignmentFlag.AlignHCenter)

        self.widget_8 = QWidget(self.loffsetFrame)
        self.widget_8.setObjectName(u"widget_8")
        self.horizontalLayout_37 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalLayout_37.setContentsMargins(0, 0, 0, 0)
        self.offlaserFrame = QFrame(self.widget_8)
        self.offlaserFrame.setObjectName(u"offlaserFrame")
        self.offlaserFrame.setStyleSheet(u"")
        self.offlaserFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.offlaserFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_46 = QVBoxLayout(self.offlaserFrame)
        self.verticalLayout_46.setSpacing(6)
        self.verticalLayout_46.setObjectName(u"verticalLayout_46")
        self.verticalLayout_46.setContentsMargins(0, 0, 0, 0)
        self.widget_9 = QWidget(self.offlaserFrame)
        self.widget_9.setObjectName(u"widget_9")
        self.verticalLayout_47 = QVBoxLayout(self.widget_9)
        self.verticalLayout_47.setObjectName(u"verticalLayout_47")
        self.verticalLayout_47.setContentsMargins(9, -1, -1, -1)
        self.label_17 = QLabel(self.widget_9)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setMinimumSize(QSize(50, 0))
        self.label_17.setMaximumSize(QSize(90, 16777215))
        self.label_17.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")
        self.label_17.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_47.addWidget(self.label_17)

        self.offlaserComboBox = QComboBox(self.widget_9)
        self.offlaserComboBox.setObjectName(u"offlaserComboBox")
        sizePolicy6.setHeightForWidth(self.offlaserComboBox.sizePolicy().hasHeightForWidth())
        self.offlaserComboBox.setSizePolicy(sizePolicy6)
        self.offlaserComboBox.setMinimumSize(QSize(60, 25))
        self.offlaserComboBox.setMaximumSize(QSize(16777215, 30))
        self.offlaserComboBox.setFont(font)
        self.offlaserComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"	color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_47.addWidget(self.offlaserComboBox)

        self.verticalLayout_47.setStretch(0, 1)
        self.verticalLayout_47.setStretch(1, 3)

        self.verticalLayout_46.addWidget(self.widget_9)

        self.widget_17 = QWidget(self.offlaserFrame)
        self.widget_17.setObjectName(u"widget_17")
        self.horizontalLayout_51 = QHBoxLayout(self.widget_17)
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.offlaserPushButton = QPushButton(self.widget_17)
        self.offlaserPushButton.setObjectName(u"offlaserPushButton")
        self.offlaserPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.offlaserPushButton.sizePolicy().hasHeightForWidth())
        self.offlaserPushButton.setSizePolicy(sizePolicy6)
        self.offlaserPushButton.setMinimumSize(QSize(110, 0))
        self.offlaserPushButton.setMaximumSize(QSize(16777215, 150))
        self.offlaserPushButton.setFont(font2)
        self.offlaserPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_51.addWidget(self.offlaserPushButton)


        self.verticalLayout_46.addWidget(self.widget_17)

        self.verticalLayout_46.setStretch(0, 2)
        self.verticalLayout_46.setStretch(1, 1)

        self.horizontalLayout_37.addWidget(self.offlaserFrame)

        self.xyoffsetFrame = QFrame(self.widget_8)
        self.xyoffsetFrame.setObjectName(u"xyoffsetFrame")
        self.xyoffsetFrame.setStyleSheet(u"")
        self.xyoffsetFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.xyoffsetFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.xyoffsetFrame)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.widget_20 = QWidget(self.xyoffsetFrame)
        self.widget_20.setObjectName(u"widget_20")
        sizePolicy3.setHeightForWidth(self.widget_20.sizePolicy().hasHeightForWidth())
        self.widget_20.setSizePolicy(sizePolicy3)
        self.horizontalLayout_35 = QHBoxLayout(self.widget_20)
        self.horizontalLayout_35.setSpacing(0)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.horizontalLayout_35.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_6)

        self.offyplusPushButton = QPushButton(self.widget_20)
        self.offyplusPushButton.setObjectName(u"offyplusPushButton")
        sizePolicy6.setHeightForWidth(self.offyplusPushButton.sizePolicy().hasHeightForWidth())
        self.offyplusPushButton.setSizePolicy(sizePolicy6)
        self.offyplusPushButton.setMinimumSize(QSize(0, 0))
        self.offyplusPushButton.setMaximumSize(QSize(500, 150))
        self.offyplusPushButton.setFont(font2)
        self.offyplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_35.addWidget(self.offyplusPushButton)

        self.horizontalSpacer_7 = QSpacerItem(47, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer_7)


        self.verticalLayout_7.addWidget(self.widget_20)

        self.widget_21 = QWidget(self.xyoffsetFrame)
        self.widget_21.setObjectName(u"widget_21")
        self.horizontalLayout_40 = QHBoxLayout(self.widget_21)
        self.horizontalLayout_40.setSpacing(5)
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.horizontalLayout_40.setContentsMargins(0, 0, 0, 0)
        self.offxminusPushButton = QPushButton(self.widget_21)
        self.offxminusPushButton.setObjectName(u"offxminusPushButton")
        sizePolicy6.setHeightForWidth(self.offxminusPushButton.sizePolicy().hasHeightForWidth())
        self.offxminusPushButton.setSizePolicy(sizePolicy6)
        self.offxminusPushButton.setMinimumSize(QSize(0, 0))
        self.offxminusPushButton.setMaximumSize(QSize(500, 150))
        self.offxminusPushButton.setFont(font2)
        self.offxminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_40.addWidget(self.offxminusPushButton)

        self.travelPushButton = QPushButton(self.widget_21)
        self.travelPushButton.setObjectName(u"travelPushButton")
        sizePolicy6.setHeightForWidth(self.travelPushButton.sizePolicy().hasHeightForWidth())
        self.travelPushButton.setSizePolicy(sizePolicy6)
        self.travelPushButton.setMaximumSize(QSize(500, 150))
        self.travelPushButton.setFont(font2)
        self.travelPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_40.addWidget(self.travelPushButton)

        self.offxplusPushButton = QPushButton(self.widget_21)
        self.offxplusPushButton.setObjectName(u"offxplusPushButton")
        sizePolicy6.setHeightForWidth(self.offxplusPushButton.sizePolicy().hasHeightForWidth())
        self.offxplusPushButton.setSizePolicy(sizePolicy6)
        self.offxplusPushButton.setMinimumSize(QSize(0, 0))
        self.offxplusPushButton.setMaximumSize(QSize(500, 150))
        self.offxplusPushButton.setFont(font2)
        self.offxplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_40.addWidget(self.offxplusPushButton)


        self.verticalLayout_7.addWidget(self.widget_21)

        self.widget_22 = QWidget(self.xyoffsetFrame)
        self.widget_22.setObjectName(u"widget_22")
        self.widget_22.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_39 = QHBoxLayout(self.widget_22)
        self.horizontalLayout_39.setSpacing(0)
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.horizontalLayout_39.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_8 = QSpacerItem(47, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_8)

        self.offyminusPushButton = QPushButton(self.widget_22)
        self.offyminusPushButton.setObjectName(u"offyminusPushButton")
        sizePolicy6.setHeightForWidth(self.offyminusPushButton.sizePolicy().hasHeightForWidth())
        self.offyminusPushButton.setSizePolicy(sizePolicy6)
        self.offyminusPushButton.setMinimumSize(QSize(0, 0))
        self.offyminusPushButton.setMaximumSize(QSize(500, 150))
        self.offyminusPushButton.setFont(font2)
        self.offyminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_39.addWidget(self.offyminusPushButton)

        self.horizontalSpacer_9 = QSpacerItem(47, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_39.addItem(self.horizontalSpacer_9)


        self.verticalLayout_7.addWidget(self.widget_22)


        self.horizontalLayout_37.addWidget(self.xyoffsetFrame)

        self.xyposFrame = QFrame(self.widget_8)
        self.xyposFrame.setObjectName(u"xyposFrame")
        self.xyposFrame.setStyleSheet(u"")
        self.xyposFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.xyposFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_48 = QVBoxLayout(self.xyposFrame)
        self.verticalLayout_48.setObjectName(u"verticalLayout_48")
        self.verticalLayout_48.setContentsMargins(0, 0, 0, 0)
        self.widget_23 = QWidget(self.xyposFrame)
        self.widget_23.setObjectName(u"widget_23")
        self.horizontalLayout_55 = QHBoxLayout(self.widget_23)
        self.horizontalLayout_55.setSpacing(6)
        self.horizontalLayout_55.setObjectName(u"horizontalLayout_55")
        self.horizontalLayout_55.setContentsMargins(9, -1, 9, -1)
        self.label_18 = QLabel(self.widget_23)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setMaximumSize(QSize(25, 16777215))
        self.label_18.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 20px;\n"
"    border: none;\n"
"}")

        self.horizontalLayout_55.addWidget(self.label_18)

        self.xoffsetLCDNumber = QLCDNumber(self.widget_23)
        self.xoffsetLCDNumber.setObjectName(u"xoffsetLCDNumber")
        sizePolicy6.setHeightForWidth(self.xoffsetLCDNumber.sizePolicy().hasHeightForWidth())
        self.xoffsetLCDNumber.setSizePolicy(sizePolicy6)
        self.xoffsetLCDNumber.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_55.addWidget(self.xoffsetLCDNumber)

        self.horizontalLayout_55.setStretch(0, 1)
        self.horizontalLayout_55.setStretch(1, 3)

        self.verticalLayout_48.addWidget(self.widget_23)

        self.widget_31 = QWidget(self.xyposFrame)
        self.widget_31.setObjectName(u"widget_31")
        self.horizontalLayout_56 = QHBoxLayout(self.widget_31)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.label_19 = QLabel(self.widget_31)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setMaximumSize(QSize(25, 16777215))
        self.label_19.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 20px;\n"
"    border: none;\n"
"}")

        self.horizontalLayout_56.addWidget(self.label_19)

        self.yoffsetLCDNumber = QLCDNumber(self.widget_31)
        self.yoffsetLCDNumber.setObjectName(u"yoffsetLCDNumber")
        sizePolicy6.setHeightForWidth(self.yoffsetLCDNumber.sizePolicy().hasHeightForWidth())
        self.yoffsetLCDNumber.setSizePolicy(sizePolicy6)
        self.yoffsetLCDNumber.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_56.addWidget(self.yoffsetLCDNumber)

        self.horizontalLayout_56.setStretch(0, 1)
        self.horizontalLayout_56.setStretch(1, 3)

        self.verticalLayout_48.addWidget(self.widget_31)


        self.horizontalLayout_37.addWidget(self.xyposFrame)

        self.offbtnFrame = QFrame(self.widget_8)
        self.offbtnFrame.setObjectName(u"offbtnFrame")
        self.offbtnFrame.setStyleSheet(u"")
        self.offbtnFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.offbtnFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_49 = QVBoxLayout(self.offbtnFrame)
        self.verticalLayout_49.setSpacing(9)
        self.verticalLayout_49.setObjectName(u"verticalLayout_49")
        self.verticalLayout_49.setContentsMargins(9, 9, 9, 9)
        self.offzeroPushButton = QPushButton(self.offbtnFrame)
        self.offzeroPushButton.setObjectName(u"offzeroPushButton")
        self.offzeroPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.offzeroPushButton.sizePolicy().hasHeightForWidth())
        self.offzeroPushButton.setSizePolicy(sizePolicy6)
        self.offzeroPushButton.setMinimumSize(QSize(0, 0))
        self.offzeroPushButton.setMaximumSize(QSize(500, 150))
        self.offzeroPushButton.setFont(font2)
        self.offzeroPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_49.addWidget(self.offzeroPushButton)

        self.offsetPushButton = QPushButton(self.offbtnFrame)
        self.offsetPushButton.setObjectName(u"offsetPushButton")
        self.offsetPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.offsetPushButton.sizePolicy().hasHeightForWidth())
        self.offsetPushButton.setSizePolicy(sizePolicy6)
        self.offsetPushButton.setMinimumSize(QSize(0, 0))
        self.offsetPushButton.setMaximumSize(QSize(500, 150))
        self.offsetPushButton.setFont(font2)
        self.offsetPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.verticalLayout_49.addWidget(self.offsetPushButton)


        self.horizontalLayout_37.addWidget(self.offbtnFrame)

        self.horizontalLayout_37.setStretch(0, 1)
        self.horizontalLayout_37.setStretch(1, 2)
        self.horizontalLayout_37.setStretch(2, 2)
        self.horizontalLayout_37.setStretch(3, 1)

        self.verticalLayout_42.addWidget(self.widget_8)


        self.verticalLayout_37.addWidget(self.loffsetFrame)

        self.verticalLayout_37.setStretch(0, 3)
        self.verticalLayout_37.setStretch(1, 5)

        self.verticalLayout_36.addWidget(self.laserconfFrame)

        self.mainPages.addWidget(self.laserconfPage)
        self.programPage = QWidget()
        self.programPage.setObjectName(u"programPage")
        self.verticalLayout_16 = QVBoxLayout(self.programPage)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.page2Label = QLabel(self.programPage)
        self.page2Label.setObjectName(u"page2Label")
        self.page2Label.setMinimumSize(QSize(0, 20))
        self.page2Label.setMaximumSize(QSize(16777215, 20))
        self.page2Label.setFont(font2)
        self.page2Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_16.addWidget(self.page2Label)

        self.programFrame = QFrame(self.programPage)
        self.programFrame.setObjectName(u"programFrame")
        self.programFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.programFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.programFrame)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.progFrame = QFrame(self.programFrame)
        self.progFrame.setObjectName(u"progFrame")
        self.progFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.progFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.progFrame)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.widget_10 = QWidget(self.progFrame)
        self.widget_10.setObjectName(u"widget_10")
        self.horizontalLayout_32 = QHBoxLayout(self.widget_10)
        self.horizontalLayout_32.setSpacing(10)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.horizontalLayout_32.setContentsMargins(9, -1, -1, -1)
        self.label_8 = QLabel(self.widget_10)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(0, 0))
        self.label_8.setMaximumSize(QSize(120, 16777215))
        font9 = QFont()
        font9.setPointSize(13)
        font9.setBold(True)
        self.label_8.setFont(font9)
        self.label_8.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_32.addWidget(self.label_8)

        self.pgmfileTextEdit = QTextEdit(self.widget_10)
        self.pgmfileTextEdit.setObjectName(u"pgmfileTextEdit")
        sizePolicy6.setHeightForWidth(self.pgmfileTextEdit.sizePolicy().hasHeightForWidth())
        self.pgmfileTextEdit.setSizePolicy(sizePolicy6)
        self.pgmfileTextEdit.setMinimumSize(QSize(320, 0))
        self.pgmfileTextEdit.setMaximumSize(QSize(16777215, 60))
        self.pgmfileTextEdit.setFont(font9)
        self.pgmfileTextEdit.setStyleSheet(u"QTextEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}")
        self.pgmfileTextEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.pgmfileTextEdit.setReadOnly(True)

        self.horizontalLayout_32.addWidget(self.pgmfileTextEdit)

        self.pgmfilePushButton = QPushButton(self.widget_10)
        self.pgmfilePushButton.setObjectName(u"pgmfilePushButton")
        sizePolicy6.setHeightForWidth(self.pgmfilePushButton.sizePolicy().hasHeightForWidth())
        self.pgmfilePushButton.setSizePolicy(sizePolicy6)
        self.pgmfilePushButton.setMaximumSize(QSize(350, 100))
        self.pgmfilePushButton.setFont(font2)
        self.pgmfilePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_32.addWidget(self.pgmfilePushButton)

        self.horizontalLayout_32.setStretch(0, 1)
        self.horizontalLayout_32.setStretch(1, 2)
        self.horizontalLayout_32.setStretch(2, 1)

        self.verticalLayout_28.addWidget(self.widget_10)

        self.widget_3 = QWidget(self.progFrame)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_24 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_24.setSpacing(9)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_6 = QLabel(self.widget_3)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(0, 0))
        self.label_6.setMaximumSize(QSize(130, 16777215))
        self.label_6.setFont(font9)
        self.label_6.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_24.addWidget(self.label_6)

        self.pgmheightLineEdit = QLineEdit(self.widget_3)
        self.pgmheightLineEdit.setObjectName(u"pgmheightLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmheightLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmheightLineEdit.setSizePolicy(sizePolicy6)
        self.pgmheightLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmheightLineEdit.setFont(font9)
        self.pgmheightLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmheightLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_24.addWidget(self.pgmheightLineEdit)

        self.label_9 = QLabel(self.widget_3)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font9)
        self.label_9.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_24.addWidget(self.label_9)

        self.pgmheightPushButton = QPushButton(self.widget_3)
        self.pgmheightPushButton.setObjectName(u"pgmheightPushButton")
        self.pgmheightPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.pgmheightPushButton.sizePolicy().hasHeightForWidth())
        self.pgmheightPushButton.setSizePolicy(sizePolicy6)
        self.pgmheightPushButton.setMaximumSize(QSize(16777215, 100))
        self.pgmheightPushButton.setFont(font2)
        self.pgmheightPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_24.addWidget(self.pgmheightPushButton)

        self.horizontalLayout_24.setStretch(0, 1)
        self.horizontalLayout_24.setStretch(1, 3)
        self.horizontalLayout_24.setStretch(3, 1)

        self.verticalLayout_28.addWidget(self.widget_3)

        self.widget_4 = QWidget(self.progFrame)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_41 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.label_13 = QLabel(self.widget_4)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMaximumSize(QSize(130, 16777215))
        self.label_13.setFont(font9)
        self.label_13.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_41.addWidget(self.label_13)

        self.pgmfeedLineEdit = QLineEdit(self.widget_4)
        self.pgmfeedLineEdit.setObjectName(u"pgmfeedLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmfeedLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmfeedLineEdit.setSizePolicy(sizePolicy6)
        self.pgmfeedLineEdit.setMinimumSize(QSize(280, 0))
        self.pgmfeedLineEdit.setFont(font9)
        self.pgmfeedLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmfeedLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_41.addWidget(self.pgmfeedLineEdit)

        self.label_14 = QLabel(self.widget_4)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(0, 0))
        self.label_14.setFont(font9)
        self.label_14.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_41.addWidget(self.label_14)

        self.pgmfeedPushButton = QPushButton(self.widget_4)
        self.pgmfeedPushButton.setObjectName(u"pgmfeedPushButton")
        self.pgmfeedPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.pgmfeedPushButton.sizePolicy().hasHeightForWidth())
        self.pgmfeedPushButton.setSizePolicy(sizePolicy6)
        self.pgmfeedPushButton.setMaximumSize(QSize(180, 100))
        self.pgmfeedPushButton.setFont(font2)
        self.pgmfeedPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_41.addWidget(self.pgmfeedPushButton)


        self.verticalLayout_28.addWidget(self.widget_4)

        self.widget_2 = QWidget(self.progFrame)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_23 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_23.setSpacing(9)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_5 = QLabel(self.widget_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(132, 16777215))
        self.label_5.setFont(font9)
        self.label_5.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_23.addWidget(self.label_5)

        self.pgmlaserComboBox = QComboBox(self.widget_2)
        self.pgmlaserComboBox.setObjectName(u"pgmlaserComboBox")
        sizePolicy6.setHeightForWidth(self.pgmlaserComboBox.sizePolicy().hasHeightForWidth())
        self.pgmlaserComboBox.setSizePolicy(sizePolicy6)
        self.pgmlaserComboBox.setMaximumSize(QSize(16777215, 100))
        self.pgmlaserComboBox.setFont(font9)
        self.pgmlaserComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"	color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_23.addWidget(self.pgmlaserComboBox)

        self.pgmlaserPushButton = QPushButton(self.widget_2)
        self.pgmlaserPushButton.setObjectName(u"pgmlaserPushButton")
        self.pgmlaserPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.pgmlaserPushButton.sizePolicy().hasHeightForWidth())
        self.pgmlaserPushButton.setSizePolicy(sizePolicy6)
        self.pgmlaserPushButton.setMaximumSize(QSize(16777215, 100))
        self.pgmlaserPushButton.setFont(font2)
        self.pgmlaserPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_23.addWidget(self.pgmlaserPushButton)

        self.horizontalLayout_23.setStretch(0, 1)
        self.horizontalLayout_23.setStretch(1, 2)
        self.horizontalLayout_23.setStretch(2, 1)

        self.verticalLayout_28.addWidget(self.widget_2)

        self.widget_11 = QWidget(self.progFrame)
        self.widget_11.setObjectName(u"widget_11")
        self.horizontalLayout_26 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.label_25 = QLabel(self.widget_11)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setMinimumSize(QSize(0, 0))
        self.label_25.setMaximumSize(QSize(120, 16777215))
        self.label_25.setFont(font9)
        self.label_25.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_26.addWidget(self.label_25)

        self.recipefileTextEdit = QTextEdit(self.widget_11)
        self.recipefileTextEdit.setObjectName(u"recipefileTextEdit")
        sizePolicy6.setHeightForWidth(self.recipefileTextEdit.sizePolicy().hasHeightForWidth())
        self.recipefileTextEdit.setSizePolicy(sizePolicy6)
        self.recipefileTextEdit.setMinimumSize(QSize(320, 0))
        self.recipefileTextEdit.setMaximumSize(QSize(16777215, 60))
        self.recipefileTextEdit.setFont(font9)
        self.recipefileTextEdit.setStyleSheet(u"QTextEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}")
        self.recipefileTextEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.recipefileTextEdit.setReadOnly(True)

        self.horizontalLayout_26.addWidget(self.recipefileTextEdit)

        self.pgmsavePushButton = QPushButton(self.widget_11)
        self.pgmsavePushButton.setObjectName(u"pgmsavePushButton")
        self.pgmsavePushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.pgmsavePushButton.sizePolicy().hasHeightForWidth())
        self.pgmsavePushButton.setSizePolicy(sizePolicy6)
        self.pgmsavePushButton.setMaximumSize(QSize(16777215, 100))
        self.pgmsavePushButton.setFont(font2)
        self.pgmsavePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_26.addWidget(self.pgmsavePushButton)


        self.verticalLayout_28.addWidget(self.widget_11)


        self.verticalLayout_27.addWidget(self.progFrame)


        self.verticalLayout_16.addWidget(self.programFrame)

        self.mainPages.addWidget(self.programPage)
        self.recipePage = QWidget()
        self.recipePage.setObjectName(u"recipePage")
        self.verticalLayout_133 = QVBoxLayout(self.recipePage)
        self.verticalLayout_133.setObjectName(u"verticalLayout_133")
        self.page4Label = QLabel(self.recipePage)
        self.page4Label.setObjectName(u"page4Label")
        self.page4Label.setMinimumSize(QSize(0, 20))
        self.page4Label.setMaximumSize(QSize(16777215, 20))
        self.page4Label.setFont(font2)
        self.page4Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_133.addWidget(self.page4Label)

        self.recipeFrame = QFrame(self.recipePage)
        self.recipeFrame.setObjectName(u"recipeFrame")
        self.recipeFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.recipeFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_131 = QVBoxLayout(self.recipeFrame)
        self.verticalLayout_131.setObjectName(u"verticalLayout_131")
        self.rcpFrame = QFrame(self.recipeFrame)
        self.rcpFrame.setObjectName(u"rcpFrame")
        self.rcpFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.rcpFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_132 = QVBoxLayout(self.rcpFrame)
        self.verticalLayout_132.setObjectName(u"verticalLayout_132")
        self.widget_50 = QWidget(self.rcpFrame)
        self.widget_50.setObjectName(u"widget_50")
        self.horizontalLayout_117 = QHBoxLayout(self.widget_50)
        self.horizontalLayout_117.setSpacing(10)
        self.horizontalLayout_117.setObjectName(u"horizontalLayout_117")
        self.horizontalLayout_117.setContentsMargins(9, -1, -1, -1)
        self.label_72 = QLabel(self.widget_50)
        self.label_72.setObjectName(u"label_72")
        self.label_72.setMinimumSize(QSize(0, 0))
        self.label_72.setMaximumSize(QSize(120, 16777215))
        self.label_72.setFont(font9)
        self.label_72.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_117.addWidget(self.label_72)

        self.rcpfileTextEdit = QTextEdit(self.widget_50)
        self.rcpfileTextEdit.setObjectName(u"rcpfileTextEdit")
        sizePolicy6.setHeightForWidth(self.rcpfileTextEdit.sizePolicy().hasHeightForWidth())
        self.rcpfileTextEdit.setSizePolicy(sizePolicy6)
        self.rcpfileTextEdit.setMinimumSize(QSize(320, 0))
        self.rcpfileTextEdit.setMaximumSize(QSize(16777215, 60))
        self.rcpfileTextEdit.setFont(font9)
        self.rcpfileTextEdit.setStyleSheet(u"QTextEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}")
        self.rcpfileTextEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.rcpfileTextEdit.setReadOnly(True)

        self.horizontalLayout_117.addWidget(self.rcpfileTextEdit)

        self.rcpfilePushButton = QPushButton(self.widget_50)
        self.rcpfilePushButton.setObjectName(u"rcpfilePushButton")
        sizePolicy6.setHeightForWidth(self.rcpfilePushButton.sizePolicy().hasHeightForWidth())
        self.rcpfilePushButton.setSizePolicy(sizePolicy6)
        self.rcpfilePushButton.setMaximumSize(QSize(350, 100))
        self.rcpfilePushButton.setFont(font2)
        self.rcpfilePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_117.addWidget(self.rcpfilePushButton)

        self.horizontalLayout_117.setStretch(0, 1)
        self.horizontalLayout_117.setStretch(1, 2)
        self.horizontalLayout_117.setStretch(2, 1)

        self.verticalLayout_132.addWidget(self.widget_50)

        self.widget_51 = QWidget(self.rcpFrame)
        self.widget_51.setObjectName(u"widget_51")
        self.horizontalLayout_118 = QHBoxLayout(self.widget_51)
        self.horizontalLayout_118.setSpacing(9)
        self.horizontalLayout_118.setObjectName(u"horizontalLayout_118")
        self.label_73 = QLabel(self.widget_51)
        self.label_73.setObjectName(u"label_73")
        self.label_73.setMinimumSize(QSize(0, 0))
        self.label_73.setMaximumSize(QSize(130, 16777215))
        self.label_73.setFont(font9)
        self.label_73.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_118.addWidget(self.label_73)

        self.rcpheightLineEdit = QLineEdit(self.widget_51)
        self.rcpheightLineEdit.setObjectName(u"rcpheightLineEdit")
        sizePolicy6.setHeightForWidth(self.rcpheightLineEdit.sizePolicy().hasHeightForWidth())
        self.rcpheightLineEdit.setSizePolicy(sizePolicy6)
        self.rcpheightLineEdit.setMaximumSize(QSize(16777215, 100))
        self.rcpheightLineEdit.setFont(font9)
        self.rcpheightLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.rcpheightLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_118.addWidget(self.rcpheightLineEdit)

        self.label_74 = QLabel(self.widget_51)
        self.label_74.setObjectName(u"label_74")
        self.label_74.setFont(font9)
        self.label_74.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_118.addWidget(self.label_74)

        self.horizontalLayout_118.setStretch(0, 1)
        self.horizontalLayout_118.setStretch(1, 3)

        self.verticalLayout_132.addWidget(self.widget_51)

        self.widget_52 = QWidget(self.rcpFrame)
        self.widget_52.setObjectName(u"widget_52")
        self.horizontalLayout_119 = QHBoxLayout(self.widget_52)
        self.horizontalLayout_119.setObjectName(u"horizontalLayout_119")
        self.label_75 = QLabel(self.widget_52)
        self.label_75.setObjectName(u"label_75")
        self.label_75.setMaximumSize(QSize(130, 16777215))
        self.label_75.setFont(font9)
        self.label_75.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_119.addWidget(self.label_75)

        self.rcpfeedLineEdit = QLineEdit(self.widget_52)
        self.rcpfeedLineEdit.setObjectName(u"rcpfeedLineEdit")
        sizePolicy6.setHeightForWidth(self.rcpfeedLineEdit.sizePolicy().hasHeightForWidth())
        self.rcpfeedLineEdit.setSizePolicy(sizePolicy6)
        self.rcpfeedLineEdit.setMinimumSize(QSize(280, 0))
        self.rcpfeedLineEdit.setFont(font9)
        self.rcpfeedLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.rcpfeedLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_119.addWidget(self.rcpfeedLineEdit)

        self.label_76 = QLabel(self.widget_52)
        self.label_76.setObjectName(u"label_76")
        self.label_76.setMinimumSize(QSize(0, 0))
        self.label_76.setFont(font9)
        self.label_76.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_119.addWidget(self.label_76)


        self.verticalLayout_132.addWidget(self.widget_52)

        self.widget_53 = QWidget(self.rcpFrame)
        self.widget_53.setObjectName(u"widget_53")
        self.horizontalLayout_120 = QHBoxLayout(self.widget_53)
        self.horizontalLayout_120.setSpacing(9)
        self.horizontalLayout_120.setObjectName(u"horizontalLayout_120")
        self.label_77 = QLabel(self.widget_53)
        self.label_77.setObjectName(u"label_77")
        self.label_77.setMaximumSize(QSize(132, 16777215))
        self.label_77.setFont(font9)
        self.label_77.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_120.addWidget(self.label_77)

        self.rcplaserComboBox = QComboBox(self.widget_53)
        self.rcplaserComboBox.setObjectName(u"rcplaserComboBox")
        sizePolicy6.setHeightForWidth(self.rcplaserComboBox.sizePolicy().hasHeightForWidth())
        self.rcplaserComboBox.setSizePolicy(sizePolicy6)
        self.rcplaserComboBox.setMaximumSize(QSize(16777215, 100))
        self.rcplaserComboBox.setFont(font9)
        self.rcplaserComboBox.setStyleSheet(u"QComboBox {\n"
"	background-color: rgb(144, 170, 197);\n"
"    border: 2px solid rgb(16, 42, 131);\n"
"	color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"	background-color: rgb(144, 170, 197);\n"
"	selection-background-color: #A0D0F0;\n"
"	color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_120.addWidget(self.rcplaserComboBox)

        self.horizontalLayout_120.setStretch(0, 1)
        self.horizontalLayout_120.setStretch(1, 2)

        self.verticalLayout_132.addWidget(self.widget_53)

        self.widget_54 = QWidget(self.rcpFrame)
        self.widget_54.setObjectName(u"widget_54")
        self.horizontalLayout_121 = QHBoxLayout(self.widget_54)
        self.horizontalLayout_121.setObjectName(u"horizontalLayout_121")
        self.horizontalSpacer_25 = QSpacerItem(428, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_121.addItem(self.horizontalSpacer_25)

        self.rcploadPushButton = QPushButton(self.widget_54)
        self.rcploadPushButton.setObjectName(u"rcploadPushButton")
        self.rcploadPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.rcploadPushButton.sizePolicy().hasHeightForWidth())
        self.rcploadPushButton.setSizePolicy(sizePolicy6)
        self.rcploadPushButton.setMaximumSize(QSize(350, 100))
        self.rcploadPushButton.setFont(font2)
        self.rcploadPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_121.addWidget(self.rcploadPushButton)


        self.verticalLayout_132.addWidget(self.widget_54)


        self.verticalLayout_131.addWidget(self.rcpFrame)


        self.verticalLayout_133.addWidget(self.recipeFrame)

        self.mainPages.addWidget(self.recipePage)
        self.printPage = QWidget()
        self.printPage.setObjectName(u"printPage")
        self.verticalLayout_14 = QVBoxLayout(self.printPage)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.page3Label = QLabel(self.printPage)
        self.page3Label.setObjectName(u"page3Label")
        self.page3Label.setMinimumSize(QSize(0, 20))
        self.page3Label.setMaximumSize(QSize(16777215, 20))
        self.page3Label.setFont(font2)
        self.page3Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_14.addWidget(self.page3Label)

        self.printFrame = QFrame(self.printPage)
        self.printFrame.setObjectName(u"printFrame")
        self.printFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.printFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_30 = QVBoxLayout(self.printFrame)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.frame_10 = QFrame(self.printFrame)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_28 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.printimgFrame = QFrame(self.frame_10)
        self.printimgFrame.setObjectName(u"printimgFrame")
        self.printimgFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.printimgFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_31 = QVBoxLayout(self.printimgFrame)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.label_11 = QLabel(self.printimgFrame)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font5)
        self.label_11.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_31.addWidget(self.label_11, 0, Qt.AlignmentFlag.AlignHCenter)

        self.printplotFrame = QFrame(self.printimgFrame)
        self.printplotFrame.setObjectName(u"printplotFrame")
        self.printplotFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.printplotFrame.setFrameShadow(QFrame.Shadow.Plain)

        self.verticalLayout_31.addWidget(self.printplotFrame)

        self.verticalLayout_31.setStretch(0, 1)
        self.verticalLayout_31.setStretch(1, 115)

        self.horizontalLayout_28.addWidget(self.printimgFrame)

        self.printopFrame = QFrame(self.frame_10)
        self.printopFrame.setObjectName(u"printopFrame")
        self.printopFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.printopFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_32 = QVBoxLayout(self.printopFrame)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.label_12 = QLabel(self.printopFrame)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setMinimumSize(QSize(20, 20))
        self.label_12.setMaximumSize(QSize(80, 20))
        self.label_12.setFont(font5)
        self.label_12.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_32.addWidget(self.label_12)

        self.printrunPushButton = QPushButton(self.printopFrame)
        self.printrunPushButton.setObjectName(u"printrunPushButton")
        sizePolicy6.setHeightForWidth(self.printrunPushButton.sizePolicy().hasHeightForWidth())
        self.printrunPushButton.setSizePolicy(sizePolicy6)
        font10 = QFont()
        font10.setPointSize(13)
        self.printrunPushButton.setFont(font10)
        self.printrunPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        icon20 = QIcon()
        icon20.addFile(u":/icons/icons/play.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.printrunPushButton.setIcon(icon20)
        self.printrunPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_32.addWidget(self.printrunPushButton)

        self.printpausePushButton = QPushButton(self.printopFrame)
        self.printpausePushButton.setObjectName(u"printpausePushButton")
        self.printpausePushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.printpausePushButton.sizePolicy().hasHeightForWidth())
        self.printpausePushButton.setSizePolicy(sizePolicy6)
        self.printpausePushButton.setFont(font10)
        self.printpausePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        icon21 = QIcon()
        icon21.addFile(u":/icons/icons/pause.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.printpausePushButton.setIcon(icon21)
        self.printpausePushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_32.addWidget(self.printpausePushButton)

        self.printabortPushButton = QPushButton(self.printopFrame)
        self.printabortPushButton.setObjectName(u"printabortPushButton")
        self.printabortPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.printabortPushButton.sizePolicy().hasHeightForWidth())
        self.printabortPushButton.setSizePolicy(sizePolicy6)
        self.printabortPushButton.setFont(font10)
        self.printabortPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        self.printabortPushButton.setIcon(icon18)
        self.printabortPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_32.addWidget(self.printabortPushButton)

        self.inspectionPushButton = QPushButton(self.printopFrame)
        self.inspectionPushButton.setObjectName(u"inspectionPushButton")
        sizePolicy6.setHeightForWidth(self.inspectionPushButton.sizePolicy().hasHeightForWidth())
        self.inspectionPushButton.setSizePolicy(sizePolicy6)
        self.inspectionPushButton.setFont(font10)
        self.inspectionPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        icon22 = QIcon()
        icon22.addFile(u":/icons/icons/search.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.inspectionPushButton.setIcon(icon22)
        self.inspectionPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_32.addWidget(self.inspectionPushButton)


        self.horizontalLayout_28.addWidget(self.printopFrame)

        self.horizontalLayout_28.setStretch(0, 4)

        self.verticalLayout_30.addWidget(self.frame_10)

        self.printprogressFrame = QFrame(self.printFrame)
        self.printprogressFrame.setObjectName(u"printprogressFrame")
        sizePolicy6.setHeightForWidth(self.printprogressFrame.sizePolicy().hasHeightForWidth())
        self.printprogressFrame.setSizePolicy(sizePolicy6)
        self.printprogressFrame.setMaximumSize(QSize(16777215, 60))
        self.printprogressFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.printprogressFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_27 = QHBoxLayout(self.printprogressFrame)
        self.horizontalLayout_27.setSpacing(10)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalLayout_27.setContentsMargins(5, -1, 5, -1)
        self.label_10 = QLabel(self.printprogressFrame)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(0, 0))
        self.label_10.setMaximumSize(QSize(75, 16777215))
        self.label_10.setFont(font5)
        self.label_10.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_27.addWidget(self.label_10)

        self.printProgressBar = QProgressBar(self.printprogressFrame)
        self.printProgressBar.setObjectName(u"printProgressBar")
        self.printProgressBar.setFont(font5)
        self.printProgressBar.setStyleSheet(u"QProgressBar {\n"
"	color: rgb(16, 42, 131);\n"
"	border-style: solid;\n"
"	border-color: grey;\n"
"	border-width: 2px;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-radius: 2px;\n"
"	width: 6px;\n"
"	margin: 1px;\n"
"}")
        self.printProgressBar.setValue(100)
        self.printProgressBar.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.printProgressBar.setTextDirection(QProgressBar.Direction.TopToBottom)

        self.horizontalLayout_27.addWidget(self.printProgressBar)

        self.progressLabel = QLabel(self.printprogressFrame)
        self.progressLabel.setObjectName(u"progressLabel")
        self.progressLabel.setFont(font5)
        self.progressLabel.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")
        self.progressLabel.setScaledContents(False)
        self.progressLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_27.addWidget(self.progressLabel)


        self.verticalLayout_30.addWidget(self.printprogressFrame)

        self.verticalLayout_30.setStretch(0, 5)
        self.verticalLayout_30.setStretch(1, 1)

        self.verticalLayout_14.addWidget(self.printFrame)

        self.mainPages.addWidget(self.printPage)
        self.cameraPage = QWidget()
        self.cameraPage.setObjectName(u"cameraPage")
        self.verticalLayout_57 = QVBoxLayout(self.cameraPage)
        self.verticalLayout_57.setObjectName(u"verticalLayout_57")
        self.page3Label_4 = QLabel(self.cameraPage)
        self.page3Label_4.setObjectName(u"page3Label_4")
        self.page3Label_4.setMinimumSize(QSize(0, 20))
        self.page3Label_4.setMaximumSize(QSize(16777215, 20))
        self.page3Label_4.setFont(font2)
        self.page3Label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_57.addWidget(self.page3Label_4)

        self.cameraFrame = QFrame(self.cameraPage)
        self.cameraFrame.setObjectName(u"cameraFrame")
        self.cameraFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.cameraFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_55 = QVBoxLayout(self.cameraFrame)
        self.verticalLayout_55.setObjectName(u"verticalLayout_55")
        self.camFrame = QFrame(self.cameraFrame)
        self.camFrame.setObjectName(u"camFrame")
        self.camFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.camFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_42 = QHBoxLayout(self.camFrame)
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.horizontalLayout_42.setContentsMargins(0, 0, 0, 0)
        self.printimgFrame_2 = QFrame(self.camFrame)
        self.printimgFrame_2.setObjectName(u"printimgFrame_2")
        self.printimgFrame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.printimgFrame_2.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_60 = QVBoxLayout(self.printimgFrame_2)
        self.verticalLayout_60.setObjectName(u"verticalLayout_60")
        self.camvdoFrame = QFrame(self.printimgFrame_2)
        self.camvdoFrame.setObjectName(u"camvdoFrame")
        self.camvdoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.camvdoFrame.setFrameShadow(QFrame.Shadow.Plain)

        self.verticalLayout_60.addWidget(self.camvdoFrame)

        self.cameraxyoffFrame = QFrame(self.printimgFrame_2)
        self.cameraxyoffFrame.setObjectName(u"cameraxyoffFrame")
        self.cameraxyoffFrame.setMaximumSize(QSize(16777215, 100))
        self.cameraxyoffFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.cameraxyoffFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_44 = QHBoxLayout(self.cameraxyoffFrame)
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.horizontalLayout_44.setContentsMargins(4, 4, 4, 4)
        self.frame_13 = QFrame(self.cameraxyoffFrame)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_59 = QVBoxLayout(self.frame_13)
        self.verticalLayout_59.setObjectName(u"verticalLayout_59")
        self.verticalLayout_59.setContentsMargins(0, 0, 0, 0)
        self.label_15 = QLabel(self.frame_13)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFont(font5)
        self.label_15.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_59.addWidget(self.label_15, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.frame_15 = QFrame(self.frame_13)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_45 = QHBoxLayout(self.frame_15)
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.horizontalLayout_45.setContentsMargins(0, 0, 0, 0)
        self.camoffxplusPushButton = QPushButton(self.frame_15)
        self.camoffxplusPushButton.setObjectName(u"camoffxplusPushButton")
        sizePolicy6.setHeightForWidth(self.camoffxplusPushButton.sizePolicy().hasHeightForWidth())
        self.camoffxplusPushButton.setSizePolicy(sizePolicy6)
        self.camoffxplusPushButton.setMinimumSize(QSize(0, 0))
        self.camoffxplusPushButton.setMaximumSize(QSize(50, 50))
        self.camoffxplusPushButton.setFont(font2)
        self.camoffxplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_45.addWidget(self.camoffxplusPushButton)

        self.camoffxminusPushButton = QPushButton(self.frame_15)
        self.camoffxminusPushButton.setObjectName(u"camoffxminusPushButton")
        sizePolicy6.setHeightForWidth(self.camoffxminusPushButton.sizePolicy().hasHeightForWidth())
        self.camoffxminusPushButton.setSizePolicy(sizePolicy6)
        self.camoffxminusPushButton.setMinimumSize(QSize(0, 0))
        self.camoffxminusPushButton.setMaximumSize(QSize(50, 50))
        self.camoffxminusPushButton.setFont(font2)
        self.camoffxminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_45.addWidget(self.camoffxminusPushButton)

        self.camoffyplusPushButton = QPushButton(self.frame_15)
        self.camoffyplusPushButton.setObjectName(u"camoffyplusPushButton")
        sizePolicy6.setHeightForWidth(self.camoffyplusPushButton.sizePolicy().hasHeightForWidth())
        self.camoffyplusPushButton.setSizePolicy(sizePolicy6)
        self.camoffyplusPushButton.setMinimumSize(QSize(0, 0))
        self.camoffyplusPushButton.setMaximumSize(QSize(50, 50))
        self.camoffyplusPushButton.setFont(font2)
        self.camoffyplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_45.addWidget(self.camoffyplusPushButton)

        self.camoffyminusPushButton = QPushButton(self.frame_15)
        self.camoffyminusPushButton.setObjectName(u"camoffyminusPushButton")
        sizePolicy6.setHeightForWidth(self.camoffyminusPushButton.sizePolicy().hasHeightForWidth())
        self.camoffyminusPushButton.setSizePolicy(sizePolicy6)
        self.camoffyminusPushButton.setMinimumSize(QSize(0, 0))
        self.camoffyminusPushButton.setMaximumSize(QSize(50, 50))
        self.camoffyminusPushButton.setFont(font2)
        self.camoffyminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_45.addWidget(self.camoffyminusPushButton)


        self.verticalLayout_59.addWidget(self.frame_15)


        self.horizontalLayout_44.addWidget(self.frame_13)

        self.frame_14 = QFrame(self.cameraxyoffFrame)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_58 = QVBoxLayout(self.frame_14)
        self.verticalLayout_58.setObjectName(u"verticalLayout_58")
        self.verticalLayout_58.setContentsMargins(0, 0, 0, 0)
        self.label_22 = QLabel(self.frame_14)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setFont(font5)
        self.label_22.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_58.addWidget(self.label_22, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.frame_17 = QFrame(self.frame_14)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_17.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_47 = QHBoxLayout(self.frame_17)
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.horizontalLayout_47.setContentsMargins(0, 0, 0, 0)
        self.camstep10_RadioButton = QRadioButton(self.frame_17)
        self.camstep10_RadioButton.setObjectName(u"camstep10_RadioButton")
        font11 = QFont()
        font11.setPointSize(10)
        font11.setBold(True)
        self.camstep10_RadioButton.setFont(font11)

        self.horizontalLayout_47.addWidget(self.camstep10_RadioButton)

        self.camstep5_RadioButton = QRadioButton(self.frame_17)
        self.camstep5_RadioButton.setObjectName(u"camstep5_RadioButton")
        self.camstep5_RadioButton.setFont(font11)

        self.horizontalLayout_47.addWidget(self.camstep5_RadioButton)

        self.camstep1_RadioButton = QRadioButton(self.frame_17)
        self.camstep1_RadioButton.setObjectName(u"camstep1_RadioButton")
        self.camstep1_RadioButton.setFont(font11)

        self.horizontalLayout_47.addWidget(self.camstep1_RadioButton)

        self.camstep01_RadioButton = QRadioButton(self.frame_17)
        self.camstep01_RadioButton.setObjectName(u"camstep01_RadioButton")
        self.camstep01_RadioButton.setFont(font11)

        self.horizontalLayout_47.addWidget(self.camstep01_RadioButton)


        self.verticalLayout_58.addWidget(self.frame_17)


        self.horizontalLayout_44.addWidget(self.frame_14)

        self.frame_11 = QFrame(self.cameraxyoffFrame)
        self.frame_11.setObjectName(u"frame_11")
        self.frame_11.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_56 = QVBoxLayout(self.frame_11)
        self.verticalLayout_56.setObjectName(u"verticalLayout_56")
        self.verticalLayout_56.setContentsMargins(0, 0, 0, 0)
        self.label_23 = QLabel(self.frame_11)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setFont(font5)
        self.label_23.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_56.addWidget(self.label_23, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.frame_16 = QFrame(self.frame_11)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_46 = QHBoxLayout(self.frame_16)
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.horizontalLayout_46.setContentsMargins(0, 0, 0, 0)
        self.camoffzplusPushButton = QPushButton(self.frame_16)
        self.camoffzplusPushButton.setObjectName(u"camoffzplusPushButton")
        sizePolicy6.setHeightForWidth(self.camoffzplusPushButton.sizePolicy().hasHeightForWidth())
        self.camoffzplusPushButton.setSizePolicy(sizePolicy6)
        self.camoffzplusPushButton.setMinimumSize(QSize(0, 0))
        self.camoffzplusPushButton.setMaximumSize(QSize(50, 50))
        self.camoffzplusPushButton.setFont(font2)
        self.camoffzplusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_46.addWidget(self.camoffzplusPushButton)

        self.camoffzminusPushButton = QPushButton(self.frame_16)
        self.camoffzminusPushButton.setObjectName(u"camoffzminusPushButton")
        sizePolicy6.setHeightForWidth(self.camoffzminusPushButton.sizePolicy().hasHeightForWidth())
        self.camoffzminusPushButton.setSizePolicy(sizePolicy6)
        self.camoffzminusPushButton.setMinimumSize(QSize(0, 0))
        self.camoffzminusPushButton.setMaximumSize(QSize(50, 50))
        self.camoffzminusPushButton.setFont(font2)
        self.camoffzminusPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_46.addWidget(self.camoffzminusPushButton)


        self.verticalLayout_56.addWidget(self.frame_16)


        self.horizontalLayout_44.addWidget(self.frame_11)

        self.horizontalLayout_44.setStretch(0, 4)
        self.horizontalLayout_44.setStretch(1, 2)
        self.horizontalLayout_44.setStretch(2, 2)

        self.verticalLayout_60.addWidget(self.cameraxyoffFrame)

        self.frame_2 = QFrame(self.printimgFrame_2)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_43 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.camstartPushButton = QPushButton(self.frame_2)
        self.camstartPushButton.setObjectName(u"camstartPushButton")
        sizePolicy6.setHeightForWidth(self.camstartPushButton.sizePolicy().hasHeightForWidth())
        self.camstartPushButton.setSizePolicy(sizePolicy6)
        self.camstartPushButton.setMaximumSize(QSize(350, 80))
        self.camstartPushButton.setFont(font2)
        self.camstartPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_43.addWidget(self.camstartPushButton)

        self.campausePushButton = QPushButton(self.frame_2)
        self.campausePushButton.setObjectName(u"campausePushButton")
        sizePolicy6.setHeightForWidth(self.campausePushButton.sizePolicy().hasHeightForWidth())
        self.campausePushButton.setSizePolicy(sizePolicy6)
        self.campausePushButton.setMaximumSize(QSize(350, 80))
        self.campausePushButton.setFont(font2)
        self.campausePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_43.addWidget(self.campausePushButton)

        self.camstopPushButton = QPushButton(self.frame_2)
        self.camstopPushButton.setObjectName(u"camstopPushButton")
        sizePolicy6.setHeightForWidth(self.camstopPushButton.sizePolicy().hasHeightForWidth())
        self.camstopPushButton.setSizePolicy(sizePolicy6)
        self.camstopPushButton.setMaximumSize(QSize(350, 80))
        self.camstopPushButton.setFont(font2)
        self.camstopPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 15px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")

        self.horizontalLayout_43.addWidget(self.camstopPushButton)


        self.verticalLayout_60.addWidget(self.frame_2)

        self.verticalLayout_60.setStretch(0, 9)
        self.verticalLayout_60.setStretch(1, 1)

        self.horizontalLayout_42.addWidget(self.printimgFrame_2)

        self.horizontalLayout_42.setStretch(0, 4)

        self.verticalLayout_55.addWidget(self.camFrame)

        self.verticalLayout_55.setStretch(0, 5)

        self.verticalLayout_57.addWidget(self.cameraFrame)

        self.mainPages.addWidget(self.cameraPage)
        self.terminalPage = QWidget()
        self.terminalPage.setObjectName(u"terminalPage")
        self.verticalLayout_34 = QVBoxLayout(self.terminalPage)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.page3Label_2 = QLabel(self.terminalPage)
        self.page3Label_2.setObjectName(u"page3Label_2")
        self.page3Label_2.setMinimumSize(QSize(0, 20))
        self.page3Label_2.setMaximumSize(QSize(16777215, 20))
        self.page3Label_2.setFont(font2)
        self.page3Label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_34.addWidget(self.page3Label_2)

        self.terminalFrame = QFrame(self.terminalPage)
        self.terminalFrame.setObjectName(u"terminalFrame")
        self.verticalLayout_29 = QVBoxLayout(self.terminalFrame)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.terminaloutFrame = QFrame(self.terminalFrame)
        self.terminaloutFrame.setObjectName(u"terminaloutFrame")
        self.horizontalLayout_30 = QHBoxLayout(self.terminaloutFrame)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.termresponseTextEdit = QTextEdit(self.terminaloutFrame)
        self.termresponseTextEdit.setObjectName(u"termresponseTextEdit")
        self.termresponseTextEdit.setFont(font)
        self.termresponseTextEdit.setStyleSheet(u"QTextEdit {\n"
"	background-color: rgb(144, 170, 197);\n"
"	border-radius: 12px;\n"
"	border: 2px solid rgb(16, 42, 131);\n"
"}")
        self.termresponseTextEdit.setFrameShape(QFrame.Shape.VLine)
        self.termresponseTextEdit.setFrameShadow(QFrame.Shadow.Raised)
        self.termresponseTextEdit.setLineWidth(1)

        self.horizontalLayout_30.addWidget(self.termresponseTextEdit)


        self.verticalLayout_29.addWidget(self.terminaloutFrame)

        self.terminalsendFrame = QFrame(self.terminalFrame)
        self.terminalsendFrame.setObjectName(u"terminalsendFrame")
        self.terminalsendFrame.setFrameShape(QFrame.Shape.Box)
        self.horizontalLayout_31 = QHBoxLayout(self.terminalsendFrame)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.termdataLineEdit = QLineEdit(self.terminalsendFrame)
        self.termdataLineEdit.setObjectName(u"termdataLineEdit")
        self.termdataLineEdit.setMinimumSize(QSize(0, 40))
        self.termdataLineEdit.setFont(font5)
        self.termdataLineEdit.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(144, 170, 197);\n"
"	border-radius: 12px;\n"
"	border: 2px solid rgb(16, 42, 131);\n"
"}")
        self.termdataLineEdit.setFrame(True)

        self.horizontalLayout_31.addWidget(self.termdataLineEdit)

        self.termsendPushButton = QPushButton(self.terminalsendFrame)
        self.termsendPushButton.setObjectName(u"termsendPushButton")
        font12 = QFont()
        font12.setPointSize(15)
        self.termsendPushButton.setFont(font12)
        self.termsendPushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	padding: 6px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	color: rgb(16, 42, 131);\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-color: rgb(16, 42, 131);\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"	background-color: rgb(172, 172, 172);\n"
"}")
        icon23 = QIcon()
        icon23.addFile(u":/icons/icons/arrow-right.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.termsendPushButton.setIcon(icon23)
        self.termsendPushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_31.addWidget(self.termsendPushButton)

        self.horizontalLayout_31.setStretch(0, 4)
        self.horizontalLayout_31.setStretch(1, 1)

        self.verticalLayout_29.addWidget(self.terminalsendFrame)


        self.verticalLayout_34.addWidget(self.terminalFrame)

        self.mainPages.addWidget(self.terminalPage)

        self.horizontalLayout_11.addWidget(self.mainPages)


        self.horizontalLayout_10.addWidget(self.mainContentContainer)


        self.verticalLayout_11.addWidget(self.mainBodyContent)

        self.notifySlideMenu = QCustomSlideMenu(self.mainBodyContainer)
        self.notifySlideMenu.setObjectName(u"notifySlideMenu")
        self.notifySlideMenu.setMaximumSize(QSize(16777215, 100))
        self.verticalLayout_12 = QVBoxLayout(self.notifySlideMenu)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.notifySubContainer = QWidget(self.notifySlideMenu)
        self.notifySubContainer.setObjectName(u"notifySubContainer")
        sizePolicy6.setHeightForWidth(self.notifySubContainer.sizePolicy().hasHeightForWidth())
        self.notifySubContainer.setSizePolicy(sizePolicy6)
        self.notifySubContainer.setMaximumSize(QSize(16777215, 150))
        self.verticalLayout_13 = QVBoxLayout(self.notifySubContainer)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(5, 5, 0, 0)
        self.notifyLabel = QLabel(self.notifySubContainer)
        self.notifyLabel.setObjectName(u"notifyLabel")
        self.notifyLabel.setFont(font11)

        self.verticalLayout_13.addWidget(self.notifyLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.frame = QFrame(self.notifySubContainer)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.notifyTextEdit = QTextEdit(self.frame)
        self.notifyTextEdit.setObjectName(u"notifyTextEdit")

        self.horizontalLayout_3.addWidget(self.notifyTextEdit)

        self.closeNotifyPushButton = QPushButton(self.frame)
        self.closeNotifyPushButton.setObjectName(u"closeNotifyPushButton")
        self.closeNotifyPushButton.setText(u"")
        icon24 = QIcon()
        icon24.addFile(u":/icons/icons/x-octagon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeNotifyPushButton.setIcon(icon24)
        self.closeNotifyPushButton.setIconSize(QSize(24, 24))
        self.closeNotifyPushButton.setCheckable(False)

        self.horizontalLayout_3.addWidget(self.closeNotifyPushButton)


        self.verticalLayout_13.addWidget(self.frame)


        self.verticalLayout_12.addWidget(self.notifySubContainer)


        self.verticalLayout_11.addWidget(self.notifySlideMenu)

        self.footerContainer = QWidget(self.mainBodyContainer)
        self.footerContainer.setObjectName(u"footerContainer")
        self.footerContainer.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_4 = QHBoxLayout(self.footerContainer)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.footerFrame = QFrame(self.footerContainer)
        self.footerFrame.setObjectName(u"footerFrame")
        self.footerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.footerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.footerFrame)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(9, 0, 9, 0)
        self.footerLabel = QLabel(self.footerFrame)
        self.footerLabel.setObjectName(u"footerLabel")
        sizePolicy6.setHeightForWidth(self.footerLabel.sizePolicy().hasHeightForWidth())
        self.footerLabel.setSizePolicy(sizePolicy6)
        self.footerLabel.setMinimumSize(QSize(0, 30))
        self.footerLabel.setMaximumSize(QSize(16777215, 16))
        self.footerLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.horizontalLayout_5.addWidget(self.footerLabel)


        self.horizontalLayout_4.addWidget(self.footerFrame)

        self.sizeGrip = QFrame(self.footerContainer)
        self.sizeGrip.setObjectName(u"sizeGrip")
        sizePolicy6.setHeightForWidth(self.sizeGrip.sizePolicy().hasHeightForWidth())
        self.sizeGrip.setSizePolicy(sizePolicy6)
        self.sizeGrip.setMaximumSize(QSize(40, 40))
        self.sizeGrip.setFrameShape(QFrame.Shape.StyledPanel)
        self.sizeGrip.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_4.addWidget(self.sizeGrip)


        self.verticalLayout_11.addWidget(self.footerContainer)

        self.verticalLayout_11.setStretch(2, 2)
        self.verticalLayout_11.setStretch(3, 1)

        self.horizontalLayout.addWidget(self.mainBodyContainer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.centerMenuPages.setCurrentIndex(0)
        self.infoSubPages.setCurrentIndex(0)
        self.mainPages.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menuPushButton.setText("")
        self.homePushButton.setText(QCoreApplication.translate("MainWindow", u" Home", None))
        self.laserPushButton.setText(QCoreApplication.translate("MainWindow", u"Lasers", None))
        self.programsPushButton.setText(QCoreApplication.translate("MainWindow", u" Programs", None))
        self.recipePushButton.setText(QCoreApplication.translate("MainWindow", u" Recipe", None))
        self.printPushButton.setText(QCoreApplication.translate("MainWindow", u" Print", None))
        self.cameraPushButton.setText(QCoreApplication.translate("MainWindow", u" Camera", None))
        self.cameraonoffoffsetPushButton.setText(QCoreApplication.translate("MainWindow", u" Camera Jog", None))
        self.terminalPushButton.setText(QCoreApplication.translate("MainWindow", u" Terminal", None))
        self.comPushButton.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.settingsPushButton.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.infoPushButton.setText(QCoreApplication.translate("MainWindow", u"Information", None))
        self.centerMenuLabel.setText(QCoreApplication.translate("MainWindow", u"Configuration", None))
        self.closeCenterMenuPushButton.setText("")
        self.comLabel.setText(QCoreApplication.translate("MainWindow", u"Communication", None))
        self.portLabel.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.baudLabel.setText(QCoreApplication.translate("MainWindow", u"Baud", None))
        self.mainconnectPushButton.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.mainrefreshPushButton.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.settingsLabel.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.indexLabel.setText(QCoreApplication.translate("MainWindow", u"Index Position :", None))
        self.feedLabel_2.setText(QCoreApplication.translate("MainWindow", u"Camera Offset:", None))
        self.cameraoffsetPushButton.setText(QCoreApplication.translate("MainWindow", u"ON", None))
        self.infoLabel.setText(QCoreApplication.translate("MainWindow", u"Information", None))
        self.aboutPushButton.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.helpPushButton.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.back1PushButton.setText("")
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.back2PushButton.setText("")
        self.profileLabel.setText(QCoreApplication.translate("MainWindow", u"Operator Profile", None))
        self.userLabel.setText(QCoreApplication.translate("MainWindow", u"Profile", None))
        self.passwordLabel.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.profilesetPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.logoLabel.setText("")
        self.profilePushButton.setText("")
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"LASER SCRIBING", None))
        self.notifyPushButton.setText("")
        self.minimizePushButton.setText("")
        self.restorePushButton.setText("")
        self.closePushButton.setText("")
        self.page1Label.setText(QCoreApplication.translate("MainWindow", u"JOG", None))
        self.homeLabel.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.xhomePushButton.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.yhomePushButton.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.zhomePushButton.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.allhomePushButton.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Steps", None))
        self.travel100_RadioButton.setText(QCoreApplication.translate("MainWindow", u"10 mm", None))
        self.travel50_RadioButton.setText(QCoreApplication.translate("MainWindow", u"5 mm", None))
        self.travel10_RadioButton.setText(QCoreApplication.translate("MainWindow", u"1 mm", None))
        self.travel1_RadioButton.setText(QCoreApplication.translate("MainWindow", u"0.1 mm", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"XY Axis", None))
        self.yplusPushButton.setText(QCoreApplication.translate("MainWindow", u"Y+", None))
        self.xminusPushButton.setText(QCoreApplication.translate("MainWindow", u"X-", None))
        self.xycenterPushButton.setText(QCoreApplication.translate("MainWindow", u"Center", None))
        self.xplusPushButton.setText(QCoreApplication.translate("MainWindow", u"X+", None))
        self.yminusPushButton.setText(QCoreApplication.translate("MainWindow", u"Y-", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Z Axis", None))
        self.zplusPushButton.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.zcenterPushButton.setText(QCoreApplication.translate("MainWindow", u"Z Center", None))
        self.zminusPushButton.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.page3Label_3.setText(QCoreApplication.translate("MainWindow", u"Laser Config", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"                                                                             Set Focus", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Object Height :", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Laser :", None))
        self.flaserPushButton.setText(QCoreApplication.translate("MainWindow", u"ON", None))
        self.fplusPushButton.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.fminusPushButton.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.fsetPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Laser Offset", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Laser :", None))
        self.offlaserPushButton.setText(QCoreApplication.translate("MainWindow", u"ON", None))
        self.offyplusPushButton.setText(QCoreApplication.translate("MainWindow", u"Y+", None))
        self.offxminusPushButton.setText(QCoreApplication.translate("MainWindow", u"X-", None))
        self.travelPushButton.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.offxplusPushButton.setText(QCoreApplication.translate("MainWindow", u"X+", None))
        self.offyminusPushButton.setText(QCoreApplication.translate("MainWindow", u"Y-", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"X:", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Y:", None))
        self.offzeroPushButton.setText(QCoreApplication.translate("MainWindow", u"ZERO", None))
        self.offsetPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.page2Label.setText(QCoreApplication.translate("MainWindow", u"PROGRAM", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Design File :", None))
        self.pgmfilePushButton.setText(QCoreApplication.translate("MainWindow", u"SELECT", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Sample Height :", None))
        self.pgmheightLineEdit.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.pgmheightPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Feedrate :", None))
        self.pgmfeedLineEdit.setText(QCoreApplication.translate("MainWindow", u"500", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"mm/min", None))
        self.pgmfeedPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Laser Selection :", None))
        self.pgmlaserPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Recipe File :", None))
        self.pgmsavePushButton.setText(QCoreApplication.translate("MainWindow", u"SAVE", None))
        self.page4Label.setText(QCoreApplication.translate("MainWindow", u"LOAD RECIPE", None))
        self.label_72.setText(QCoreApplication.translate("MainWindow", u"Recipe File :", None))
        self.rcpfilePushButton.setText(QCoreApplication.translate("MainWindow", u"SELECT", None))
        self.label_73.setText(QCoreApplication.translate("MainWindow", u"Sample Height :", None))
        self.rcpheightLineEdit.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_74.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_75.setText(QCoreApplication.translate("MainWindow", u"Feedrate :", None))
        self.rcpfeedLineEdit.setText(QCoreApplication.translate("MainWindow", u"500", None))
        self.label_76.setText(QCoreApplication.translate("MainWindow", u"mm/min", None))
        self.label_77.setText(QCoreApplication.translate("MainWindow", u"Laser Selection :", None))
        self.rcploadPushButton.setText(QCoreApplication.translate("MainWindow", u"LOAD", None))
        self.page3Label.setText(QCoreApplication.translate("MainWindow", u"PRINT", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Image Plot", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Operation", None))
        self.printrunPushButton.setText("")
        self.printpausePushButton.setText("")
        self.printabortPushButton.setText("")
        self.inspectionPushButton.setText("")
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Progress :", None))
        self.printProgressBar.setFormat("")
        self.progressLabel.setText(QCoreApplication.translate("MainWindow", u"0%", None))
        self.page3Label_4.setText(QCoreApplication.translate("MainWindow", u"CAMERA", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"   XY Offset", None))
        self.camoffxplusPushButton.setText(QCoreApplication.translate("MainWindow", u"X+", None))
        self.camoffxminusPushButton.setText(QCoreApplication.translate("MainWindow", u"X-", None))
        self.camoffyplusPushButton.setText(QCoreApplication.translate("MainWindow", u"Y+", None))
        self.camoffyminusPushButton.setText(QCoreApplication.translate("MainWindow", u"Y-", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u" Steps", None))
        self.camstep10_RadioButton.setText(QCoreApplication.translate("MainWindow", u"10 mm", None))
        self.camstep5_RadioButton.setText(QCoreApplication.translate("MainWindow", u"5 mm", None))
        self.camstep1_RadioButton.setText(QCoreApplication.translate("MainWindow", u"1 mm", None))
        self.camstep01_RadioButton.setText(QCoreApplication.translate("MainWindow", u"0.1 mm", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"    Z offset", None))
        self.camoffzplusPushButton.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.camoffzminusPushButton.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.camstartPushButton.setText(QCoreApplication.translate("MainWindow", u"START", None))
        self.campausePushButton.setText(QCoreApplication.translate("MainWindow", u"PAUSE", None))
        self.camstopPushButton.setText(QCoreApplication.translate("MainWindow", u"STOP", None))
        self.page3Label_2.setText(QCoreApplication.translate("MainWindow", u"TERMINAL", None))
        self.termsendPushButton.setText("")
        self.notifyLabel.setText(QCoreApplication.translate("MainWindow", u"Notification", None))
        self.notifyTextEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Notification Message</p></body></html>", None))
        self.footerLabel.setText(QCoreApplication.translate("MainWindow", u"Copyright Specialize Products Pvt. Ltd.", None))
    # retranslateUi

