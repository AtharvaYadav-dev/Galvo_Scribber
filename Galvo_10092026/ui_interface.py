# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interfacecPxrse.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QHBoxLayout, QLCDNumber, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSlider, QSpacerItem,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget)

from Custom_Widgets.QCustomSlideMenu import QCustomSlideMenu
from Custom_Widgets.Widgets import QCustomStackedWidget
import resources_rc
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
"#jogFrame, #laserconfFrame, #programFrame, #printFrame, #terminalFrame, #cameraFrame, #joggalvoFrame, #axisposgalvoFrame, #galvolaserconfFrame, #programgalvoFrame, #printgalvoFrame, #configgalveFrame, #ezcadFrame {\n"
"	background-color: rgb(167, 198, 229);\n"
"	border-radius: 20px;\n"
"}\n"
"\n"
"#homeFrame, #stepsFrame, #xyFrame, #zFrame, #axisposFrame, #setfocusFrame, #flaserFrame, #zfocusFrame, #fsetFrame, #loffsetFrame, #offlaserFrame, #xyoffsetFrame, #xyposFrame, #offsetFrame, #offbtnFrame, #progFrame, #printimgFrame, #printopFrame, #printprogramFrame, #printprogressFrame, #camFrame, #cameraxyoffFrame, #objheightFrame, #axisposgalvoFrame, #testpatterngalvoFrame, #zgalvoFrame, #homegalvoFrame,  #pgmgalvoFrame, #printprogressgalvoFrame, #printimggalvoFrame, #printopgalvoFrame, #fsetgalvoFrame, #zfocusgalvoFrame, #objheightlasrFrame, #goposgalvoFrame, #galvo1Frame, #galvo2Frame, #as"
                        "pectgalvoFrame, #powerFrame, #ez1Frame, #ez2Frame, #ez3Frame, #ez4Frame{\n"
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
        self.verticalLayout_5 = QVBoxLayout(self.leftMenuSubContainer)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.topFrame = QFrame(self.leftMenuSubContainer)
        self.topFrame.setObjectName(u"topFrame")
        self.topFrame.setMinimumSize(QSize(0, 36))
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


        self.verticalLayout_5.addWidget(self.topFrame, 0, Qt.AlignmentFlag.AlignTop)

        self.middleFrame = QFrame(self.leftMenuSubContainer)
        self.middleFrame.setObjectName(u"middleFrame")
        self.middleFrame.setMinimumSize(QSize(0, 120))
        self.middleFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.middleFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_3 = QVBoxLayout(self.middleFrame)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
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

        self.verticalLayout_3.addWidget(self.homePushButton)

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

        self.verticalLayout_3.addWidget(self.laserPushButton)

        self.programsPushButton = QPushButton(self.middleFrame)
        self.programsPushButton.setObjectName(u"programsPushButton")
        self.programsPushButton.setMinimumSize(QSize(0, 34))
        self.programsPushButton.setFont(font)
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons/list.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.programsPushButton.setIcon(icon3)
        self.programsPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.programsPushButton)

        self.printPushButton = QPushButton(self.middleFrame)
        self.printPushButton.setObjectName(u"printPushButton")
        self.printPushButton.setMinimumSize(QSize(0, 34))
        self.printPushButton.setFont(font)
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons/printer.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.printPushButton.setIcon(icon4)
        self.printPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.printPushButton)

        self.cameraPushButton = QPushButton(self.middleFrame)
        self.cameraPushButton.setObjectName(u"cameraPushButton")
        self.cameraPushButton.setMinimumSize(QSize(0, 34))
        self.cameraPushButton.setFont(font)
        icon5 = QIcon()
        icon5.addFile(u":/icons/icons/camera.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cameraPushButton.setIcon(icon5)
        self.cameraPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.cameraPushButton)

        self.cameraonoffoffsetPushButton = QPushButton(self.middleFrame)
        self.cameraonoffoffsetPushButton.setObjectName(u"cameraonoffoffsetPushButton")
        self.cameraonoffoffsetPushButton.setMinimumSize(QSize(0, 34))
        self.cameraonoffoffsetPushButton.setFont(font)
        icon6 = QIcon()
        icon6.addFile(u":/icons/icons/eye.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cameraonoffoffsetPushButton.setIcon(icon6)
        self.cameraonoffoffsetPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.cameraonoffoffsetPushButton)

        self.joggalvoPushButton = QPushButton(self.middleFrame)
        self.joggalvoPushButton.setObjectName(u"joggalvoPushButton")
        self.joggalvoPushButton.setMinimumSize(QSize(0, 34))
        self.joggalvoPushButton.setFont(font)
        self.joggalvoPushButton.setIcon(icon1)
        self.joggalvoPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.joggalvoPushButton)

        self.laserconfgalvoPushButton = QPushButton(self.middleFrame)
        self.laserconfgalvoPushButton.setObjectName(u"laserconfgalvoPushButton")
        self.laserconfgalvoPushButton.setMinimumSize(QSize(0, 34))
        self.laserconfgalvoPushButton.setFont(font1)
        self.laserconfgalvoPushButton.setIcon(icon2)
        self.laserconfgalvoPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.laserconfgalvoPushButton)

        self.programsgalvoPushButton = QPushButton(self.middleFrame)
        self.programsgalvoPushButton.setObjectName(u"programsgalvoPushButton")
        self.programsgalvoPushButton.setMinimumSize(QSize(0, 34))
        self.programsgalvoPushButton.setFont(font)
        self.programsgalvoPushButton.setIcon(icon3)
        self.programsgalvoPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.programsgalvoPushButton)

        self.printgalvoPushButton = QPushButton(self.middleFrame)
        self.printgalvoPushButton.setObjectName(u"printgalvoPushButton")
        self.printgalvoPushButton.setMinimumSize(QSize(0, 34))
        self.printgalvoPushButton.setFont(font)
        self.printgalvoPushButton.setIcon(icon4)
        self.printgalvoPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.printgalvoPushButton)

        self.terminalPushButton = QPushButton(self.middleFrame)
        self.terminalPushButton.setObjectName(u"terminalPushButton")
        self.terminalPushButton.setMinimumSize(QSize(0, 34))
        self.terminalPushButton.setFont(font)
        icon7 = QIcon()
        icon7.addFile(u":/icons/icons/monitor.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.terminalPushButton.setIcon(icon7)
        self.terminalPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.terminalPushButton)


        self.verticalLayout_5.addWidget(self.middleFrame, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

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
        icon8 = QIcon()
        icon8.addFile(u":/icons/icons/link.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.comPushButton.setIcon(icon8)
        self.comPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.comPushButton)

        self.settingsPushButton = QPushButton(self.bottomFrame)
        self.settingsPushButton.setObjectName(u"settingsPushButton")
        self.settingsPushButton.setMinimumSize(QSize(0, 34))
        self.settingsPushButton.setFont(font)
        icon9 = QIcon()
        icon9.addFile(u":/icons/icons/settings.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settingsPushButton.setIcon(icon9)
        self.settingsPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.settingsPushButton)

        self.infoPushButton = QPushButton(self.bottomFrame)
        self.infoPushButton.setObjectName(u"infoPushButton")
        self.infoPushButton.setMinimumSize(QSize(0, 34))
        self.infoPushButton.setFont(font)
        icon10 = QIcon()
        icon10.addFile(u":/icons/icons/info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.infoPushButton.setIcon(icon10)
        self.infoPushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.infoPushButton)


        self.verticalLayout_5.addWidget(self.bottomFrame, 0, Qt.AlignmentFlag.AlignBottom)


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
        icon11 = QIcon()
        icon11.addFile(u":/icons/icons/x-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeCenterMenuPushButton.setIcon(icon11)
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
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(-1, 0, -1, -1)
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

        self.mainconnectgalvoPushButton = QPushButton(self.comFrame)
        self.mainconnectgalvoPushButton.setObjectName(u"mainconnectgalvoPushButton")
        sizePolicy3.setHeightForWidth(self.mainconnectgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.mainconnectgalvoPushButton.setSizePolicy(sizePolicy3)
        self.mainconnectgalvoPushButton.setMinimumSize(QSize(0, 40))
        self.mainconnectgalvoPushButton.setMaximumSize(QSize(16777215, 60))
        self.mainconnectgalvoPushButton.setFont(font2)
        self.mainconnectgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_19.addWidget(self.mainconnectgalvoPushButton)

        self.maindisconnectgalvoPushButton = QPushButton(self.comFrame)
        self.maindisconnectgalvoPushButton.setObjectName(u"maindisconnectgalvoPushButton")
        sizePolicy3.setHeightForWidth(self.maindisconnectgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.maindisconnectgalvoPushButton.setSizePolicy(sizePolicy3)
        self.maindisconnectgalvoPushButton.setMinimumSize(QSize(0, 40))
        self.maindisconnectgalvoPushButton.setMaximumSize(QSize(16777215, 60))
        self.maindisconnectgalvoPushButton.setFont(font2)
        self.maindisconnectgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_19.addWidget(self.maindisconnectgalvoPushButton)


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
        self.verticalLayout_94 = QVBoxLayout(self.widget)
        self.verticalLayout_94.setSpacing(0)
        self.verticalLayout_94.setObjectName(u"verticalLayout_94")
        self.verticalLayout_94.setContentsMargins(0, 0, 0, 0)
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


        self.verticalLayout_94.addWidget(self.indexFrame)

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


        self.verticalLayout_94.addWidget(self.machinesetFrame)

        self.machinesetFrame_2 = QFrame(self.widget)
        self.machinesetFrame_2.setObjectName(u"machinesetFrame_2")
        self.verticalLayout_45 = QVBoxLayout(self.machinesetFrame_2)
        self.verticalLayout_45.setObjectName(u"verticalLayout_45")
        self.setconfigPushButton = QPushButton(self.machinesetFrame_2)
        self.setconfigPushButton.setObjectName(u"setconfigPushButton")
        self.setconfigPushButton.setFont(font5)
        self.setconfigPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_45.addWidget(self.setconfigPushButton)


        self.verticalLayout_94.addWidget(self.machinesetFrame_2)

        self.machinesetFrame_3 = QFrame(self.widget)
        self.machinesetFrame_3.setObjectName(u"machinesetFrame_3")
        self.verticalLayout_75 = QVBoxLayout(self.machinesetFrame_3)
        self.verticalLayout_75.setObjectName(u"verticalLayout_75")
        self.verticalLayout_75.setContentsMargins(-1, 9, -1, -1)
        self.setadvancalPushButton = QPushButton(self.machinesetFrame_3)
        self.setadvancalPushButton.setObjectName(u"setadvancalPushButton")
        self.setadvancalPushButton.setFont(font5)
        self.setadvancalPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_75.addWidget(self.setadvancalPushButton)


        self.verticalLayout_94.addWidget(self.machinesetFrame_3)


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
        self.aboutPushButton.setIcon(icon10)
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
        icon12 = QIcon()
        icon12.addFile(u":/icons/icons/help-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.helpPushButton.setIcon(icon12)
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
        icon13 = QIcon()
        icon13.addFile(u":/icons/icons/arrow-left.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.back1PushButton.setIcon(icon13)
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
        self.back2PushButton.setIcon(icon13)
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
        icon14 = QIcon()
        icon14.addFile(u":/icons/icons/user.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.profilePushButton.setIcon(icon14)
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
        icon15 = QIcon()
        icon15.addFile(u":/icons/icons/bell.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.notifyPushButton.setIcon(icon15)
        self.notifyPushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.notifyPushButton)

        self.minimizePushButton = QPushButton(self.windowFrame)
        self.minimizePushButton.setObjectName(u"minimizePushButton")
        icon16 = QIcon()
        icon16.addFile(u":/icons/icons/minus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizePushButton.setIcon(icon16)
        self.minimizePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.minimizePushButton)

        self.restorePushButton = QPushButton(self.windowFrame)
        self.restorePushButton.setObjectName(u"restorePushButton")
        icon17 = QIcon()
        icon17.addFile(u":/icons/icons/square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.restorePushButton.setIcon(icon17)
        self.restorePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_7.addWidget(self.restorePushButton)

        self.closePushButton = QPushButton(self.windowFrame)
        self.closePushButton.setObjectName(u"closePushButton")
        icon18 = QIcon()
        icon18.addFile(u":/icons/icons/x.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closePushButton.setIcon(icon18)
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
        self.horizontalLayout_49 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_49.setObjectName(u"horizontalLayout_49")
        self.horizontalLayout_49.setContentsMargins(0, 0, 0, 0)
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


        self.horizontalLayout_49.addWidget(self.objheightFrame)

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

        self.horizontalLayout_49.addWidget(self.flaserFrame)

        self.zfocusFrame = QFrame(self.widget_5)
        self.zfocusFrame.setObjectName(u"zfocusFrame")
        self.zfocusFrame.setStyleSheet(u"")
        self.zfocusFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.zfocusFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_48 = QHBoxLayout(self.zfocusFrame)
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.horizontalLayout_48.setContentsMargins(9, -1, 9, -1)
        self.frame_3 = QFrame(self.zfocusFrame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.fplusPushButton = QPushButton(self.frame_3)
        self.fplusPushButton.setObjectName(u"fplusPushButton")
        sizePolicy6.setHeightForWidth(self.fplusPushButton.sizePolicy().hasHeightForWidth())
        self.fplusPushButton.setSizePolicy(sizePolicy6)
        self.fplusPushButton.setMinimumSize(QSize(0, 0))
        self.fplusPushButton.setMaximumSize(QSize(16777215, 16777215))
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

        self.verticalLayout_8.addWidget(self.fplusPushButton)

        self.ftravelPushButton = QPushButton(self.frame_3)
        self.ftravelPushButton.setObjectName(u"ftravelPushButton")
        sizePolicy6.setHeightForWidth(self.ftravelPushButton.sizePolicy().hasHeightForWidth())
        self.ftravelPushButton.setSizePolicy(sizePolicy6)
        self.ftravelPushButton.setMinimumSize(QSize(0, 0))
        self.ftravelPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.ftravelPushButton.setFont(font2)
        self.ftravelPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_8.addWidget(self.ftravelPushButton)

        self.fminusPushButton = QPushButton(self.frame_3)
        self.fminusPushButton.setObjectName(u"fminusPushButton")
        sizePolicy6.setHeightForWidth(self.fminusPushButton.sizePolicy().hasHeightForWidth())
        self.fminusPushButton.setSizePolicy(sizePolicy6)
        self.fminusPushButton.setMinimumSize(QSize(0, 0))
        self.fminusPushButton.setMaximumSize(QSize(16777215, 16777215))
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

        self.verticalLayout_8.addWidget(self.fminusPushButton)


        self.horizontalLayout_48.addWidget(self.frame_3)


        self.horizontalLayout_49.addWidget(self.zfocusFrame)

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

        self.horizontalLayout_49.addWidget(self.fsetFrame)


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
        self.pgmfileTextEdit.setMaximumSize(QSize(16777215, 70))
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

        self.horizontalLayout_32.setStretch(0, 2)
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

        self.horizontalLayout_24.setStretch(0, 1)
        self.horizontalLayout_24.setStretch(1, 5)

        self.verticalLayout_28.addWidget(self.widget_3)

        self.widget_4 = QWidget(self.progFrame)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_41 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.horizontalLayout_41.setContentsMargins(-1, -1, 0, -1)
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
        self.pgmfeedLineEdit.setMaximumSize(QSize(16777215, 100))
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

        self.horizontalLayout_41.setStretch(0, 3)
        self.horizontalLayout_41.setStretch(1, 5)

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

        self.horizontalLayout_23.setStretch(0, 1)
        self.horizontalLayout_23.setStretch(1, 2)

        self.verticalLayout_28.addWidget(self.widget_2)

        self.widget_11 = QWidget(self.progFrame)
        self.widget_11.setObjectName(u"widget_11")
        self.horizontalLayout_26 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_26.setSpacing(9)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalSpacer_5 = QSpacerItem(366, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_5)

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

        self.horizontalLayout_26.setStretch(0, 5)
        self.horizontalLayout_26.setStretch(1, 2)

        self.verticalLayout_28.addWidget(self.widget_11)


        self.verticalLayout_27.addWidget(self.progFrame)


        self.verticalLayout_16.addWidget(self.programFrame)

        self.mainPages.addWidget(self.programPage)
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
        icon19 = QIcon()
        icon19.addFile(u":/icons/icons/play.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.printrunPushButton.setIcon(icon19)
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
        icon20 = QIcon()
        icon20.addFile(u":/icons/icons/pause.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.printpausePushButton.setIcon(icon20)
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
        self.printabortPushButton.setIcon(icon17)
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
        icon21 = QIcon()
        icon21.addFile(u":/icons/icons/search.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.inspectionPushButton.setIcon(icon21)
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
        self.joggalvoPage = QWidget()
        self.joggalvoPage.setObjectName(u"joggalvoPage")
        self.verticalLayout_102 = QVBoxLayout(self.joggalvoPage)
        self.verticalLayout_102.setObjectName(u"verticalLayout_102")
        self.page1Label_3 = QLabel(self.joggalvoPage)
        self.page1Label_3.setObjectName(u"page1Label_3")
        self.page1Label_3.setMinimumSize(QSize(0, 20))
        self.page1Label_3.setMaximumSize(QSize(16777215, 20))
        self.page1Label_3.setFont(font2)
        self.page1Label_3.setFrameShadow(QFrame.Shadow.Raised)
        self.page1Label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_102.addWidget(self.page1Label_3)

        self.joggalvoFrame = QFrame(self.joggalvoPage)
        self.joggalvoFrame.setObjectName(u"joggalvoFrame")
        self.joggalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.joggalvoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_97 = QVBoxLayout(self.joggalvoFrame)
        self.verticalLayout_97.setObjectName(u"verticalLayout_97")
        self.axisposgalvoFrame = QFrame(self.joggalvoFrame)
        self.axisposgalvoFrame.setObjectName(u"axisposgalvoFrame")
        self.axisposgalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.axisposgalvoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_86 = QHBoxLayout(self.axisposgalvoFrame)
        self.horizontalLayout_86.setObjectName(u"horizontalLayout_86")
        self.xposgalvoLCDNumber = QLCDNumber(self.axisposgalvoFrame)
        self.xposgalvoLCDNumber.setObjectName(u"xposgalvoLCDNumber")
        self.xposgalvoLCDNumber.setFont(font7)
        self.xposgalvoLCDNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.xposgalvoLCDNumber.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_86.addWidget(self.xposgalvoLCDNumber)

        self.yposgalvoLCDNumber = QLCDNumber(self.axisposgalvoFrame)
        self.yposgalvoLCDNumber.setObjectName(u"yposgalvoLCDNumber")
        self.yposgalvoLCDNumber.setFont(font7)
        self.yposgalvoLCDNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.yposgalvoLCDNumber.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_86.addWidget(self.yposgalvoLCDNumber)

        self.zposgalvoLCDNumber = QLCDNumber(self.axisposgalvoFrame)
        self.zposgalvoLCDNumber.setObjectName(u"zposgalvoLCDNumber")
        self.zposgalvoLCDNumber.setFont(font7)
        self.zposgalvoLCDNumber.setFrameShape(QFrame.Shape.NoFrame)
        self.zposgalvoLCDNumber.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_86.addWidget(self.zposgalvoLCDNumber)


        self.verticalLayout_97.addWidget(self.axisposgalvoFrame)

        self.frame_32 = QFrame(self.joggalvoFrame)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_32.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_90 = QHBoxLayout(self.frame_32)
        self.horizontalLayout_90.setObjectName(u"horizontalLayout_90")
        self.horizontalLayout_90.setContentsMargins(0, 0, 0, 0)
        self.homegalvoFrame = QFrame(self.frame_32)
        self.homegalvoFrame.setObjectName(u"homegalvoFrame")
        self.homegalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.homegalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_77 = QVBoxLayout(self.homegalvoFrame)
        self.verticalLayout_77.setObjectName(u"verticalLayout_77")
        self.homeLabel_3 = QLabel(self.homegalvoFrame)
        self.homeLabel_3.setObjectName(u"homeLabel_3")
        self.homeLabel_3.setMinimumSize(QSize(0, 20))
        self.homeLabel_3.setMaximumSize(QSize(16777215, 16777215))
        self.homeLabel_3.setFont(font5)
        self.homeLabel_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_77.addWidget(self.homeLabel_3)

        self.frame_41 = QFrame(self.homegalvoFrame)
        self.frame_41.setObjectName(u"frame_41")
        self.frame_41.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_41.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_76 = QVBoxLayout(self.frame_41)
        self.verticalLayout_76.setObjectName(u"verticalLayout_76")
        self.galvohomePushButton = QPushButton(self.frame_41)
        self.galvohomePushButton.setObjectName(u"galvohomePushButton")
        sizePolicy5.setHeightForWidth(self.galvohomePushButton.sizePolicy().hasHeightForWidth())
        self.galvohomePushButton.setSizePolicy(sizePolicy5)
        self.galvohomePushButton.setMinimumSize(QSize(0, 0))
        self.galvohomePushButton.setMaximumSize(QSize(16777215, 70))
        font12 = QFont()
        font12.setPointSize(9)
        font12.setBold(True)
        self.galvohomePushButton.setFont(font12)
        self.galvohomePushButton.setStyleSheet(u"QPushButton {\n"
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
        self.galvohomePushButton.setIcon(icon1)
        self.galvohomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_76.addWidget(self.galvohomePushButton)

        self.galvozhomePushButton = QPushButton(self.frame_41)
        self.galvozhomePushButton.setObjectName(u"galvozhomePushButton")
        sizePolicy5.setHeightForWidth(self.galvozhomePushButton.sizePolicy().hasHeightForWidth())
        self.galvozhomePushButton.setSizePolicy(sizePolicy5)
        self.galvozhomePushButton.setMinimumSize(QSize(0, 0))
        self.galvozhomePushButton.setMaximumSize(QSize(16777215, 70))
        self.galvozhomePushButton.setFont(font2)
        self.galvozhomePushButton.setStyleSheet(u"QPushButton {\n"
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
        self.galvozhomePushButton.setIcon(icon1)
        self.galvozhomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_76.addWidget(self.galvozhomePushButton)

        self.galvoallhomePushButton = QPushButton(self.frame_41)
        self.galvoallhomePushButton.setObjectName(u"galvoallhomePushButton")
        sizePolicy5.setHeightForWidth(self.galvoallhomePushButton.sizePolicy().hasHeightForWidth())
        self.galvoallhomePushButton.setSizePolicy(sizePolicy5)
        self.galvoallhomePushButton.setMinimumSize(QSize(0, 0))
        self.galvoallhomePushButton.setMaximumSize(QSize(16777215, 70))
        self.galvoallhomePushButton.setFont(font5)
        self.galvoallhomePushButton.setStyleSheet(u"QPushButton {\n"
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
        self.galvoallhomePushButton.setIcon(icon1)
        self.galvoallhomePushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_76.addWidget(self.galvoallhomePushButton)


        self.verticalLayout_77.addWidget(self.frame_41)

        self.verticalLayout_77.setStretch(0, 2)
        self.verticalLayout_77.setStretch(1, 6)

        self.horizontalLayout_90.addWidget(self.homegalvoFrame)

        self.jogSubFrame_3 = QFrame(self.frame_32)
        self.jogSubFrame_3.setObjectName(u"jogSubFrame_3")
        self.jogSubFrame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.jogSubFrame_3.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_96 = QVBoxLayout(self.jogSubFrame_3)
        self.verticalLayout_96.setObjectName(u"verticalLayout_96")
        self.verticalLayout_96.setContentsMargins(0, 0, 0, 0)
        self.testpatterngalvoFrame = QFrame(self.jogSubFrame_3)
        self.testpatterngalvoFrame.setObjectName(u"testpatterngalvoFrame")
        self.testpatterngalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.testpatterngalvoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_99 = QVBoxLayout(self.testpatterngalvoFrame)
        self.verticalLayout_99.setObjectName(u"verticalLayout_99")
        self.verticalLayout_99.setContentsMargins(-1, 0, -1, -1)
        self.label_50 = QLabel(self.testpatterngalvoFrame)
        self.label_50.setObjectName(u"label_50")
        sizePolicy3.setHeightForWidth(self.label_50.sizePolicy().hasHeightForWidth())
        self.label_50.setSizePolicy(sizePolicy3)
        self.label_50.setMinimumSize(QSize(0, 20))
        self.label_50.setMaximumSize(QSize(16777215, 0))
        self.label_50.setFont(font5)
        self.label_50.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_99.addWidget(self.label_50, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.frame_33 = QFrame(self.testpatterngalvoFrame)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_33.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_87 = QHBoxLayout(self.frame_33)
        self.horizontalLayout_87.setObjectName(u"horizontalLayout_87")
        self.circlePushButton = QPushButton(self.frame_33)
        self.circlePushButton.setObjectName(u"circlePushButton")
        sizePolicy5.setHeightForWidth(self.circlePushButton.sizePolicy().hasHeightForWidth())
        self.circlePushButton.setSizePolicy(sizePolicy5)
        self.circlePushButton.setMinimumSize(QSize(0, 0))
        self.circlePushButton.setMaximumSize(QSize(16777215, 16777215))
        self.circlePushButton.setFont(font2)
        self.circlePushButton.setStyleSheet(u"QPushButton {\n"
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
        icon22 = QIcon()
        icon22.addFile(u":/icons/icons/circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.circlePushButton.setIcon(icon22)
        self.circlePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_87.addWidget(self.circlePushButton)

        self.trianglePushButton = QPushButton(self.frame_33)
        self.trianglePushButton.setObjectName(u"trianglePushButton")
        sizePolicy5.setHeightForWidth(self.trianglePushButton.sizePolicy().hasHeightForWidth())
        self.trianglePushButton.setSizePolicy(sizePolicy5)
        self.trianglePushButton.setMinimumSize(QSize(0, 0))
        self.trianglePushButton.setMaximumSize(QSize(16777215, 16777215))
        self.trianglePushButton.setFont(font2)
        self.trianglePushButton.setStyleSheet(u"QPushButton {\n"
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
        icon23 = QIcon()
        icon23.addFile(u":/icons/icons/triangle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.trianglePushButton.setIcon(icon23)
        self.trianglePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_87.addWidget(self.trianglePushButton)

        self.squarePushButton = QPushButton(self.frame_33)
        self.squarePushButton.setObjectName(u"squarePushButton")
        sizePolicy5.setHeightForWidth(self.squarePushButton.sizePolicy().hasHeightForWidth())
        self.squarePushButton.setSizePolicy(sizePolicy5)
        self.squarePushButton.setMinimumSize(QSize(0, 0))
        self.squarePushButton.setMaximumSize(QSize(16777215, 16777215))
        self.squarePushButton.setFont(font2)
        self.squarePushButton.setStyleSheet(u"QPushButton {\n"
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
        self.squarePushButton.setIcon(icon17)
        self.squarePushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_87.addWidget(self.squarePushButton)


        self.verticalLayout_99.addWidget(self.frame_33)


        self.verticalLayout_96.addWidget(self.testpatterngalvoFrame)

        self.zgalvoFrame = QFrame(self.jogSubFrame_3)
        self.zgalvoFrame.setObjectName(u"zgalvoFrame")
        self.zgalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.zgalvoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_100 = QVBoxLayout(self.zgalvoFrame)
        self.verticalLayout_100.setObjectName(u"verticalLayout_100")
        self.verticalLayout_100.setContentsMargins(-1, 0, -1, -1)
        self.label_49 = QLabel(self.zgalvoFrame)
        self.label_49.setObjectName(u"label_49")
        sizePolicy3.setHeightForWidth(self.label_49.sizePolicy().hasHeightForWidth())
        self.label_49.setSizePolicy(sizePolicy3)
        self.label_49.setMinimumSize(QSize(0, 20))
        self.label_49.setMaximumSize(QSize(16777215, 0))
        self.label_49.setFont(font5)
        self.label_49.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_100.addWidget(self.label_49, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.frame_34 = QFrame(self.zgalvoFrame)
        self.frame_34.setObjectName(u"frame_34")
        self.frame_34.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_34.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_88 = QHBoxLayout(self.frame_34)
        self.horizontalLayout_88.setObjectName(u"horizontalLayout_88")
        self.zplusgalvoPushButton = QPushButton(self.frame_34)
        self.zplusgalvoPushButton.setObjectName(u"zplusgalvoPushButton")
        sizePolicy5.setHeightForWidth(self.zplusgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.zplusgalvoPushButton.setSizePolicy(sizePolicy5)
        self.zplusgalvoPushButton.setMinimumSize(QSize(0, 0))
        self.zplusgalvoPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.zplusgalvoPushButton.setFont(font2)
        self.zplusgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_88.addWidget(self.zplusgalvoPushButton)

        self.ztravelPushButton = QPushButton(self.frame_34)
        self.ztravelPushButton.setObjectName(u"ztravelPushButton")
        sizePolicy5.setHeightForWidth(self.ztravelPushButton.sizePolicy().hasHeightForWidth())
        self.ztravelPushButton.setSizePolicy(sizePolicy5)
        self.ztravelPushButton.setMinimumSize(QSize(0, 0))
        self.ztravelPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.ztravelPushButton.setFont(font2)
        self.ztravelPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_88.addWidget(self.ztravelPushButton)

        self.zminusgalvoPushButton = QPushButton(self.frame_34)
        self.zminusgalvoPushButton.setObjectName(u"zminusgalvoPushButton")
        sizePolicy5.setHeightForWidth(self.zminusgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.zminusgalvoPushButton.setSizePolicy(sizePolicy5)
        self.zminusgalvoPushButton.setMinimumSize(QSize(0, 0))
        self.zminusgalvoPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.zminusgalvoPushButton.setFont(font2)
        self.zminusgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_88.addWidget(self.zminusgalvoPushButton)


        self.verticalLayout_100.addWidget(self.frame_34)


        self.verticalLayout_96.addWidget(self.zgalvoFrame)


        self.horizontalLayout_90.addWidget(self.jogSubFrame_3)

        self.horizontalLayout_90.setStretch(0, 4)
        self.horizontalLayout_90.setStretch(1, 9)

        self.verticalLayout_97.addWidget(self.frame_32)

        self.verticalLayout_97.setStretch(0, 3)
        self.verticalLayout_97.setStretch(1, 7)

        self.verticalLayout_102.addWidget(self.joggalvoFrame)

        self.mainPages.addWidget(self.joggalvoPage)
        self.laserconfgalvoPage = QWidget()
        self.laserconfgalvoPage.setObjectName(u"laserconfgalvoPage")
        self.verticalLayout_73 = QVBoxLayout(self.laserconfgalvoPage)
        self.verticalLayout_73.setObjectName(u"verticalLayout_73")
        self.page3Label_5 = QLabel(self.laserconfgalvoPage)
        self.page3Label_5.setObjectName(u"page3Label_5")
        self.page3Label_5.setMinimumSize(QSize(0, 30))
        self.page3Label_5.setMaximumSize(QSize(16777215, 30))
        self.page3Label_5.setFont(font2)
        self.page3Label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_73.addWidget(self.page3Label_5)

        self.galvolaserconfFrame = QFrame(self.laserconfgalvoPage)
        self.galvolaserconfFrame.setObjectName(u"galvolaserconfFrame")
        self.verticalLayout_40 = QVBoxLayout(self.galvolaserconfFrame)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.galvosetfocusFrame = QFrame(self.galvolaserconfFrame)
        self.galvosetfocusFrame.setObjectName(u"galvosetfocusFrame")
        self.galvosetfocusFrame.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")
        self.galvosetfocusFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.galvosetfocusFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_87 = QVBoxLayout(self.galvosetfocusFrame)
        self.verticalLayout_87.setObjectName(u"verticalLayout_87")
        self.label_25 = QLabel(self.galvosetfocusFrame)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setFont(font5)

        self.verticalLayout_87.addWidget(self.label_25, 0, Qt.AlignmentFlag.AlignHCenter)

        self.widget_12 = QWidget(self.galvosetfocusFrame)
        self.widget_12.setObjectName(u"widget_12")
        self.horizontalLayout_53 = QHBoxLayout(self.widget_12)
        self.horizontalLayout_53.setObjectName(u"horizontalLayout_53")
        self.horizontalLayout_53.setContentsMargins(0, 0, 0, 0)
        self.objheightlasrFrame = QFrame(self.widget_12)
        self.objheightlasrFrame.setObjectName(u"objheightlasrFrame")
        self.objheightlasrFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.objheightlasrFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_63 = QVBoxLayout(self.objheightlasrFrame)
        self.verticalLayout_63.setObjectName(u"verticalLayout_63")
        self.objheightFrame_2 = QFrame(self.objheightlasrFrame)
        self.objheightFrame_2.setObjectName(u"objheightFrame_2")
        self.objheightFrame_2.setStyleSheet(u"")
        self.objheightFrame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.objheightFrame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_50 = QHBoxLayout(self.objheightFrame_2)
        self.horizontalLayout_50.setObjectName(u"horizontalLayout_50")
        self.horizontalLayout_50.setContentsMargins(0, 0, 0, 0)
        self.label_26 = QLabel(self.objheightFrame_2)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setMinimumSize(QSize(0, 0))
        self.label_26.setMaximumSize(QSize(140, 16777215))
        self.label_26.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")
        self.label_26.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_50.addWidget(self.label_26, 0, Qt.AlignmentFlag.AlignLeft)

        self.galvoobjheightLineEdit = QLineEdit(self.objheightFrame_2)
        self.galvoobjheightLineEdit.setObjectName(u"galvoobjheightLineEdit")
        sizePolicy3.setHeightForWidth(self.galvoobjheightLineEdit.sizePolicy().hasHeightForWidth())
        self.galvoobjheightLineEdit.setSizePolicy(sizePolicy3)
        self.galvoobjheightLineEdit.setMinimumSize(QSize(0, 0))
        self.galvoobjheightLineEdit.setMaximumSize(QSize(120, 50))
        self.galvoobjheightLineEdit.setFont(font5)
        self.galvoobjheightLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.galvoobjheightLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_50.addWidget(self.galvoobjheightLineEdit)


        self.verticalLayout_63.addWidget(self.objheightFrame_2)

        self.widget_13 = QWidget(self.objheightlasrFrame)
        self.widget_13.setObjectName(u"widget_13")
        sizePolicy6.setHeightForWidth(self.widget_13.sizePolicy().hasHeightForWidth())
        self.widget_13.setSizePolicy(sizePolicy6)
        self.widget_13.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_52 = QHBoxLayout(self.widget_13)
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.horizontalLayout_52.setContentsMargins(0, -1, -1, -1)
        self.label_27 = QLabel(self.widget_13)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setMaximumSize(QSize(90, 16777215))
        self.label_27.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")

        self.horizontalLayout_52.addWidget(self.label_27, 0, Qt.AlignmentFlag.AlignLeft)

        self.flasergalvoPushButton = QPushButton(self.widget_13)
        self.flasergalvoPushButton.setObjectName(u"flasergalvoPushButton")
        self.flasergalvoPushButton.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.flasergalvoPushButton.sizePolicy().hasHeightForWidth())
        self.flasergalvoPushButton.setSizePolicy(sizePolicy6)
        self.flasergalvoPushButton.setMinimumSize(QSize(0, 0))
        self.flasergalvoPushButton.setMaximumSize(QSize(16777215, 50))
        self.flasergalvoPushButton.setBaseSize(QSize(0, 0))
        self.flasergalvoPushButton.setFont(font2)
        self.flasergalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_52.addWidget(self.flasergalvoPushButton)

        self.horizontalLayout_52.setStretch(0, 3)
        self.horizontalLayout_52.setStretch(1, 3)

        self.verticalLayout_63.addWidget(self.widget_13)

        self.widget_14 = QWidget(self.objheightlasrFrame)
        self.widget_14.setObjectName(u"widget_14")
        sizePolicy6.setHeightForWidth(self.widget_14.sizePolicy().hasHeightForWidth())
        self.widget_14.setSizePolicy(sizePolicy6)
        self.widget_14.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_126 = QHBoxLayout(self.widget_14)
        self.horizontalLayout_126.setObjectName(u"horizontalLayout_126")
        self.horizontalLayout_126.setContentsMargins(0, -1, -1, -1)
        self.label_109 = QLabel(self.widget_14)
        self.label_109.setObjectName(u"label_109")
        self.label_109.setMaximumSize(QSize(110, 16777215))
        self.label_109.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")

        self.horizontalLayout_126.addWidget(self.label_109, 0, Qt.AlignmentFlag.AlignLeft)

        self.freddotlasergalvoPushButton = QPushButton(self.widget_14)
        self.freddotlasergalvoPushButton.setObjectName(u"freddotlasergalvoPushButton")
        self.freddotlasergalvoPushButton.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.freddotlasergalvoPushButton.sizePolicy().hasHeightForWidth())
        self.freddotlasergalvoPushButton.setSizePolicy(sizePolicy6)
        self.freddotlasergalvoPushButton.setMinimumSize(QSize(0, 0))
        self.freddotlasergalvoPushButton.setMaximumSize(QSize(16777215, 50))
        self.freddotlasergalvoPushButton.setBaseSize(QSize(0, 0))
        self.freddotlasergalvoPushButton.setFont(font2)
        self.freddotlasergalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_126.addWidget(self.freddotlasergalvoPushButton)

        self.horizontalLayout_126.setStretch(0, 3)
        self.horizontalLayout_126.setStretch(1, 3)

        self.verticalLayout_63.addWidget(self.widget_14)


        self.horizontalLayout_53.addWidget(self.objheightlasrFrame)

        self.zfocusgalvoFrame = QFrame(self.widget_12)
        self.zfocusgalvoFrame.setObjectName(u"zfocusgalvoFrame")
        self.zfocusgalvoFrame.setStyleSheet(u"")
        self.zfocusgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.zfocusgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_54 = QHBoxLayout(self.zfocusgalvoFrame)
        self.horizontalLayout_54.setObjectName(u"horizontalLayout_54")
        self.horizontalLayout_54.setContentsMargins(9, -1, 9, -1)
        self.frame_18 = QFrame(self.zfocusgalvoFrame)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_18.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_65 = QVBoxLayout(self.frame_18)
        self.verticalLayout_65.setObjectName(u"verticalLayout_65")
        self.verticalLayout_65.setContentsMargins(0, 0, 0, 0)
        self.fplusgalvoPushButton = QPushButton(self.frame_18)
        self.fplusgalvoPushButton.setObjectName(u"fplusgalvoPushButton")
        sizePolicy6.setHeightForWidth(self.fplusgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.fplusgalvoPushButton.setSizePolicy(sizePolicy6)
        self.fplusgalvoPushButton.setMinimumSize(QSize(0, 0))
        self.fplusgalvoPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.fplusgalvoPushButton.setFont(font2)
        self.fplusgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_65.addWidget(self.fplusgalvoPushButton)

        self.ftravelgalvoPushButton = QPushButton(self.frame_18)
        self.ftravelgalvoPushButton.setObjectName(u"ftravelgalvoPushButton")
        sizePolicy6.setHeightForWidth(self.ftravelgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.ftravelgalvoPushButton.setSizePolicy(sizePolicy6)
        self.ftravelgalvoPushButton.setMinimumSize(QSize(0, 0))
        self.ftravelgalvoPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.ftravelgalvoPushButton.setFont(font2)
        self.ftravelgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_65.addWidget(self.ftravelgalvoPushButton)

        self.fminusgalvoPushButton = QPushButton(self.frame_18)
        self.fminusgalvoPushButton.setObjectName(u"fminusgalvoPushButton")
        sizePolicy6.setHeightForWidth(self.fminusgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.fminusgalvoPushButton.setSizePolicy(sizePolicy6)
        self.fminusgalvoPushButton.setMinimumSize(QSize(0, 0))
        self.fminusgalvoPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.fminusgalvoPushButton.setFont(font2)
        self.fminusgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_65.addWidget(self.fminusgalvoPushButton)


        self.horizontalLayout_54.addWidget(self.frame_18)


        self.horizontalLayout_53.addWidget(self.zfocusgalvoFrame)

        self.fsetgalvoFrame = QFrame(self.widget_12)
        self.fsetgalvoFrame.setObjectName(u"fsetgalvoFrame")
        self.fsetgalvoFrame.setStyleSheet(u"")
        self.fsetgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.fsetgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_66 = QVBoxLayout(self.fsetgalvoFrame)
        self.verticalLayout_66.setObjectName(u"verticalLayout_66")
        self.focusgalvoLCDNumber = QLCDNumber(self.fsetgalvoFrame)
        self.focusgalvoLCDNumber.setObjectName(u"focusgalvoLCDNumber")
        sizePolicy6.setHeightForWidth(self.focusgalvoLCDNumber.sizePolicy().hasHeightForWidth())
        self.focusgalvoLCDNumber.setSizePolicy(sizePolicy6)
        self.focusgalvoLCDNumber.setMinimumSize(QSize(100, 0))

        self.verticalLayout_66.addWidget(self.focusgalvoLCDNumber)

        self.fsetgalvoPushButton = QPushButton(self.fsetgalvoFrame)
        self.fsetgalvoPushButton.setObjectName(u"fsetgalvoPushButton")
        self.fsetgalvoPushButton.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.fsetgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.fsetgalvoPushButton.setSizePolicy(sizePolicy6)
        self.fsetgalvoPushButton.setMinimumSize(QSize(100, 0))
        self.fsetgalvoPushButton.setMaximumSize(QSize(16777215, 150))
        self.fsetgalvoPushButton.setFont(font2)
        self.fsetgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.verticalLayout_66.addWidget(self.fsetgalvoPushButton)

        self.verticalLayout_66.setStretch(0, 2)
        self.verticalLayout_66.setStretch(1, 1)

        self.horizontalLayout_53.addWidget(self.fsetgalvoFrame)


        self.verticalLayout_87.addWidget(self.widget_12)

        self.frame_54 = QFrame(self.galvosetfocusFrame)
        self.frame_54.setObjectName(u"frame_54")
        self.frame_54.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_54.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_62 = QVBoxLayout(self.frame_54)
        self.verticalLayout_62.setObjectName(u"verticalLayout_62")
        self.verticalLayout_62.setContentsMargins(0, 0, 0, 0)
        self.label_45 = QLabel(self.frame_54)
        self.label_45.setObjectName(u"label_45")
        font13 = QFont()
        font13.setBold(True)
        self.label_45.setFont(font13)
        self.label_45.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")

        self.verticalLayout_62.addWidget(self.label_45, 0, Qt.AlignmentFlag.AlignHCenter)

        self.powerFrame = QFrame(self.frame_54)
        self.powerFrame.setObjectName(u"powerFrame")
        self.powerFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.powerFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_86 = QVBoxLayout(self.powerFrame)
        self.verticalLayout_86.setObjectName(u"verticalLayout_86")
        self.frame_55 = QFrame(self.powerFrame)
        self.frame_55.setObjectName(u"frame_55")
        self.frame_55.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_55.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_124 = QHBoxLayout(self.frame_55)
        self.horizontalLayout_124.setObjectName(u"horizontalLayout_124")
        self.label_108 = QLabel(self.frame_55)
        self.label_108.setObjectName(u"label_108")
        self.label_108.setMinimumSize(QSize(0, 0))
        self.label_108.setMaximumSize(QSize(140, 16777215))
        self.label_108.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")
        self.label_108.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_124.addWidget(self.label_108)

        self.laserpowerLineEdit = QLineEdit(self.frame_55)
        self.laserpowerLineEdit.setObjectName(u"laserpowerLineEdit")
        sizePolicy3.setHeightForWidth(self.laserpowerLineEdit.sizePolicy().hasHeightForWidth())
        self.laserpowerLineEdit.setSizePolicy(sizePolicy3)
        self.laserpowerLineEdit.setMinimumSize(QSize(0, 0))
        self.laserpowerLineEdit.setMaximumSize(QSize(80, 16777215))
        self.laserpowerLineEdit.setFont(font5)
        self.laserpowerLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.laserpowerLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_124.addWidget(self.laserpowerLineEdit)

        self.galvolaserpowerHorizontalSlider_2 = QSlider(self.frame_55)
        self.galvolaserpowerHorizontalSlider_2.setObjectName(u"galvolaserpowerHorizontalSlider_2")
        self.galvolaserpowerHorizontalSlider_2.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_124.addWidget(self.galvolaserpowerHorizontalSlider_2)

        self.powersetgalvoPushButton_2 = QPushButton(self.frame_55)
        self.powersetgalvoPushButton_2.setObjectName(u"powersetgalvoPushButton_2")
        self.powersetgalvoPushButton_2.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.powersetgalvoPushButton_2.sizePolicy().hasHeightForWidth())
        self.powersetgalvoPushButton_2.setSizePolicy(sizePolicy6)
        self.powersetgalvoPushButton_2.setMinimumSize(QSize(0, 0))
        self.powersetgalvoPushButton_2.setMaximumSize(QSize(80, 50))
        self.powersetgalvoPushButton_2.setFont(font2)
        self.powersetgalvoPushButton_2.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_124.addWidget(self.powersetgalvoPushButton_2)


        self.verticalLayout_86.addWidget(self.frame_55)

        self.frame_61 = QFrame(self.powerFrame)
        self.frame_61.setObjectName(u"frame_61")
        self.frame_61.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_61.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_125 = QHBoxLayout(self.frame_61)
        self.horizontalLayout_125.setObjectName(u"horizontalLayout_125")
        self.label_32 = QLabel(self.frame_61)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setMinimumSize(QSize(0, 0))
        self.label_32.setMaximumSize(QSize(140, 16777215))
        self.label_32.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")
        self.label_32.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_125.addWidget(self.label_32)

        self.laserfreqLineEdit = QLineEdit(self.frame_61)
        self.laserfreqLineEdit.setObjectName(u"laserfreqLineEdit")
        sizePolicy3.setHeightForWidth(self.laserfreqLineEdit.sizePolicy().hasHeightForWidth())
        self.laserfreqLineEdit.setSizePolicy(sizePolicy3)
        self.laserfreqLineEdit.setMinimumSize(QSize(0, 0))
        self.laserfreqLineEdit.setMaximumSize(QSize(80, 16777215))
        self.laserfreqLineEdit.setFont(font5)
        self.laserfreqLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.laserfreqLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_125.addWidget(self.laserfreqLineEdit)

        self.galvolaserfreqHorizontalSlider = QSlider(self.frame_61)
        self.galvolaserfreqHorizontalSlider.setObjectName(u"galvolaserfreqHorizontalSlider")
        self.galvolaserfreqHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_125.addWidget(self.galvolaserfreqHorizontalSlider)

        self.freqsetgalvoPushButton = QPushButton(self.frame_61)
        self.freqsetgalvoPushButton.setObjectName(u"freqsetgalvoPushButton")
        self.freqsetgalvoPushButton.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.freqsetgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.freqsetgalvoPushButton.setSizePolicy(sizePolicy6)
        self.freqsetgalvoPushButton.setMinimumSize(QSize(0, 0))
        self.freqsetgalvoPushButton.setMaximumSize(QSize(80, 50))
        self.freqsetgalvoPushButton.setFont(font2)
        self.freqsetgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_125.addWidget(self.freqsetgalvoPushButton)


        self.verticalLayout_86.addWidget(self.frame_61)


        self.verticalLayout_62.addWidget(self.powerFrame)


        self.verticalLayout_87.addWidget(self.frame_54)


        self.verticalLayout_40.addWidget(self.galvosetfocusFrame)


        self.verticalLayout_73.addWidget(self.galvolaserconfFrame)

        self.mainPages.addWidget(self.laserconfgalvoPage)
        self.programgalvoPage = QWidget()
        self.programgalvoPage.setObjectName(u"programgalvoPage")
        self.verticalLayout_67 = QVBoxLayout(self.programgalvoPage)
        self.verticalLayout_67.setObjectName(u"verticalLayout_67")
        self.page2Label_2 = QLabel(self.programgalvoPage)
        self.page2Label_2.setObjectName(u"page2Label_2")
        self.page2Label_2.setMinimumSize(QSize(0, 20))
        self.page2Label_2.setMaximumSize(QSize(16777215, 20))
        self.page2Label_2.setFont(font2)
        self.page2Label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_67.addWidget(self.page2Label_2)

        self.programgalvoFrame = QFrame(self.programgalvoPage)
        self.programgalvoFrame.setObjectName(u"programgalvoFrame")
        self.programgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.programgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_22 = QHBoxLayout(self.programgalvoFrame)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.pgmgalvoFrame = QFrame(self.programgalvoFrame)
        self.pgmgalvoFrame.setObjectName(u"pgmgalvoFrame")
        self.pgmgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.pgmgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_72 = QVBoxLayout(self.pgmgalvoFrame)
        self.verticalLayout_72.setObjectName(u"verticalLayout_72")
        self.scrollArea = QScrollArea(self.pgmgalvoFrame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 687, 929))
        self.verticalLayout_64 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_64.setObjectName(u"verticalLayout_64")
        self.widget_15 = QWidget(self.scrollAreaWidgetContents)
        self.widget_15.setObjectName(u"widget_15")
        self.horizontalLayout_57 = QHBoxLayout(self.widget_15)
        self.horizontalLayout_57.setSpacing(10)
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.horizontalLayout_57.setContentsMargins(9, -1, -1, -1)
        self.label_28 = QLabel(self.widget_15)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setMinimumSize(QSize(0, 0))
        self.label_28.setMaximumSize(QSize(120, 16777215))
        self.label_28.setFont(font9)
        self.label_28.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_57.addWidget(self.label_28)

        self.pgmfilegalvoTextEdit = QTextEdit(self.widget_15)
        self.pgmfilegalvoTextEdit.setObjectName(u"pgmfilegalvoTextEdit")
        sizePolicy6.setHeightForWidth(self.pgmfilegalvoTextEdit.sizePolicy().hasHeightForWidth())
        self.pgmfilegalvoTextEdit.setSizePolicy(sizePolicy6)
        self.pgmfilegalvoTextEdit.setMinimumSize(QSize(320, 0))
        self.pgmfilegalvoTextEdit.setMaximumSize(QSize(16777215, 50))
        self.pgmfilegalvoTextEdit.setFont(font9)
        self.pgmfilegalvoTextEdit.setStyleSheet(u"QTextEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}")
        self.pgmfilegalvoTextEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.pgmfilegalvoTextEdit.setReadOnly(True)

        self.horizontalLayout_57.addWidget(self.pgmfilegalvoTextEdit)

        self.pgmfilegalvoPushButton = QPushButton(self.widget_15)
        self.pgmfilegalvoPushButton.setObjectName(u"pgmfilegalvoPushButton")
        sizePolicy6.setHeightForWidth(self.pgmfilegalvoPushButton.sizePolicy().hasHeightForWidth())
        self.pgmfilegalvoPushButton.setSizePolicy(sizePolicy6)
        self.pgmfilegalvoPushButton.setMaximumSize(QSize(350, 100))
        self.pgmfilegalvoPushButton.setFont(font2)
        self.pgmfilegalvoPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_57.addWidget(self.pgmfilegalvoPushButton)

        self.horizontalLayout_57.setStretch(0, 2)
        self.horizontalLayout_57.setStretch(1, 2)
        self.horizontalLayout_57.setStretch(2, 1)

        self.verticalLayout_64.addWidget(self.widget_15)

        self.widget_16 = QWidget(self.scrollAreaWidgetContents)
        self.widget_16.setObjectName(u"widget_16")
        self.horizontalLayout_58 = QHBoxLayout(self.widget_16)
        self.horizontalLayout_58.setSpacing(9)
        self.horizontalLayout_58.setObjectName(u"horizontalLayout_58")
        self.label_29 = QLabel(self.widget_16)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setMinimumSize(QSize(0, 0))
        self.label_29.setMaximumSize(QSize(16777215, 16777215))
        self.label_29.setFont(font9)
        self.label_29.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_58.addWidget(self.label_29)

        self.pgmheightgalvoLineEdit = QLineEdit(self.widget_16)
        self.pgmheightgalvoLineEdit.setObjectName(u"pgmheightgalvoLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmheightgalvoLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmheightgalvoLineEdit.setSizePolicy(sizePolicy6)
        self.pgmheightgalvoLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmheightgalvoLineEdit.setFont(font9)
        self.pgmheightgalvoLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmheightgalvoLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_58.addWidget(self.pgmheightgalvoLineEdit)

        self.label_30 = QLabel(self.widget_16)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setFont(font9)
        self.label_30.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_58.addWidget(self.label_30)

        self.horizontalLayout_58.setStretch(0, 1)
        self.horizontalLayout_58.setStretch(1, 5)

        self.verticalLayout_64.addWidget(self.widget_16)

        self.frame_40 = QFrame(self.scrollAreaWidgetContents)
        self.frame_40.setObjectName(u"frame_40")
        self.frame_40.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_40.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_66 = QHBoxLayout(self.frame_40)
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.horizontalLayout_66.setContentsMargins(0, 0, 0, 0)
        self.widget_18 = QWidget(self.frame_40)
        self.widget_18.setObjectName(u"widget_18")
        self.horizontalLayout_60 = QHBoxLayout(self.widget_18)
        self.horizontalLayout_60.setObjectName(u"horizontalLayout_60")
        self.horizontalLayout_60.setContentsMargins(-1, -1, 0, -1)
        self.label_33 = QLabel(self.widget_18)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setMaximumSize(QSize(16777215, 16777215))
        self.label_33.setFont(font9)
        self.label_33.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_60.addWidget(self.label_33)

        self.pgmmarkspeedgalvoLineEdit = QLineEdit(self.widget_18)
        self.pgmmarkspeedgalvoLineEdit.setObjectName(u"pgmmarkspeedgalvoLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmmarkspeedgalvoLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmmarkspeedgalvoLineEdit.setSizePolicy(sizePolicy6)
        self.pgmmarkspeedgalvoLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmmarkspeedgalvoLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmmarkspeedgalvoLineEdit.setFont(font9)
        self.pgmmarkspeedgalvoLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmmarkspeedgalvoLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_60.addWidget(self.pgmmarkspeedgalvoLineEdit)

        self.horizontalLayout_60.setStretch(0, 3)
        self.horizontalLayout_60.setStretch(1, 5)

        self.horizontalLayout_66.addWidget(self.widget_18)

        self.widget_19 = QWidget(self.frame_40)
        self.widget_19.setObjectName(u"widget_19")
        self.horizontalLayout_62 = QHBoxLayout(self.widget_19)
        self.horizontalLayout_62.setObjectName(u"horizontalLayout_62")
        self.horizontalLayout_62.setContentsMargins(-1, -1, 0, -1)
        self.label_36 = QLabel(self.widget_19)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setMaximumSize(QSize(16777215, 16777215))
        self.label_36.setFont(font9)
        self.label_36.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_62.addWidget(self.label_36)

        self.pgmjumpspeedLineEdit = QLineEdit(self.widget_19)
        self.pgmjumpspeedLineEdit.setObjectName(u"pgmjumpspeedLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmjumpspeedLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmjumpspeedLineEdit.setSizePolicy(sizePolicy6)
        self.pgmjumpspeedLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmjumpspeedLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmjumpspeedLineEdit.setFont(font9)
        self.pgmjumpspeedLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmjumpspeedLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_62.addWidget(self.pgmjumpspeedLineEdit)

        self.horizontalLayout_62.setStretch(0, 3)
        self.horizontalLayout_62.setStretch(1, 5)

        self.horizontalLayout_66.addWidget(self.widget_19)

        self.widget_24 = QWidget(self.frame_40)
        self.widget_24.setObjectName(u"widget_24")
        self.horizontalLayout_63 = QHBoxLayout(self.widget_24)
        self.horizontalLayout_63.setObjectName(u"horizontalLayout_63")
        self.horizontalLayout_63.setContentsMargins(-1, -1, 0, -1)
        self.label_37 = QLabel(self.widget_24)
        self.label_37.setObjectName(u"label_37")
        self.label_37.setMaximumSize(QSize(16777215, 16777215))
        self.label_37.setFont(font9)
        self.label_37.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_63.addWidget(self.label_37)

        self.pgmloopcountLineEdit = QLineEdit(self.widget_24)
        self.pgmloopcountLineEdit.setObjectName(u"pgmloopcountLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmloopcountLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmloopcountLineEdit.setSizePolicy(sizePolicy6)
        self.pgmloopcountLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmloopcountLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmloopcountLineEdit.setFont(font9)
        self.pgmloopcountLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmloopcountLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_63.addWidget(self.pgmloopcountLineEdit)

        self.horizontalLayout_63.setStretch(0, 3)

        self.horizontalLayout_66.addWidget(self.widget_24)


        self.verticalLayout_64.addWidget(self.frame_40)

        self.widget_25 = QWidget(self.scrollAreaWidgetContents)
        self.widget_25.setObjectName(u"widget_25")
        self.horizontalLayout_64 = QHBoxLayout(self.widget_25)
        self.horizontalLayout_64.setObjectName(u"horizontalLayout_64")
        self.label_38 = QLabel(self.widget_25)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setMaximumSize(QSize(16777215, 16777215))
        self.label_38.setFont(font9)
        self.label_38.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_64.addWidget(self.label_38)

        self.label_39 = QLabel(self.widget_25)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setMaximumSize(QSize(16777215, 16777215))
        self.label_39.setFont(font9)
        self.label_39.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_64.addWidget(self.label_39)

        self.pgmstartposxLineEdit = QLineEdit(self.widget_25)
        self.pgmstartposxLineEdit.setObjectName(u"pgmstartposxLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmstartposxLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmstartposxLineEdit.setSizePolicy(sizePolicy6)
        self.pgmstartposxLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmstartposxLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmstartposxLineEdit.setFont(font9)
        self.pgmstartposxLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmstartposxLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_64.addWidget(self.pgmstartposxLineEdit)

        self.label_40 = QLabel(self.widget_25)
        self.label_40.setObjectName(u"label_40")
        self.label_40.setMaximumSize(QSize(130, 16777215))
        self.label_40.setFont(font9)
        self.label_40.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_64.addWidget(self.label_40)

        self.pgmstartposyLineEdit = QLineEdit(self.widget_25)
        self.pgmstartposyLineEdit.setObjectName(u"pgmstartposyLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmstartposyLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmstartposyLineEdit.setSizePolicy(sizePolicy6)
        self.pgmstartposyLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmstartposyLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmstartposyLineEdit.setFont(font9)
        self.pgmstartposyLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmstartposyLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_64.addWidget(self.pgmstartposyLineEdit)


        self.verticalLayout_64.addWidget(self.widget_25)

        self.widget_26 = QWidget(self.scrollAreaWidgetContents)
        self.widget_26.setObjectName(u"widget_26")
        self.horizontalLayout_74 = QHBoxLayout(self.widget_26)
        self.horizontalLayout_74.setObjectName(u"horizontalLayout_74")
        self.label_41 = QLabel(self.widget_26)
        self.label_41.setObjectName(u"label_41")
        self.label_41.setMaximumSize(QSize(16777215, 16777215))
        self.label_41.setFont(font9)
        self.label_41.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_74.addWidget(self.label_41)

        self.pgmenablehatchCheckBox = QCheckBox(self.widget_26)
        self.pgmenablehatchCheckBox.setObjectName(u"pgmenablehatchCheckBox")

        self.horizontalLayout_74.addWidget(self.pgmenablehatchCheckBox, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_74.setStretch(0, 1)
        self.horizontalLayout_74.setStretch(1, 2)

        self.verticalLayout_64.addWidget(self.widget_26)

        self.widget_32 = QWidget(self.scrollAreaWidgetContents)
        self.widget_32.setObjectName(u"widget_32")
        self.horizontalLayout_77 = QHBoxLayout(self.widget_32)
        self.horizontalLayout_77.setObjectName(u"horizontalLayout_77")
        self.label_54 = QLabel(self.widget_32)
        self.label_54.setObjectName(u"label_54")
        self.label_54.setMaximumSize(QSize(16777215, 16777215))
        self.label_54.setFont(font9)
        self.label_54.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_77.addWidget(self.label_54)

        self.pgmmarkcontourCheckBox = QCheckBox(self.widget_32)
        self.pgmmarkcontourCheckBox.setObjectName(u"pgmmarkcontourCheckBox")

        self.horizontalLayout_77.addWidget(self.pgmmarkcontourCheckBox, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalLayout_77.setStretch(0, 1)
        self.horizontalLayout_77.setStretch(1, 2)

        self.verticalLayout_64.addWidget(self.widget_32)

        self.frame_26 = QFrame(self.scrollAreaWidgetContents)
        self.frame_26.setObjectName(u"frame_26")
        self.frame_26.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_26.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_61 = QHBoxLayout(self.frame_26)
        self.horizontalLayout_61.setObjectName(u"horizontalLayout_61")
        self.horizontalLayout_61.setContentsMargins(9, -1, -1, -1)
        self.label_55 = QLabel(self.frame_26)
        self.label_55.setObjectName(u"label_55")
        self.label_55.setMinimumSize(QSize(0, 0))
        self.label_55.setMaximumSize(QSize(130, 16777215))
        self.label_55.setFont(font9)
        self.label_55.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_61.addWidget(self.label_55)

        self.pgmhatch1_RadioButton = QRadioButton(self.frame_26)
        self.pgmhatch1_RadioButton.setObjectName(u"pgmhatch1_RadioButton")
        self.pgmhatch1_RadioButton.setMaximumSize(QSize(20, 16777215))
        self.pgmhatch1_RadioButton.setFont(font9)

        self.horizontalLayout_61.addWidget(self.pgmhatch1_RadioButton)

        self.label_79 = QLabel(self.frame_26)
        self.label_79.setObjectName(u"label_79")
        self.label_79.setMaximumSize(QSize(16777215, 16777215))
        self.label_79.setFont(font9)
        self.label_79.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_61.addWidget(self.label_79)

        self.pgmhatch2_RadioButton = QRadioButton(self.frame_26)
        self.pgmhatch2_RadioButton.setObjectName(u"pgmhatch2_RadioButton")
        self.pgmhatch2_RadioButton.setMaximumSize(QSize(20, 16777215))
        self.pgmhatch2_RadioButton.setFont(font9)

        self.horizontalLayout_61.addWidget(self.pgmhatch2_RadioButton)

        self.label_80 = QLabel(self.frame_26)
        self.label_80.setObjectName(u"label_80")
        self.label_80.setMaximumSize(QSize(16777215, 16777215))
        self.label_80.setFont(font9)
        self.label_80.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_61.addWidget(self.label_80, 0, Qt.AlignmentFlag.AlignLeft)

        self.pgmhatch3_RadioButton = QRadioButton(self.frame_26)
        self.pgmhatch3_RadioButton.setObjectName(u"pgmhatch3_RadioButton")
        self.pgmhatch3_RadioButton.setMaximumSize(QSize(20, 16777215))
        self.pgmhatch3_RadioButton.setFont(font9)

        self.horizontalLayout_61.addWidget(self.pgmhatch3_RadioButton)

        self.label_81 = QLabel(self.frame_26)
        self.label_81.setObjectName(u"label_81")
        self.label_81.setMaximumSize(QSize(16777215, 16777215))
        self.label_81.setFont(font9)
        self.label_81.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_61.addWidget(self.label_81, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalLayout_61.setStretch(0, 3)

        self.verticalLayout_64.addWidget(self.frame_26)

        self.frame_36 = QFrame(self.scrollAreaWidgetContents)
        self.frame_36.setObjectName(u"frame_36")
        self.horizontalLayout_84 = QHBoxLayout(self.frame_36)
        self.horizontalLayout_84.setObjectName(u"horizontalLayout_84")
        self.label_78 = QLabel(self.frame_36)
        self.label_78.setObjectName(u"label_78")
        self.label_78.setMaximumSize(QSize(16777215, 16777215))
        self.label_78.setFont(font9)
        self.label_78.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_84.addWidget(self.label_78)

        self.pgmenableCheckBox = QCheckBox(self.frame_36)
        self.pgmenableCheckBox.setObjectName(u"pgmenableCheckBox")

        self.horizontalLayout_84.addWidget(self.pgmenableCheckBox, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalLayout_84.setStretch(0, 1)
        self.horizontalLayout_84.setStretch(1, 2)

        self.verticalLayout_64.addWidget(self.frame_36)

        self.widget_33 = QWidget(self.scrollAreaWidgetContents)
        self.widget_33.setObjectName(u"widget_33")
        self.horizontalLayout_71 = QHBoxLayout(self.widget_33)
        self.horizontalLayout_71.setObjectName(u"horizontalLayout_71")
        self.horizontalLayout_71.setContentsMargins(0, 0, 0, 0)
        self.frame_19 = QFrame(self.widget_33)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_19.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_68 = QHBoxLayout(self.frame_19)
        self.horizontalLayout_68.setObjectName(u"horizontalLayout_68")
        self.label_56 = QLabel(self.frame_19)
        self.label_56.setObjectName(u"label_56")
        self.label_56.setMaximumSize(QSize(130, 16777215))
        self.label_56.setFont(font9)
        self.label_56.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_68.addWidget(self.label_56)

        self.pgmallcalcCheckBox = QCheckBox(self.frame_19)
        self.pgmallcalcCheckBox.setObjectName(u"pgmallcalcCheckBox")

        self.horizontalLayout_68.addWidget(self.pgmallcalcCheckBox)


        self.horizontalLayout_71.addWidget(self.frame_19)

        self.frame_20 = QFrame(self.widget_33)
        self.frame_20.setObjectName(u"frame_20")
        self.frame_20.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_20.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_69 = QHBoxLayout(self.frame_20)
        self.horizontalLayout_69.setObjectName(u"horizontalLayout_69")
        self.label_57 = QLabel(self.frame_20)
        self.label_57.setObjectName(u"label_57")
        self.label_57.setMaximumSize(QSize(130, 16777215))
        self.label_57.setFont(font9)
        self.label_57.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_69.addWidget(self.label_57)

        self.pgmfolloedgCheckBox = QCheckBox(self.frame_20)
        self.pgmfolloedgCheckBox.setObjectName(u"pgmfolloedgCheckBox")

        self.horizontalLayout_69.addWidget(self.pgmfolloedgCheckBox)


        self.horizontalLayout_71.addWidget(self.frame_20)

        self.frame_21 = QFrame(self.widget_33)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_21.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_70 = QHBoxLayout(self.frame_21)
        self.horizontalLayout_70.setObjectName(u"horizontalLayout_70")
        self.label_58 = QLabel(self.frame_21)
        self.label_58.setObjectName(u"label_58")
        self.label_58.setMaximumSize(QSize(130, 16777215))
        self.label_58.setFont(font9)
        self.label_58.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_70.addWidget(self.label_58)

        self.pgmcrosshatchCheckBox = QCheckBox(self.frame_21)
        self.pgmcrosshatchCheckBox.setObjectName(u"pgmcrosshatchCheckBox")

        self.horizontalLayout_70.addWidget(self.pgmcrosshatchCheckBox)


        self.horizontalLayout_71.addWidget(self.frame_21)


        self.verticalLayout_64.addWidget(self.widget_33)

        self.widget_34 = QWidget(self.scrollAreaWidgetContents)
        self.widget_34.setObjectName(u"widget_34")
        sizePolicy6.setHeightForWidth(self.widget_34.sizePolicy().hasHeightForWidth())
        self.widget_34.setSizePolicy(sizePolicy6)
        self.widget_34.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_72 = QHBoxLayout(self.widget_34)
        self.horizontalLayout_72.setObjectName(u"horizontalLayout_72")
        self.label_31 = QLabel(self.widget_34)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMaximumSize(QSize(90, 16777215))
        self.label_31.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"    font-size: 16px;\n"
"    border: none;\n"
"}")

        self.horizontalLayout_72.addWidget(self.label_31)

        self.pgmtypeComboBox = QComboBox(self.widget_34)
        self.pgmtypeComboBox.setObjectName(u"pgmtypeComboBox")
        self.pgmtypeComboBox.setEnabled(True)
        self.pgmtypeComboBox.setFont(font)
        self.pgmtypeComboBox.setStyleSheet(u"QComboBox {\n"
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

        self.horizontalLayout_72.addWidget(self.pgmtypeComboBox)

        self.horizontalLayout_72.setStretch(0, 1)
        self.horizontalLayout_72.setStretch(1, 3)

        self.verticalLayout_64.addWidget(self.widget_34)

        self.frame_22 = QFrame(self.scrollAreaWidgetContents)
        self.frame_22.setObjectName(u"frame_22")
        self.frame_22.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_22.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_80 = QHBoxLayout(self.frame_22)
        self.horizontalLayout_80.setObjectName(u"horizontalLayout_80")
        self.horizontalLayout_80.setContentsMargins(0, 0, 0, 0)
        self.frame_24 = QFrame(self.frame_22)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_24.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_73 = QHBoxLayout(self.frame_24)
        self.horizontalLayout_73.setObjectName(u"horizontalLayout_73")
        self.label_48 = QLabel(self.frame_24)
        self.label_48.setObjectName(u"label_48")
        self.label_48.setMaximumSize(QSize(130, 16777215))
        self.label_48.setFont(font9)
        self.label_48.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_73.addWidget(self.label_48)

        self.pgmangleLineEdit = QLineEdit(self.frame_24)
        self.pgmangleLineEdit.setObjectName(u"pgmangleLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmangleLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmangleLineEdit.setSizePolicy(sizePolicy6)
        self.pgmangleLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmangleLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmangleLineEdit.setFont(font9)
        self.pgmangleLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmangleLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_73.addWidget(self.pgmangleLineEdit)

        self.label_59 = QLabel(self.frame_24)
        self.label_59.setObjectName(u"label_59")
        font14 = QFont()
        font14.setPointSize(20)
        font14.setBold(True)
        self.label_59.setFont(font14)
        self.label_59.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_73.addWidget(self.label_59)


        self.horizontalLayout_80.addWidget(self.frame_24)

        self.frame_23 = QFrame(self.frame_22)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_23.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_78 = QHBoxLayout(self.frame_23)
        self.horizontalLayout_78.setObjectName(u"horizontalLayout_78")
        self.label_60 = QLabel(self.frame_23)
        self.label_60.setObjectName(u"label_60")
        self.label_60.setMaximumSize(QSize(130, 16777215))
        self.label_60.setFont(font9)
        self.label_60.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_78.addWidget(self.label_60)

        self.pgmcountLineEdit = QLineEdit(self.frame_23)
        self.pgmcountLineEdit.setObjectName(u"pgmcountLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmcountLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmcountLineEdit.setSizePolicy(sizePolicy6)
        self.pgmcountLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmcountLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmcountLineEdit.setFont(font9)
        self.pgmcountLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmcountLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_78.addWidget(self.pgmcountLineEdit)


        self.horizontalLayout_80.addWidget(self.frame_23)

        self.frame_27 = QFrame(self.frame_22)
        self.frame_27.setObjectName(u"frame_27")
        self.frame_27.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_27.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_79 = QHBoxLayout(self.frame_27)
        self.horizontalLayout_79.setObjectName(u"horizontalLayout_79")
        self.label_61 = QLabel(self.frame_27)
        self.label_61.setObjectName(u"label_61")
        self.label_61.setMaximumSize(QSize(130, 16777215))
        self.label_61.setFont(font9)
        self.label_61.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_79.addWidget(self.label_61)

        self.pgmlinespaceLineEdit = QLineEdit(self.frame_27)
        self.pgmlinespaceLineEdit.setObjectName(u"pgmlinespaceLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmlinespaceLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmlinespaceLineEdit.setSizePolicy(sizePolicy6)
        self.pgmlinespaceLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmlinespaceLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmlinespaceLineEdit.setFont(font9)
        self.pgmlinespaceLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmlinespaceLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_79.addWidget(self.pgmlinespaceLineEdit)

        self.label_62 = QLabel(self.frame_27)
        self.label_62.setObjectName(u"label_62")
        self.label_62.setFont(font9)
        self.label_62.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_79.addWidget(self.label_62)


        self.horizontalLayout_80.addWidget(self.frame_27)


        self.verticalLayout_64.addWidget(self.frame_22)

        self.widget_35 = QWidget(self.scrollAreaWidgetContents)
        self.widget_35.setObjectName(u"widget_35")
        self.horizontalLayout_81 = QHBoxLayout(self.widget_35)
        self.horizontalLayout_81.setObjectName(u"horizontalLayout_81")
        self.label_63 = QLabel(self.widget_35)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setMaximumSize(QSize(16777215, 16777215))
        self.label_63.setFont(font9)
        self.label_63.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_81.addWidget(self.label_63)

        self.pgmavgdistCheckBox = QCheckBox(self.widget_35)
        self.pgmavgdistCheckBox.setObjectName(u"pgmavgdistCheckBox")

        self.horizontalLayout_81.addWidget(self.pgmavgdistCheckBox, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_64.addWidget(self.widget_35)

        self.frame_28 = QFrame(self.scrollAreaWidgetContents)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_28.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_67 = QHBoxLayout(self.frame_28)
        self.horizontalLayout_67.setObjectName(u"horizontalLayout_67")
        self.horizontalLayout_67.setContentsMargins(0, 0, 0, 0)
        self.frame_29 = QFrame(self.frame_28)
        self.frame_29.setObjectName(u"frame_29")
        self.frame_29.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_29.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_82 = QHBoxLayout(self.frame_29)
        self.horizontalLayout_82.setObjectName(u"horizontalLayout_82")
        self.label_64 = QLabel(self.frame_29)
        self.label_64.setObjectName(u"label_64")
        self.label_64.setMaximumSize(QSize(130, 16777215))
        self.label_64.setFont(font9)
        self.label_64.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_82.addWidget(self.label_64)

        self.pgmedgeoffLineEdit = QLineEdit(self.frame_29)
        self.pgmedgeoffLineEdit.setObjectName(u"pgmedgeoffLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmedgeoffLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmedgeoffLineEdit.setSizePolicy(sizePolicy6)
        self.pgmedgeoffLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmedgeoffLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.pgmedgeoffLineEdit.setFont(font9)
        self.pgmedgeoffLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmedgeoffLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_82.addWidget(self.pgmedgeoffLineEdit)

        self.label_75 = QLabel(self.frame_29)
        self.label_75.setObjectName(u"label_75")
        self.label_75.setFont(font9)
        self.label_75.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_82.addWidget(self.label_75)

        self.label_65 = QLabel(self.frame_29)
        self.label_65.setObjectName(u"label_65")
        self.label_65.setFont(font14)
        self.label_65.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_82.addWidget(self.label_65)


        self.horizontalLayout_67.addWidget(self.frame_29)

        self.frame_30 = QFrame(self.frame_28)
        self.frame_30.setObjectName(u"frame_30")
        self.frame_30.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_30.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_83 = QHBoxLayout(self.frame_30)
        self.horizontalLayout_83.setObjectName(u"horizontalLayout_83")
        self.label_66 = QLabel(self.frame_30)
        self.label_66.setObjectName(u"label_66")
        self.label_66.setMaximumSize(QSize(130, 16777215))
        self.label_66.setFont(font9)
        self.label_66.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_83.addWidget(self.label_66)

        self.pgmstartoffLineEdit = QLineEdit(self.frame_30)
        self.pgmstartoffLineEdit.setObjectName(u"pgmstartoffLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmstartoffLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmstartoffLineEdit.setSizePolicy(sizePolicy6)
        self.pgmstartoffLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmstartoffLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.pgmstartoffLineEdit.setFont(font9)
        self.pgmstartoffLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmstartoffLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_83.addWidget(self.pgmstartoffLineEdit)

        self.label_77 = QLabel(self.frame_30)
        self.label_77.setObjectName(u"label_77")
        self.label_77.setFont(font9)
        self.label_77.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_83.addWidget(self.label_77)


        self.horizontalLayout_67.addWidget(self.frame_30)

        self.frame_31 = QFrame(self.frame_28)
        self.frame_31.setObjectName(u"frame_31")
        self.frame_31.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_31.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_85 = QHBoxLayout(self.frame_31)
        self.horizontalLayout_85.setObjectName(u"horizontalLayout_85")
        self.label_67 = QLabel(self.frame_31)
        self.label_67.setObjectName(u"label_67")
        self.label_67.setMaximumSize(QSize(130, 16777215))
        self.label_67.setFont(font9)
        self.label_67.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_85.addWidget(self.label_67)

        self.pgmendoffLineEdit = QLineEdit(self.frame_31)
        self.pgmendoffLineEdit.setObjectName(u"pgmendoffLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmendoffLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmendoffLineEdit.setSizePolicy(sizePolicy6)
        self.pgmendoffLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmendoffLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.pgmendoffLineEdit.setFont(font9)
        self.pgmendoffLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmendoffLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_85.addWidget(self.pgmendoffLineEdit)

        self.label_68 = QLabel(self.frame_31)
        self.label_68.setObjectName(u"label_68")
        self.label_68.setFont(font9)
        self.label_68.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_85.addWidget(self.label_68)


        self.horizontalLayout_67.addWidget(self.frame_31)


        self.verticalLayout_64.addWidget(self.frame_28)

        self.frame_35 = QFrame(self.scrollAreaWidgetContents)
        self.frame_35.setObjectName(u"frame_35")
        self.frame_35.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_35.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_89 = QHBoxLayout(self.frame_35)
        self.horizontalLayout_89.setObjectName(u"horizontalLayout_89")
        self.horizontalLayout_89.setContentsMargins(0, 0, 0, 0)
        self.frame_361 = QFrame(self.frame_35)
        self.frame_361.setObjectName(u"frame_361")
        self.frame_361.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_361.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_91 = QHBoxLayout(self.frame_361)
        self.horizontalLayout_91.setObjectName(u"horizontalLayout_91")
        self.label_69 = QLabel(self.frame_361)
        self.label_69.setObjectName(u"label_69")
        self.label_69.setMaximumSize(QSize(130, 16777215))
        self.label_69.setFont(font9)
        self.label_69.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_91.addWidget(self.label_69)

        self.pgmlineredLineEdit = QLineEdit(self.frame_361)
        self.pgmlineredLineEdit.setObjectName(u"pgmlineredLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmlineredLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmlineredLineEdit.setSizePolicy(sizePolicy6)
        self.pgmlineredLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmlineredLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.pgmlineredLineEdit.setFont(font9)
        self.pgmlineredLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmlineredLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_91.addWidget(self.pgmlineredLineEdit)

        self.label_70 = QLabel(self.frame_361)
        self.label_70.setObjectName(u"label_70")
        self.label_70.setFont(font9)
        self.label_70.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_91.addWidget(self.label_70)


        self.horizontalLayout_89.addWidget(self.frame_361)

        self.frame_37 = QFrame(self.frame_35)
        self.frame_37.setObjectName(u"frame_37")
        self.frame_37.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_37.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_92 = QHBoxLayout(self.frame_37)
        self.horizontalLayout_92.setObjectName(u"horizontalLayout_92")
        self.label_71 = QLabel(self.frame_37)
        self.label_71.setObjectName(u"label_71")
        self.label_71.setMaximumSize(QSize(130, 16777215))
        self.label_71.setFont(font9)
        self.label_71.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_92.addWidget(self.label_71)

        self.pgmnumloopsLineEdit = QLineEdit(self.frame_37)
        self.pgmnumloopsLineEdit.setObjectName(u"pgmnumloopsLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmnumloopsLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmnumloopsLineEdit.setSizePolicy(sizePolicy6)
        self.pgmnumloopsLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmnumloopsLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.pgmnumloopsLineEdit.setFont(font9)
        self.pgmnumloopsLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmnumloopsLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_92.addWidget(self.pgmnumloopsLineEdit)


        self.horizontalLayout_89.addWidget(self.frame_37)

        self.frame_38 = QFrame(self.frame_35)
        self.frame_38.setObjectName(u"frame_38")
        self.frame_38.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_38.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_93 = QHBoxLayout(self.frame_38)
        self.horizontalLayout_93.setObjectName(u"horizontalLayout_93")
        self.label_72 = QLabel(self.frame_38)
        self.label_72.setObjectName(u"label_72")
        self.label_72.setMaximumSize(QSize(130, 16777215))
        self.label_72.setFont(font9)
        self.label_72.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_93.addWidget(self.label_72)

        self.pgmloopdistLineEdit = QLineEdit(self.frame_38)
        self.pgmloopdistLineEdit.setObjectName(u"pgmloopdistLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmloopdistLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmloopdistLineEdit.setSizePolicy(sizePolicy6)
        self.pgmloopdistLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmloopdistLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.pgmloopdistLineEdit.setFont(font9)
        self.pgmloopdistLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmloopdistLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_93.addWidget(self.pgmloopdistLineEdit)

        self.label_73 = QLabel(self.frame_38)
        self.label_73.setObjectName(u"label_73")
        self.label_73.setFont(font9)
        self.label_73.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_93.addWidget(self.label_73)


        self.horizontalLayout_89.addWidget(self.frame_38)


        self.verticalLayout_64.addWidget(self.frame_35)

        self.frame_39 = QFrame(self.scrollAreaWidgetContents)
        self.frame_39.setObjectName(u"frame_39")
        self.frame_39.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_39.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_65 = QHBoxLayout(self.frame_39)
        self.horizontalLayout_65.setObjectName(u"horizontalLayout_65")
        self.label_76 = QLabel(self.frame_39)
        self.label_76.setObjectName(u"label_76")
        self.label_76.setMaximumSize(QSize(16777215, 16777215))
        self.label_76.setFont(font9)
        self.label_76.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_65.addWidget(self.label_76)

        self.pgmautorotangleCheckBox = QCheckBox(self.frame_39)
        self.pgmautorotangleCheckBox.setObjectName(u"pgmautorotangleCheckBox")

        self.horizontalLayout_65.addWidget(self.pgmautorotangleCheckBox)

        self.pgmautorotanglLineEdit = QLineEdit(self.frame_39)
        self.pgmautorotanglLineEdit.setObjectName(u"pgmautorotanglLineEdit")
        sizePolicy6.setHeightForWidth(self.pgmautorotanglLineEdit.sizePolicy().hasHeightForWidth())
        self.pgmautorotanglLineEdit.setSizePolicy(sizePolicy6)
        self.pgmautorotanglLineEdit.setMinimumSize(QSize(0, 0))
        self.pgmautorotanglLineEdit.setMaximumSize(QSize(16777215, 100))
        self.pgmautorotanglLineEdit.setFont(font9)
        self.pgmautorotanglLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.pgmautorotanglLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_65.addWidget(self.pgmautorotanglLineEdit)

        self.label_74 = QLabel(self.frame_39)
        self.label_74.setObjectName(u"label_74")
        self.label_74.setFont(font14)
        self.label_74.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_65.addWidget(self.label_74)


        self.verticalLayout_64.addWidget(self.frame_39)

        self.widget_30 = QWidget(self.scrollAreaWidgetContents)
        self.widget_30.setObjectName(u"widget_30")
        self.horizontalLayout_59 = QHBoxLayout(self.widget_30)
        self.horizontalLayout_59.setSpacing(9)
        self.horizontalLayout_59.setObjectName(u"horizontalLayout_59")
        self.horizontalSpacer_10 = QSpacerItem(366, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_59.addItem(self.horizontalSpacer_10)

        self.pgmgalvosavePushButton = QPushButton(self.widget_30)
        self.pgmgalvosavePushButton.setObjectName(u"pgmgalvosavePushButton")
        self.pgmgalvosavePushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.pgmgalvosavePushButton.sizePolicy().hasHeightForWidth())
        self.pgmgalvosavePushButton.setSizePolicy(sizePolicy6)
        self.pgmgalvosavePushButton.setMaximumSize(QSize(16777215, 100))
        self.pgmgalvosavePushButton.setFont(font2)
        self.pgmgalvosavePushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_59.addWidget(self.pgmgalvosavePushButton)

        self.horizontalLayout_59.setStretch(0, 5)
        self.horizontalLayout_59.setStretch(1, 2)

        self.verticalLayout_64.addWidget(self.widget_30)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_72.addWidget(self.scrollArea)


        self.horizontalLayout_22.addWidget(self.pgmgalvoFrame)


        self.verticalLayout_67.addWidget(self.programgalvoFrame)

        self.mainPages.addWidget(self.programgalvoPage)
        self.printgalvoPage = QWidget()
        self.printgalvoPage.setObjectName(u"printgalvoPage")
        self.verticalLayout_74 = QVBoxLayout(self.printgalvoPage)
        self.verticalLayout_74.setObjectName(u"verticalLayout_74")
        self.page3Label_6 = QLabel(self.printgalvoPage)
        self.page3Label_6.setObjectName(u"page3Label_6")
        self.page3Label_6.setMinimumSize(QSize(0, 20))
        self.page3Label_6.setMaximumSize(QSize(16777215, 20))
        self.page3Label_6.setFont(font2)
        self.page3Label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_74.addWidget(self.page3Label_6)

        self.printgalvoFrame = QFrame(self.printgalvoPage)
        self.printgalvoFrame.setObjectName(u"printgalvoFrame")
        self.printgalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.printgalvoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_69 = QVBoxLayout(self.printgalvoFrame)
        self.verticalLayout_69.setObjectName(u"verticalLayout_69")
        self.frame_25 = QFrame(self.printgalvoFrame)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_25.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_75 = QHBoxLayout(self.frame_25)
        self.horizontalLayout_75.setObjectName(u"horizontalLayout_75")
        self.horizontalLayout_75.setContentsMargins(0, 0, 0, 0)
        self.printimggalvoFrame = QFrame(self.frame_25)
        self.printimggalvoFrame.setObjectName(u"printimggalvoFrame")
        self.printimggalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.printimggalvoFrame.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_70 = QVBoxLayout(self.printimggalvoFrame)
        self.verticalLayout_70.setObjectName(u"verticalLayout_70")
        self.label_51 = QLabel(self.printimggalvoFrame)
        self.label_51.setObjectName(u"label_51")
        self.label_51.setFont(font5)
        self.label_51.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_70.addWidget(self.label_51, 0, Qt.AlignmentFlag.AlignHCenter)

        self.printplotgalvoFrame = QFrame(self.printimggalvoFrame)
        self.printplotgalvoFrame.setObjectName(u"printplotgalvoFrame")
        self.printplotgalvoFrame.setFrameShape(QFrame.Shape.NoFrame)
        self.printplotgalvoFrame.setFrameShadow(QFrame.Shadow.Plain)

        self.verticalLayout_70.addWidget(self.printplotgalvoFrame)

        self.verticalLayout_70.setStretch(0, 1)
        self.verticalLayout_70.setStretch(1, 115)

        self.horizontalLayout_75.addWidget(self.printimggalvoFrame)

        self.printopgalvoFrame = QFrame(self.frame_25)
        self.printopgalvoFrame.setObjectName(u"printopgalvoFrame")
        self.printopgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.printopgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_71 = QVBoxLayout(self.printopgalvoFrame)
        self.verticalLayout_71.setObjectName(u"verticalLayout_71")
        self.label_52 = QLabel(self.printopgalvoFrame)
        self.label_52.setObjectName(u"label_52")
        self.label_52.setMinimumSize(QSize(20, 20))
        self.label_52.setMaximumSize(QSize(80, 20))
        self.label_52.setFont(font5)
        self.label_52.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_71.addWidget(self.label_52)

        self.printrungalvoPushButton = QPushButton(self.printopgalvoFrame)
        self.printrungalvoPushButton.setObjectName(u"printrungalvoPushButton")
        sizePolicy6.setHeightForWidth(self.printrungalvoPushButton.sizePolicy().hasHeightForWidth())
        self.printrungalvoPushButton.setSizePolicy(sizePolicy6)
        self.printrungalvoPushButton.setFont(font10)
        self.printrungalvoPushButton.setStyleSheet(u"QPushButton {\n"
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
        self.printrungalvoPushButton.setIcon(icon19)
        self.printrungalvoPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_71.addWidget(self.printrungalvoPushButton)

        self.printabortgalvoPushButton = QPushButton(self.printopgalvoFrame)
        self.printabortgalvoPushButton.setObjectName(u"printabortgalvoPushButton")
        self.printabortgalvoPushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.printabortgalvoPushButton.sizePolicy().hasHeightForWidth())
        self.printabortgalvoPushButton.setSizePolicy(sizePolicy6)
        self.printabortgalvoPushButton.setFont(font10)
        self.printabortgalvoPushButton.setStyleSheet(u"QPushButton {\n"
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
        self.printabortgalvoPushButton.setIcon(icon17)
        self.printabortgalvoPushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_71.addWidget(self.printabortgalvoPushButton)

        self.redlightprePushButton = QPushButton(self.printopgalvoFrame)
        self.redlightprePushButton.setObjectName(u"redlightprePushButton")
        sizePolicy6.setHeightForWidth(self.redlightprePushButton.sizePolicy().hasHeightForWidth())
        self.redlightprePushButton.setSizePolicy(sizePolicy6)
        self.redlightprePushButton.setFont(font10)
        self.redlightprePushButton.setStyleSheet(u"QPushButton {\n"
"	color: rgb(255, 255, 255);	\n"
"	background-color: rgb(16, 42, 131);\n"
"	border-color: transparent;\n"
"	border-style: outset;\n"
"	border-radius: 20px;\n"
"	border-width: 2px;\n"
"	\n"
"	/* --- THE ICON SETTINGS --- */\n"
"	background-image: url(:/icons/icons/aperture.svg); \n"
"	background-repeat: no-repeat;\n"
"	background-position: center 8px; \n"
"	\n"
"	/* --- PUSHES TEXT DOWN TO MAKE ROOM FOR ICON --- */\n"
"	padding-top: 55px;  /* Increased to 55px to add space between icon and text */\n"
"	padding-bottom: 6px;\n"
"	padding-left: 6px;\n"
"	padding-right: 6px;\n"
"	text-align: center;\n"
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
        self.redlightprePushButton.setIconSize(QSize(32, 32))

        self.verticalLayout_71.addWidget(self.redlightprePushButton)


        self.horizontalLayout_75.addWidget(self.printopgalvoFrame)

        self.horizontalLayout_75.setStretch(0, 4)

        self.verticalLayout_69.addWidget(self.frame_25)

        self.printprogressgalvoFrame = QFrame(self.printgalvoFrame)
        self.printprogressgalvoFrame.setObjectName(u"printprogressgalvoFrame")
        sizePolicy6.setHeightForWidth(self.printprogressgalvoFrame.sizePolicy().hasHeightForWidth())
        self.printprogressgalvoFrame.setSizePolicy(sizePolicy6)
        self.printprogressgalvoFrame.setMaximumSize(QSize(16777215, 60))
        self.printprogressgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.printprogressgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_76 = QHBoxLayout(self.printprogressgalvoFrame)
        self.horizontalLayout_76.setSpacing(10)
        self.horizontalLayout_76.setObjectName(u"horizontalLayout_76")
        self.horizontalLayout_76.setContentsMargins(5, -1, 5, -1)
        self.label_53 = QLabel(self.printprogressgalvoFrame)
        self.label_53.setObjectName(u"label_53")
        self.label_53.setMinimumSize(QSize(0, 0))
        self.label_53.setMaximumSize(QSize(75, 16777215))
        self.label_53.setFont(font5)
        self.label_53.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_76.addWidget(self.label_53)

        self.printgalvoProgressBar = QProgressBar(self.printprogressgalvoFrame)
        self.printgalvoProgressBar.setObjectName(u"printgalvoProgressBar")
        self.printgalvoProgressBar.setFont(font5)
        self.printgalvoProgressBar.setStyleSheet(u"QProgressBar {\n"
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
        self.printgalvoProgressBar.setValue(100)
        self.printgalvoProgressBar.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.printgalvoProgressBar.setTextDirection(QProgressBar.Direction.TopToBottom)

        self.horizontalLayout_76.addWidget(self.printgalvoProgressBar)

        self.progressLabel_2 = QLabel(self.printprogressgalvoFrame)
        self.progressLabel_2.setObjectName(u"progressLabel_2")
        self.progressLabel_2.setFont(font5)
        self.progressLabel_2.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")
        self.progressLabel_2.setScaledContents(False)
        self.progressLabel_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_76.addWidget(self.progressLabel_2)


        self.verticalLayout_69.addWidget(self.printprogressgalvoFrame)

        self.verticalLayout_69.setStretch(0, 5)
        self.verticalLayout_69.setStretch(1, 1)

        self.verticalLayout_74.addWidget(self.printgalvoFrame)

        self.mainPages.addWidget(self.printgalvoPage)
        self.configgalvoPage = QWidget()
        self.configgalvoPage.setObjectName(u"configgalvoPage")
        self.verticalLayout_68 = QVBoxLayout(self.configgalvoPage)
        self.verticalLayout_68.setObjectName(u"verticalLayout_68")
        self.page3Label_7 = QLabel(self.configgalvoPage)
        self.page3Label_7.setObjectName(u"page3Label_7")
        self.page3Label_7.setMinimumSize(QSize(0, 20))
        self.page3Label_7.setMaximumSize(QSize(16777215, 20))
        self.page3Label_7.setFont(font2)
        self.page3Label_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_68.addWidget(self.page3Label_7)

        self.configgalveFrame = QFrame(self.configgalvoPage)
        self.configgalveFrame.setObjectName(u"configgalveFrame")
        self.configgalveFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.configgalveFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_122 = QHBoxLayout(self.configgalveFrame)
        self.horizontalLayout_122.setObjectName(u"horizontalLayout_122")
        self.horizontalLayout_122.setContentsMargins(0, -1, -1, -1)
        self.scrollArea_2 = QScrollArea(self.configgalveFrame)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, -354, 613, 687))
        self.verticalLayout_85 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_85.setObjectName(u"verticalLayout_85")
        self.frame_42 = QFrame(self.scrollAreaWidgetContents_2)
        self.frame_42.setObjectName(u"frame_42")
        self.frame_42.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_42.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_95 = QHBoxLayout(self.frame_42)
        self.horizontalLayout_95.setObjectName(u"horizontalLayout_95")
        self.horizontalLayout_95.setContentsMargins(0, 0, 0, 0)
        self.frame_43 = QFrame(self.frame_42)
        self.frame_43.setObjectName(u"frame_43")
        self.frame_43.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_43.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_78 = QVBoxLayout(self.frame_43)
        self.verticalLayout_78.setObjectName(u"verticalLayout_78")
        self.verticalLayout_78.setContentsMargins(0, 0, 0, 0)
        self.aspectgalvoFrame = QFrame(self.frame_43)
        self.aspectgalvoFrame.setObjectName(u"aspectgalvoFrame")
        self.aspectgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.aspectgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_83 = QVBoxLayout(self.aspectgalvoFrame)
        self.verticalLayout_83.setObjectName(u"verticalLayout_83")
        self.verticalLayout_83.setContentsMargins(0, 0, 0, 0)
        self.label_82 = QLabel(self.aspectgalvoFrame)
        self.label_82.setObjectName(u"label_82")
        self.label_82.setFont(font5)
        self.label_82.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_83.addWidget(self.label_82, 0, Qt.AlignmentFlag.AlignHCenter)

        self.frame_48 = QFrame(self.aspectgalvoFrame)
        self.frame_48.setObjectName(u"frame_48")
        self.frame_48.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_48.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_105 = QHBoxLayout(self.frame_48)
        self.horizontalLayout_105.setObjectName(u"horizontalLayout_105")
        self.horizontalLayout_105.setContentsMargins(0, 0, 0, 0)
        self.frame_47 = QFrame(self.frame_48)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_47.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_79 = QVBoxLayout(self.frame_47)
        self.verticalLayout_79.setObjectName(u"verticalLayout_79")
        self.verticalLayout_79.setContentsMargins(0, 0, 0, 0)
        self.frame_271 = QFrame(self.frame_47)
        self.frame_271.setObjectName(u"frame_271")
        self.horizontalLayout_97 = QHBoxLayout(self.frame_271)
        self.horizontalLayout_97.setObjectName(u"horizontalLayout_97")
        self.label_34 = QLabel(self.frame_271)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setMaximumSize(QSize(16777215, 16777215))
        self.label_34.setFont(font9)
        self.label_34.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_97.addWidget(self.label_34)

        self.fieldsizeconfLineEdit = QLineEdit(self.frame_271)
        self.fieldsizeconfLineEdit.setObjectName(u"fieldsizeconfLineEdit")
        sizePolicy6.setHeightForWidth(self.fieldsizeconfLineEdit.sizePolicy().hasHeightForWidth())
        self.fieldsizeconfLineEdit.setSizePolicy(sizePolicy6)
        self.fieldsizeconfLineEdit.setMinimumSize(QSize(0, 0))
        self.fieldsizeconfLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.fieldsizeconfLineEdit.setFont(font9)
        self.fieldsizeconfLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.fieldsizeconfLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_97.addWidget(self.fieldsizeconfLineEdit)

        self.label_104 = QLabel(self.frame_271)
        self.label_104.setObjectName(u"label_104")
        self.label_104.setFont(font9)
        self.label_104.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_97.addWidget(self.label_104)

        self.horizontalLayout_97.setStretch(0, 2)
        self.horizontalLayout_97.setStretch(1, 3)

        self.verticalLayout_79.addWidget(self.frame_271)

        self.frame_281 = QFrame(self.frame_47)
        self.frame_281.setObjectName(u"frame_281")
        self.horizontalLayout_98 = QHBoxLayout(self.frame_281)
        self.horizontalLayout_98.setObjectName(u"horizontalLayout_98")
        self.label_35 = QLabel(self.frame_281)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setMaximumSize(QSize(16777215, 16777215))
        self.label_35.setFont(font9)
        self.label_35.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_98.addWidget(self.label_35)

        self.offxconfLineEdit = QLineEdit(self.frame_281)
        self.offxconfLineEdit.setObjectName(u"offxconfLineEdit")
        sizePolicy6.setHeightForWidth(self.offxconfLineEdit.sizePolicy().hasHeightForWidth())
        self.offxconfLineEdit.setSizePolicy(sizePolicy6)
        self.offxconfLineEdit.setMinimumSize(QSize(0, 0))
        self.offxconfLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.offxconfLineEdit.setFont(font9)
        self.offxconfLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.offxconfLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_98.addWidget(self.offxconfLineEdit)

        self.label_105 = QLabel(self.frame_281)
        self.label_105.setObjectName(u"label_105")
        self.label_105.setFont(font9)
        self.label_105.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_98.addWidget(self.label_105)

        self.horizontalLayout_98.setStretch(0, 2)
        self.horizontalLayout_98.setStretch(1, 3)

        self.verticalLayout_79.addWidget(self.frame_281)

        self.frame_291 = QFrame(self.frame_47)
        self.frame_291.setObjectName(u"frame_291")
        self.horizontalLayout_99 = QHBoxLayout(self.frame_291)
        self.horizontalLayout_99.setObjectName(u"horizontalLayout_99")
        self.label_42 = QLabel(self.frame_291)
        self.label_42.setObjectName(u"label_42")
        self.label_42.setMaximumSize(QSize(16777215, 16777215))
        self.label_42.setFont(font9)
        self.label_42.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_99.addWidget(self.label_42)

        self.offyconfLineEdit = QLineEdit(self.frame_291)
        self.offyconfLineEdit.setObjectName(u"offyconfLineEdit")
        sizePolicy6.setHeightForWidth(self.offyconfLineEdit.sizePolicy().hasHeightForWidth())
        self.offyconfLineEdit.setSizePolicy(sizePolicy6)
        self.offyconfLineEdit.setMinimumSize(QSize(0, 0))
        self.offyconfLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.offyconfLineEdit.setFont(font9)
        self.offyconfLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.offyconfLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_99.addWidget(self.offyconfLineEdit)

        self.label_106 = QLabel(self.frame_291)
        self.label_106.setObjectName(u"label_106")
        self.label_106.setFont(font9)
        self.label_106.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_99.addWidget(self.label_106)

        self.horizontalLayout_99.setStretch(0, 2)
        self.horizontalLayout_99.setStretch(1, 3)

        self.verticalLayout_79.addWidget(self.frame_291)

        self.frame_391 = QFrame(self.frame_47)
        self.frame_391.setObjectName(u"frame_391")
        self.horizontalLayout_106 = QHBoxLayout(self.frame_391)
        self.horizontalLayout_106.setObjectName(u"horizontalLayout_106")
        self.label_46 = QLabel(self.frame_391)
        self.label_46.setObjectName(u"label_46")
        self.label_46.setMaximumSize(QSize(16777215, 16777215))
        self.label_46.setFont(font9)
        self.label_46.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_106.addWidget(self.label_46)

        self.angleconfLineEdit = QLineEdit(self.frame_391)
        self.angleconfLineEdit.setObjectName(u"angleconfLineEdit")
        sizePolicy6.setHeightForWidth(self.angleconfLineEdit.sizePolicy().hasHeightForWidth())
        self.angleconfLineEdit.setSizePolicy(sizePolicy6)
        self.angleconfLineEdit.setMinimumSize(QSize(0, 0))
        self.angleconfLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.angleconfLineEdit.setFont(font9)
        self.angleconfLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.angleconfLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_106.addWidget(self.angleconfLineEdit)

        self.label_107 = QLabel(self.frame_391)
        self.label_107.setObjectName(u"label_107")
        font15 = QFont()
        font15.setPointSize(21)
        font15.setBold(True)
        self.label_107.setFont(font15)
        self.label_107.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")

        self.horizontalLayout_106.addWidget(self.label_107, 0, Qt.AlignmentFlag.AlignHCenter)

        self.horizontalLayout_106.setStretch(0, 2)
        self.horizontalLayout_106.setStretch(1, 4)

        self.verticalLayout_79.addWidget(self.frame_391)


        self.horizontalLayout_105.addWidget(self.frame_47)

        self.frame_49 = QFrame(self.frame_48)
        self.frame_49.setObjectName(u"frame_49")
        self.frame_49.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_49.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_81 = QVBoxLayout(self.frame_49)
        self.verticalLayout_81.setObjectName(u"verticalLayout_81")
        self.verticalLayout_81.setContentsMargins(0, 0, 0, 0)
        self.frame_362 = QFrame(self.frame_49)
        self.frame_362.setObjectName(u"frame_362")
        self.horizontalLayout_101 = QHBoxLayout(self.frame_362)
        self.horizontalLayout_101.setObjectName(u"horizontalLayout_101")
        self.galvo1confRadioButton = QRadioButton(self.frame_362)
        self.galvo1confRadioButton.setObjectName(u"galvo1confRadioButton")

        self.horizontalLayout_101.addWidget(self.galvo1confRadioButton)

        self.label_43 = QLabel(self.frame_362)
        self.label_43.setObjectName(u"label_43")
        self.label_43.setMaximumSize(QSize(16777215, 16777215))
        self.label_43.setFont(font9)
        self.label_43.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_101.addWidget(self.label_43)


        self.verticalLayout_81.addWidget(self.frame_362)

        self.frame_371 = QFrame(self.frame_49)
        self.frame_371.setObjectName(u"frame_371")
        self.horizontalLayout_104 = QHBoxLayout(self.frame_371)
        self.horizontalLayout_104.setObjectName(u"horizontalLayout_104")
        self.galvo2confRadioButton = QRadioButton(self.frame_371)
        self.galvo2confRadioButton.setObjectName(u"galvo2confRadioButton")

        self.horizontalLayout_104.addWidget(self.galvo2confRadioButton)

        self.label_44 = QLabel(self.frame_371)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setMaximumSize(QSize(16777215, 16777215))
        self.label_44.setFont(font9)
        self.label_44.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_104.addWidget(self.label_44)


        self.verticalLayout_81.addWidget(self.frame_371)

        self.verticalSpacer_9 = QSpacerItem(20, 140, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_81.addItem(self.verticalSpacer_9)


        self.horizontalLayout_105.addWidget(self.frame_49)


        self.verticalLayout_83.addWidget(self.frame_48)


        self.verticalLayout_78.addWidget(self.aspectgalvoFrame)

        self.galvoconfigFrame = QFrame(self.frame_43)
        self.galvoconfigFrame.setObjectName(u"galvoconfigFrame")
        self.galvoconfigFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.galvoconfigFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_121 = QHBoxLayout(self.galvoconfigFrame)
        self.horizontalLayout_121.setObjectName(u"horizontalLayout_121")
        self.horizontalLayout_121.setContentsMargins(0, 0, 0, 0)
        self.galvo1Frame = QFrame(self.galvoconfigFrame)
        self.galvo1Frame.setObjectName(u"galvo1Frame")
        self.galvo1Frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.galvo1Frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_84 = QVBoxLayout(self.galvo1Frame)
        self.verticalLayout_84.setObjectName(u"verticalLayout_84")
        self.label_88 = QLabel(self.galvo1Frame)
        self.label_88.setObjectName(u"label_88")
        self.label_88.setFont(font5)
        self.label_88.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_84.addWidget(self.label_88, 0, Qt.AlignmentFlag.AlignHCenter)

        self.frame_59 = QFrame(self.galvo1Frame)
        self.frame_59.setObjectName(u"frame_59")
        self.frame_59.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_59.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_112 = QHBoxLayout(self.frame_59)
        self.horizontalLayout_112.setObjectName(u"horizontalLayout_112")
        self.horizontalLayout_112.setContentsMargins(0, -1, 0, -1)
        self.label_94 = QLabel(self.frame_59)
        self.label_94.setObjectName(u"label_94")
        self.label_94.setMaximumSize(QSize(130, 16777215))
        self.label_94.setFont(font9)
        self.label_94.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_112.addWidget(self.label_94)

        self.neggalvo1confCheckBox = QCheckBox(self.frame_59)
        self.neggalvo1confCheckBox.setObjectName(u"neggalvo1confCheckBox")

        self.horizontalLayout_112.addWidget(self.neggalvo1confCheckBox)


        self.verticalLayout_84.addWidget(self.frame_59)

        self.frame_421 = QFrame(self.galvo1Frame)
        self.frame_421.setObjectName(u"frame_421")
        self.horizontalLayout_114 = QHBoxLayout(self.frame_421)
        self.horizontalLayout_114.setObjectName(u"horizontalLayout_114")
        self.horizontalLayout_114.setContentsMargins(0, -1, 0, -1)
        self.label_96 = QLabel(self.frame_421)
        self.label_96.setObjectName(u"label_96")
        self.label_96.setMaximumSize(QSize(16777215, 16777215))
        self.label_96.setFont(font9)
        self.label_96.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_114.addWidget(self.label_96)

        self.confscalegalvo1LineEdit = QLineEdit(self.frame_421)
        self.confscalegalvo1LineEdit.setObjectName(u"confscalegalvo1LineEdit")
        sizePolicy6.setHeightForWidth(self.confscalegalvo1LineEdit.sizePolicy().hasHeightForWidth())
        self.confscalegalvo1LineEdit.setSizePolicy(sizePolicy6)
        self.confscalegalvo1LineEdit.setMinimumSize(QSize(0, 0))
        self.confscalegalvo1LineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.confscalegalvo1LineEdit.setFont(font9)
        self.confscalegalvo1LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confscalegalvo1LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_114.addWidget(self.confscalegalvo1LineEdit)

        self.confscalegalvo1PushButton = QPushButton(self.frame_421)
        self.confscalegalvo1PushButton.setObjectName(u"confscalegalvo1PushButton")
        self.confscalegalvo1PushButton.setFont(font9)
        self.confscalegalvo1PushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_114.addWidget(self.confscalegalvo1PushButton)


        self.verticalLayout_84.addWidget(self.frame_421)

        self.frame_44 = QFrame(self.galvo1Frame)
        self.frame_44.setObjectName(u"frame_44")
        self.horizontalLayout_116 = QHBoxLayout(self.frame_44)
        self.horizontalLayout_116.setObjectName(u"horizontalLayout_116")
        self.horizontalLayout_116.setContentsMargins(0, -1, 0, -1)
        self.label_98 = QLabel(self.frame_44)
        self.label_98.setObjectName(u"label_98")
        self.label_98.setMaximumSize(QSize(16777215, 16777215))
        self.label_98.setFont(font9)
        self.label_98.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_116.addWidget(self.label_98)

        self.confbargalvo1LineEdit = QLineEdit(self.frame_44)
        self.confbargalvo1LineEdit.setObjectName(u"confbargalvo1LineEdit")
        sizePolicy6.setHeightForWidth(self.confbargalvo1LineEdit.sizePolicy().hasHeightForWidth())
        self.confbargalvo1LineEdit.setSizePolicy(sizePolicy6)
        self.confbargalvo1LineEdit.setMinimumSize(QSize(0, 0))
        self.confbargalvo1LineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.confbargalvo1LineEdit.setFont(font9)
        self.confbargalvo1LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confbargalvo1LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_116.addWidget(self.confbargalvo1LineEdit)

        self.horizontalLayout_116.setStretch(0, 3)
        self.horizontalLayout_116.setStretch(1, 2)

        self.verticalLayout_84.addWidget(self.frame_44)

        self.frame_431 = QFrame(self.galvo1Frame)
        self.frame_431.setObjectName(u"frame_431")
        self.horizontalLayout_115 = QHBoxLayout(self.frame_431)
        self.horizontalLayout_115.setObjectName(u"horizontalLayout_115")
        self.horizontalLayout_115.setContentsMargins(0, -1, 0, -1)
        self.label_97 = QLabel(self.frame_431)
        self.label_97.setObjectName(u"label_97")
        self.label_97.setMaximumSize(QSize(16777215, 16777215))
        self.label_97.setFont(font9)
        self.label_97.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_115.addWidget(self.label_97)

        self.confpargalvo1LineEdit = QLineEdit(self.frame_431)
        self.confpargalvo1LineEdit.setObjectName(u"confpargalvo1LineEdit")
        sizePolicy6.setHeightForWidth(self.confpargalvo1LineEdit.sizePolicy().hasHeightForWidth())
        self.confpargalvo1LineEdit.setSizePolicy(sizePolicy6)
        self.confpargalvo1LineEdit.setMinimumSize(QSize(0, 0))
        self.confpargalvo1LineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.confpargalvo1LineEdit.setFont(font9)
        self.confpargalvo1LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confpargalvo1LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_115.addWidget(self.confpargalvo1LineEdit)

        self.horizontalLayout_115.setStretch(0, 3)
        self.horizontalLayout_115.setStretch(1, 2)

        self.verticalLayout_84.addWidget(self.frame_431)

        self.frame_491 = QFrame(self.galvo1Frame)
        self.frame_491.setObjectName(u"frame_491")
        self.horizontalLayout_123 = QHBoxLayout(self.frame_491)
        self.horizontalLayout_123.setObjectName(u"horizontalLayout_123")
        self.horizontalLayout_123.setContentsMargins(0, -1, 0, -1)
        self.label_103 = QLabel(self.frame_491)
        self.label_103.setObjectName(u"label_103")
        self.label_103.setMaximumSize(QSize(16777215, 16777215))
        self.label_103.setFont(font9)
        self.label_103.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_123.addWidget(self.label_103)

        self.conftrapgalvo1LineEdit = QLineEdit(self.frame_491)
        self.conftrapgalvo1LineEdit.setObjectName(u"conftrapgalvo1LineEdit")
        sizePolicy6.setHeightForWidth(self.conftrapgalvo1LineEdit.sizePolicy().hasHeightForWidth())
        self.conftrapgalvo1LineEdit.setSizePolicy(sizePolicy6)
        self.conftrapgalvo1LineEdit.setMinimumSize(QSize(0, 0))
        self.conftrapgalvo1LineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.conftrapgalvo1LineEdit.setFont(font9)
        self.conftrapgalvo1LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.conftrapgalvo1LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_123.addWidget(self.conftrapgalvo1LineEdit)

        self.horizontalLayout_123.setStretch(0, 3)
        self.horizontalLayout_123.setStretch(1, 2)

        self.verticalLayout_84.addWidget(self.frame_491)


        self.horizontalLayout_121.addWidget(self.galvo1Frame)

        self.galvo2Frame = QFrame(self.galvoconfigFrame)
        self.galvo2Frame.setObjectName(u"galvo2Frame")
        self.galvo2Frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.galvo2Frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_80 = QVBoxLayout(self.galvo2Frame)
        self.verticalLayout_80.setObjectName(u"verticalLayout_80")
        self.label_89 = QLabel(self.galvo2Frame)
        self.label_89.setObjectName(u"label_89")
        self.label_89.setFont(font5)
        self.label_89.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_80.addWidget(self.label_89, 0, Qt.AlignmentFlag.AlignHCenter)

        self.frame_60 = QFrame(self.galvo2Frame)
        self.frame_60.setObjectName(u"frame_60")
        self.frame_60.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_60.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_113 = QHBoxLayout(self.frame_60)
        self.horizontalLayout_113.setObjectName(u"horizontalLayout_113")
        self.horizontalLayout_113.setContentsMargins(0, -1, 0, -1)
        self.label_95 = QLabel(self.frame_60)
        self.label_95.setObjectName(u"label_95")
        self.label_95.setMaximumSize(QSize(130, 16777215))
        self.label_95.setFont(font9)
        self.label_95.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_113.addWidget(self.label_95)

        self.neggalvo2confCheckBox = QCheckBox(self.frame_60)
        self.neggalvo2confCheckBox.setObjectName(u"neggalvo2confCheckBox")

        self.horizontalLayout_113.addWidget(self.neggalvo2confCheckBox)


        self.verticalLayout_80.addWidget(self.frame_60)

        self.frame_45 = QFrame(self.galvo2Frame)
        self.frame_45.setObjectName(u"frame_45")
        self.horizontalLayout_117 = QHBoxLayout(self.frame_45)
        self.horizontalLayout_117.setObjectName(u"horizontalLayout_117")
        self.horizontalLayout_117.setContentsMargins(0, -1, 0, -1)
        self.label_99 = QLabel(self.frame_45)
        self.label_99.setObjectName(u"label_99")
        self.label_99.setMaximumSize(QSize(16777215, 16777215))
        self.label_99.setFont(font9)
        self.label_99.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_117.addWidget(self.label_99)

        self.confscalegalvo2LineEdit = QLineEdit(self.frame_45)
        self.confscalegalvo2LineEdit.setObjectName(u"confscalegalvo2LineEdit")
        sizePolicy6.setHeightForWidth(self.confscalegalvo2LineEdit.sizePolicy().hasHeightForWidth())
        self.confscalegalvo2LineEdit.setSizePolicy(sizePolicy6)
        self.confscalegalvo2LineEdit.setMinimumSize(QSize(0, 0))
        self.confscalegalvo2LineEdit.setMaximumSize(QSize(16777215, 100))
        self.confscalegalvo2LineEdit.setFont(font9)
        self.confscalegalvo2LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confscalegalvo2LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_117.addWidget(self.confscalegalvo2LineEdit)

        self.confscalegalvo2PushButton = QPushButton(self.frame_45)
        self.confscalegalvo2PushButton.setObjectName(u"confscalegalvo2PushButton")
        self.confscalegalvo2PushButton.setFont(font9)
        self.confscalegalvo2PushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_117.addWidget(self.confscalegalvo2PushButton)


        self.verticalLayout_80.addWidget(self.frame_45)

        self.frame_46 = QFrame(self.galvo2Frame)
        self.frame_46.setObjectName(u"frame_46")
        self.horizontalLayout_118 = QHBoxLayout(self.frame_46)
        self.horizontalLayout_118.setObjectName(u"horizontalLayout_118")
        self.horizontalLayout_118.setContentsMargins(0, -1, 0, -1)
        self.label_100 = QLabel(self.frame_46)
        self.label_100.setObjectName(u"label_100")
        self.label_100.setMaximumSize(QSize(16777215, 16777215))
        self.label_100.setFont(font9)
        self.label_100.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_118.addWidget(self.label_100)

        self.confbargalvo2LineEdit = QLineEdit(self.frame_46)
        self.confbargalvo2LineEdit.setObjectName(u"confbargalvo2LineEdit")
        sizePolicy6.setHeightForWidth(self.confbargalvo2LineEdit.sizePolicy().hasHeightForWidth())
        self.confbargalvo2LineEdit.setSizePolicy(sizePolicy6)
        self.confbargalvo2LineEdit.setMinimumSize(QSize(0, 0))
        self.confbargalvo2LineEdit.setMaximumSize(QSize(16777215, 100))
        self.confbargalvo2LineEdit.setFont(font9)
        self.confbargalvo2LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confbargalvo2LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_118.addWidget(self.confbargalvo2LineEdit)

        self.horizontalLayout_118.setStretch(0, 3)
        self.horizontalLayout_118.setStretch(1, 2)

        self.verticalLayout_80.addWidget(self.frame_46)

        self.frame_471 = QFrame(self.galvo2Frame)
        self.frame_471.setObjectName(u"frame_471")
        self.horizontalLayout_119 = QHBoxLayout(self.frame_471)
        self.horizontalLayout_119.setObjectName(u"horizontalLayout_119")
        self.horizontalLayout_119.setContentsMargins(0, -1, 0, -1)
        self.label_101 = QLabel(self.frame_471)
        self.label_101.setObjectName(u"label_101")
        self.label_101.setMaximumSize(QSize(16777215, 16777215))
        self.label_101.setFont(font9)
        self.label_101.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_119.addWidget(self.label_101)

        self.confpargalvo2LineEdit = QLineEdit(self.frame_471)
        self.confpargalvo2LineEdit.setObjectName(u"confpargalvo2LineEdit")
        sizePolicy6.setHeightForWidth(self.confpargalvo2LineEdit.sizePolicy().hasHeightForWidth())
        self.confpargalvo2LineEdit.setSizePolicy(sizePolicy6)
        self.confpargalvo2LineEdit.setMinimumSize(QSize(0, 0))
        self.confpargalvo2LineEdit.setMaximumSize(QSize(16777215, 100))
        self.confpargalvo2LineEdit.setFont(font9)
        self.confpargalvo2LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confpargalvo2LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_119.addWidget(self.confpargalvo2LineEdit)

        self.horizontalLayout_119.setStretch(0, 3)
        self.horizontalLayout_119.setStretch(1, 2)

        self.verticalLayout_80.addWidget(self.frame_471)

        self.frame_481 = QFrame(self.galvo2Frame)
        self.frame_481.setObjectName(u"frame_481")
        self.horizontalLayout_120 = QHBoxLayout(self.frame_481)
        self.horizontalLayout_120.setObjectName(u"horizontalLayout_120")
        self.horizontalLayout_120.setContentsMargins(0, -1, 0, -1)
        self.label_102 = QLabel(self.frame_481)
        self.label_102.setObjectName(u"label_102")
        self.label_102.setMaximumSize(QSize(16777215, 16777215))
        self.label_102.setFont(font9)
        self.label_102.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_120.addWidget(self.label_102)

        self.conftrapgalvo2LineEdit = QLineEdit(self.frame_481)
        self.conftrapgalvo2LineEdit.setObjectName(u"conftrapgalvo2LineEdit")
        sizePolicy6.setHeightForWidth(self.conftrapgalvo2LineEdit.sizePolicy().hasHeightForWidth())
        self.conftrapgalvo2LineEdit.setSizePolicy(sizePolicy6)
        self.conftrapgalvo2LineEdit.setMinimumSize(QSize(0, 0))
        self.conftrapgalvo2LineEdit.setMaximumSize(QSize(16777215, 100))
        self.conftrapgalvo2LineEdit.setFont(font9)
        self.conftrapgalvo2LineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.conftrapgalvo2LineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_120.addWidget(self.conftrapgalvo2LineEdit)

        self.horizontalLayout_120.setStretch(0, 3)
        self.horizontalLayout_120.setStretch(1, 2)

        self.verticalLayout_80.addWidget(self.frame_481)


        self.horizontalLayout_121.addWidget(self.galvo2Frame)


        self.verticalLayout_78.addWidget(self.galvoconfigFrame)


        self.horizontalLayout_95.addWidget(self.frame_43)

        self.goposgalvoFrame = QFrame(self.frame_42)
        self.goposgalvoFrame.setObjectName(u"goposgalvoFrame")
        self.goposgalvoFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.goposgalvoFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_82 = QVBoxLayout(self.goposgalvoFrame)
        self.verticalLayout_82.setObjectName(u"verticalLayout_82")
        self.label_84 = QLabel(self.goposgalvoFrame)
        self.label_84.setObjectName(u"label_84")
        self.label_84.setFont(font5)
        self.label_84.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_82.addWidget(self.label_84)

        self.frame_50 = QFrame(self.goposgalvoFrame)
        self.frame_50.setObjectName(u"frame_50")
        self.frame_50.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_50.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_96 = QHBoxLayout(self.frame_50)
        self.horizontalLayout_96.setObjectName(u"horizontalLayout_96")
        self.horizontalLayout_96.setContentsMargins(0, -1, 0, -1)
        self.confnomovRadioButton = QRadioButton(self.frame_50)
        self.confnomovRadioButton.setObjectName(u"confnomovRadioButton")

        self.horizontalLayout_96.addWidget(self.confnomovRadioButton)

        self.label_83 = QLabel(self.frame_50)
        self.label_83.setObjectName(u"label_83")
        self.label_83.setMaximumSize(QSize(130, 16777215))
        self.label_83.setFont(font9)
        self.label_83.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_96.addWidget(self.label_83)

        self.horizontalLayout_96.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_50)

        self.frame_52 = QFrame(self.goposgalvoFrame)
        self.frame_52.setObjectName(u"frame_52")
        self.frame_52.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_52.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_102 = QHBoxLayout(self.frame_52)
        self.horizontalLayout_102.setObjectName(u"horizontalLayout_102")
        self.horizontalLayout_102.setContentsMargins(0, -1, 0, -1)
        self.confgalvocentRadioButton = QRadioButton(self.frame_52)
        self.confgalvocentRadioButton.setObjectName(u"confgalvocentRadioButton")

        self.horizontalLayout_102.addWidget(self.confgalvocentRadioButton)

        self.label_86 = QLabel(self.frame_52)
        self.label_86.setObjectName(u"label_86")
        self.label_86.setMaximumSize(QSize(130, 16777215))
        self.label_86.setFont(font9)
        self.label_86.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_102.addWidget(self.label_86)

        self.horizontalLayout_102.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_52)

        self.frame_51 = QFrame(self.goposgalvoFrame)
        self.frame_51.setObjectName(u"frame_51")
        self.frame_51.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_51.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_100 = QHBoxLayout(self.frame_51)
        self.horizontalLayout_100.setObjectName(u"horizontalLayout_100")
        self.horizontalLayout_100.setContentsMargins(0, -1, 0, -1)
        self.conftopleftRadioButton = QRadioButton(self.frame_51)
        self.conftopleftRadioButton.setObjectName(u"conftopleftRadioButton")

        self.horizontalLayout_100.addWidget(self.conftopleftRadioButton)

        self.label_85 = QLabel(self.frame_51)
        self.label_85.setObjectName(u"label_85")
        self.label_85.setMaximumSize(QSize(130, 16777215))
        self.label_85.setFont(font9)
        self.label_85.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_100.addWidget(self.label_85)

        self.horizontalLayout_100.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_51)

        self.frame_53 = QFrame(self.goposgalvoFrame)
        self.frame_53.setObjectName(u"frame_53")
        self.frame_53.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_53.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_103 = QHBoxLayout(self.frame_53)
        self.horizontalLayout_103.setObjectName(u"horizontalLayout_103")
        self.horizontalLayout_103.setContentsMargins(0, -1, 0, -1)
        self.conftoprightRadioButton = QRadioButton(self.frame_53)
        self.conftoprightRadioButton.setObjectName(u"conftoprightRadioButton")

        self.horizontalLayout_103.addWidget(self.conftoprightRadioButton)

        self.label_87 = QLabel(self.frame_53)
        self.label_87.setObjectName(u"label_87")
        self.label_87.setMaximumSize(QSize(130, 16777215))
        self.label_87.setFont(font9)
        self.label_87.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_103.addWidget(self.label_87)

        self.horizontalLayout_103.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_53)

        self.frame_56 = QFrame(self.goposgalvoFrame)
        self.frame_56.setObjectName(u"frame_56")
        self.frame_56.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_56.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_107 = QHBoxLayout(self.frame_56)
        self.horizontalLayout_107.setObjectName(u"horizontalLayout_107")
        self.horizontalLayout_107.setContentsMargins(0, -1, 0, -1)
        self.confbotrightRadioButton = QRadioButton(self.frame_56)
        self.confbotrightRadioButton.setObjectName(u"confbotrightRadioButton")

        self.horizontalLayout_107.addWidget(self.confbotrightRadioButton)

        self.label_90 = QLabel(self.frame_56)
        self.label_90.setObjectName(u"label_90")
        self.label_90.setMaximumSize(QSize(130, 16777215))
        self.label_90.setFont(font9)
        self.label_90.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_107.addWidget(self.label_90)

        self.horizontalLayout_107.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_56)

        self.frame_57 = QFrame(self.goposgalvoFrame)
        self.frame_57.setObjectName(u"frame_57")
        self.frame_57.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_57.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_110 = QHBoxLayout(self.frame_57)
        self.horizontalLayout_110.setObjectName(u"horizontalLayout_110")
        self.horizontalLayout_110.setContentsMargins(0, -1, 0, -1)
        self.confbotleftRadioButton = QRadioButton(self.frame_57)
        self.confbotleftRadioButton.setObjectName(u"confbotleftRadioButton")

        self.horizontalLayout_110.addWidget(self.confbotleftRadioButton)

        self.label_92 = QLabel(self.frame_57)
        self.label_92.setObjectName(u"label_92")
        self.label_92.setMaximumSize(QSize(130, 16777215))
        self.label_92.setFont(font9)
        self.label_92.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_110.addWidget(self.label_92)

        self.horizontalLayout_110.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_57)

        self.frame_58 = QFrame(self.goposgalvoFrame)
        self.frame_58.setObjectName(u"frame_58")
        self.frame_58.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_58.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_111 = QHBoxLayout(self.frame_58)
        self.horizontalLayout_111.setObjectName(u"horizontalLayout_111")
        self.horizontalLayout_111.setContentsMargins(0, -1, 0, -1)
        self.confspecposRadioButton = QRadioButton(self.frame_58)
        self.confspecposRadioButton.setObjectName(u"confspecposRadioButton")

        self.horizontalLayout_111.addWidget(self.confspecposRadioButton)

        self.label_93 = QLabel(self.frame_58)
        self.label_93.setObjectName(u"label_93")
        self.label_93.setMaximumSize(QSize(130, 16777215))
        self.label_93.setFont(font9)
        self.label_93.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_111.addWidget(self.label_93)

        self.horizontalLayout_111.setStretch(1, 3)

        self.verticalLayout_82.addWidget(self.frame_58)

        self.frame_401 = QFrame(self.goposgalvoFrame)
        self.frame_401.setObjectName(u"frame_401")
        self.horizontalLayout_108 = QHBoxLayout(self.frame_401)
        self.horizontalLayout_108.setObjectName(u"horizontalLayout_108")
        self.horizontalLayout_108.setContentsMargins(0, 0, 0, 9)
        self.label_47 = QLabel(self.frame_401)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setMaximumSize(QSize(16777215, 16777215))
        self.label_47.setFont(font9)
        self.label_47.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_108.addWidget(self.label_47)

        self.confxmarkLineEdit = QLineEdit(self.frame_401)
        self.confxmarkLineEdit.setObjectName(u"confxmarkLineEdit")
        sizePolicy6.setHeightForWidth(self.confxmarkLineEdit.sizePolicy().hasHeightForWidth())
        self.confxmarkLineEdit.setSizePolicy(sizePolicy6)
        self.confxmarkLineEdit.setMinimumSize(QSize(0, 0))
        self.confxmarkLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.confxmarkLineEdit.setFont(font9)
        self.confxmarkLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confxmarkLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_108.addWidget(self.confxmarkLineEdit)

        self.horizontalLayout_108.setStretch(0, 1)
        self.horizontalLayout_108.setStretch(1, 4)

        self.verticalLayout_82.addWidget(self.frame_401)

        self.frame_411 = QFrame(self.goposgalvoFrame)
        self.frame_411.setObjectName(u"frame_411")
        self.horizontalLayout_109 = QHBoxLayout(self.frame_411)
        self.horizontalLayout_109.setObjectName(u"horizontalLayout_109")
        self.horizontalLayout_109.setContentsMargins(0, 9, 0, 9)
        self.label_91 = QLabel(self.frame_411)
        self.label_91.setObjectName(u"label_91")
        self.label_91.setMaximumSize(QSize(16777215, 16777215))
        self.label_91.setFont(font9)
        self.label_91.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.horizontalLayout_109.addWidget(self.label_91)

        self.confymarkLineEdit = QLineEdit(self.frame_411)
        self.confymarkLineEdit.setObjectName(u"confymarkLineEdit")
        sizePolicy6.setHeightForWidth(self.confymarkLineEdit.sizePolicy().hasHeightForWidth())
        self.confymarkLineEdit.setSizePolicy(sizePolicy6)
        self.confymarkLineEdit.setMinimumSize(QSize(0, 0))
        self.confymarkLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.confymarkLineEdit.setFont(font9)
        self.confymarkLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.confymarkLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_109.addWidget(self.confymarkLineEdit)

        self.horizontalLayout_109.setStretch(0, 1)
        self.horizontalLayout_109.setStretch(1, 4)

        self.verticalLayout_82.addWidget(self.frame_411)

        self.verticalSpacer_10 = QSpacerItem(20, 127, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_82.addItem(self.verticalSpacer_10)

        self.verticalLayout_82.setStretch(10, 1)

        self.horizontalLayout_95.addWidget(self.goposgalvoFrame)

        self.horizontalLayout_95.setStretch(0, 10)
        self.horizontalLayout_95.setStretch(1, 2)

        self.verticalLayout_85.addWidget(self.frame_42)

        self.frame_441 = QFrame(self.scrollAreaWidgetContents_2)
        self.frame_441.setObjectName(u"frame_441")
        self.frame_441.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_441.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_94 = QHBoxLayout(self.frame_441)
        self.horizontalLayout_94.setObjectName(u"horizontalLayout_94")
        self.horizontalLayout_94.setContentsMargins(-1, -1, 0, -1)
        self.horizontalSpacer_11 = QSpacerItem(366, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_94.addItem(self.horizontalSpacer_11)

        self.confokPushButton = QPushButton(self.frame_441)
        self.confokPushButton.setObjectName(u"confokPushButton")
        self.confokPushButton.setMinimumSize(QSize(80, 0))
        self.confokPushButton.setMaximumSize(QSize(16777215, 16777215))
        self.confokPushButton.setFont(font2)
        self.confokPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_94.addWidget(self.confokPushButton)

        self.confcancelPushButton = QPushButton(self.frame_441)
        self.confcancelPushButton.setObjectName(u"confcancelPushButton")
        self.confcancelPushButton.setMinimumSize(QSize(80, 0))
        self.confcancelPushButton.setMaximumSize(QSize(200, 16777215))
        self.confcancelPushButton.setFont(font2)
        self.confcancelPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_94.addWidget(self.confcancelPushButton)

        self.confapplyPushButton = QPushButton(self.frame_441)
        self.confapplyPushButton.setObjectName(u"confapplyPushButton")
        self.confapplyPushButton.setMinimumSize(QSize(80, 0))
        self.confapplyPushButton.setFont(font2)
        self.confapplyPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_94.addWidget(self.confapplyPushButton)


        self.verticalLayout_85.addWidget(self.frame_441)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout_122.addWidget(self.scrollArea_2)


        self.verticalLayout_68.addWidget(self.configgalveFrame)

        self.mainPages.addWidget(self.configgalvoPage)
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
        font16 = QFont()
        font16.setPointSize(15)
        self.termsendPushButton.setFont(font16)
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
        icon24 = QIcon()
        icon24.addFile(u":/icons/icons/arrow-right.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.termsendPushButton.setIcon(icon24)
        self.termsendPushButton.setIconSize(QSize(24, 24))

        self.horizontalLayout_31.addWidget(self.termsendPushButton)

        self.horizontalLayout_31.setStretch(0, 4)
        self.horizontalLayout_31.setStretch(1, 1)

        self.verticalLayout_29.addWidget(self.terminalsendFrame)


        self.verticalLayout_34.addWidget(self.terminalFrame)

        self.mainPages.addWidget(self.terminalPage)
        self.ezcadPage = QWidget()
        self.ezcadPage.setObjectName(u"ezcadPage")
        self.verticalLayout_88 = QVBoxLayout(self.ezcadPage)
        self.verticalLayout_88.setObjectName(u"verticalLayout_88")
        self.page3Label_8 = QLabel(self.ezcadPage)
        self.page3Label_8.setObjectName(u"page3Label_8")
        self.page3Label_8.setMinimumSize(QSize(0, 20))
        self.page3Label_8.setMaximumSize(QSize(16777215, 20))
        self.page3Label_8.setFont(font2)
        self.page3Label_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_88.addWidget(self.page3Label_8)

        self.ezcadFrame = QFrame(self.ezcadPage)
        self.ezcadFrame.setObjectName(u"ezcadFrame")
        self.ezcadFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.ezcadFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_127 = QHBoxLayout(self.ezcadFrame)
        self.horizontalLayout_127.setObjectName(u"horizontalLayout_127")
        self.horizontalLayout_127.setContentsMargins(9, 9, 9, 9)
        self.scrollArea_3 = QScrollArea(self.ezcadFrame)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(-254, -286, 828, 731))
        self.verticalLayout_93 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_93.setObjectName(u"verticalLayout_93")
        self.frame_62 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_62.setObjectName(u"frame_62")
        self.frame_62.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_62.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_139 = QHBoxLayout(self.frame_62)
        self.horizontalLayout_139.setObjectName(u"horizontalLayout_139")
        self.horizontalLayout_139.setContentsMargins(0, 0, 0, 0)
        self.ez1Frame = QFrame(self.frame_62)
        self.ez1Frame.setObjectName(u"ez1Frame")
        self.ez1Frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.ez1Frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_89 = QVBoxLayout(self.ez1Frame)
        self.verticalLayout_89.setObjectName(u"verticalLayout_89")
        self.label_110 = QLabel(self.ez1Frame)
        self.label_110.setObjectName(u"label_110")
        self.label_110.setFont(font5)
        self.label_110.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_89.addWidget(self.label_110, 0, Qt.AlignmentFlag.AlignHCenter)

        self.visualorientFrame = QFrame(self.ez1Frame)
        self.visualorientFrame.setObjectName(u"visualorientFrame")
        self.visualorientFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.visualorientFrame.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_89.addWidget(self.visualorientFrame)

        self.frame_64 = QFrame(self.ez1Frame)
        self.frame_64.setObjectName(u"frame_64")
        self.frame_64.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_64.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_130 = QHBoxLayout(self.frame_64)
        self.horizontalLayout_130.setObjectName(u"horizontalLayout_130")
        self.feedLabel_3 = QLabel(self.frame_64)
        self.feedLabel_3.setObjectName(u"feedLabel_3")
        self.feedLabel_3.setFont(font5)
        self.feedLabel_3.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_130.addWidget(self.feedLabel_3)

        self.imgindLineEdit = QLineEdit(self.frame_64)
        self.imgindLineEdit.setObjectName(u"imgindLineEdit")
        sizePolicy2.setHeightForWidth(self.imgindLineEdit.sizePolicy().hasHeightForWidth())
        self.imgindLineEdit.setSizePolicy(sizePolicy2)
        self.imgindLineEdit.setMinimumSize(QSize(0, 0))
        self.imgindLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.imgindLineEdit.setFont(font5)
        self.imgindLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.imgindLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_130.addWidget(self.imgindLineEdit)

        self.changeimgPushButton = QPushButton(self.frame_64)
        self.changeimgPushButton.setObjectName(u"changeimgPushButton")
        self.changeimgPushButton.setFont(font5)
        self.changeimgPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_130.addWidget(self.changeimgPushButton)


        self.verticalLayout_89.addWidget(self.frame_64)

        self.verticalLayout_89.setStretch(1, 4)

        self.horizontalLayout_139.addWidget(self.ez1Frame)

        self.ez2Frame = QFrame(self.frame_62)
        self.ez2Frame.setObjectName(u"ez2Frame")
        self.ez2Frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.ez2Frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_90 = QVBoxLayout(self.ez2Frame)
        self.verticalLayout_90.setObjectName(u"verticalLayout_90")
        self.verticalLayout_90.setContentsMargins(0, 0, 0, 0)
        self.label_111 = QLabel(self.ez2Frame)
        self.label_111.setObjectName(u"label_111")
        self.label_111.setFont(font5)
        self.label_111.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"}")

        self.verticalLayout_90.addWidget(self.label_111, 0, Qt.AlignmentFlag.AlignHCenter)

        self.frame_66 = QFrame(self.ez2Frame)
        self.frame_66.setObjectName(u"frame_66")
        self.frame_66.setFont(font8)
        self.frame_66.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_66.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_129 = QHBoxLayout(self.frame_66)
        self.horizontalLayout_129.setObjectName(u"horizontalLayout_129")
        self.horizontalLayout_129.setContentsMargins(9, -1, -1, -1)
        self.feedLabel_4 = QLabel(self.frame_66)
        self.feedLabel_4.setObjectName(u"feedLabel_4")
        font17 = QFont()
        font17.setPointSize(11)
        font17.setBold(True)
        self.feedLabel_4.setFont(font17)
        self.feedLabel_4.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_129.addWidget(self.feedLabel_4)

        self.targhalfwidLineEdit = QLineEdit(self.frame_66)
        self.targhalfwidLineEdit.setObjectName(u"targhalfwidLineEdit")
        sizePolicy2.setHeightForWidth(self.targhalfwidLineEdit.sizePolicy().hasHeightForWidth())
        self.targhalfwidLineEdit.setSizePolicy(sizePolicy2)
        self.targhalfwidLineEdit.setMinimumSize(QSize(0, 30))
        self.targhalfwidLineEdit.setMaximumSize(QSize(120, 16777215))
        self.targhalfwidLineEdit.setFont(font5)
        self.targhalfwidLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.targhalfwidLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_129.addWidget(self.targhalfwidLineEdit)

        self.feedLabel_29 = QLabel(self.frame_66)
        self.feedLabel_29.setObjectName(u"feedLabel_29")
        self.feedLabel_29.setFont(font17)
        self.feedLabel_29.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_29.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_129.addWidget(self.feedLabel_29)

        self.resettonominalPushButton = QPushButton(self.frame_66)
        self.resettonominalPushButton.setObjectName(u"resettonominalPushButton")
        self.resettonominalPushButton.setFont(font17)
        self.resettonominalPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_129.addWidget(self.resettonominalPushButton)


        self.verticalLayout_90.addWidget(self.frame_66)

        self.frame_67 = QFrame(self.ez2Frame)
        self.frame_67.setObjectName(u"frame_67")
        self.frame_67.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_67.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_128 = QHBoxLayout(self.frame_67)
        self.horizontalLayout_128.setObjectName(u"horizontalLayout_128")
        self.horizontalLayout_128.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_8 = QLabel(self.frame_67)
        self.feedLabel_8.setObjectName(u"feedLabel_8")
        self.feedLabel_8.setFont(font5)
        self.feedLabel_8.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_128.addWidget(self.feedLabel_8)

        self.feedLabel_7 = QLabel(self.frame_67)
        self.feedLabel_7.setObjectName(u"feedLabel_7")
        self.feedLabel_7.setFont(font5)
        self.feedLabel_7.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_128.addWidget(self.feedLabel_7)

        self.feedLabel_6 = QLabel(self.frame_67)
        self.feedLabel_6.setObjectName(u"feedLabel_6")
        self.feedLabel_6.setFont(font5)
        self.feedLabel_6.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_128.addWidget(self.feedLabel_6)

        self.feedLabel_5 = QLabel(self.frame_67)
        self.feedLabel_5.setObjectName(u"feedLabel_5")
        self.feedLabel_5.setFont(font5)
        self.feedLabel_5.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_128.addWidget(self.feedLabel_5)

        self.horizontalLayout_128.setStretch(1, 2)
        self.horizontalLayout_128.setStretch(2, 2)
        self.horizontalLayout_128.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_67)

        self.frame_68 = QFrame(self.ez2Frame)
        self.frame_68.setObjectName(u"frame_68")
        self.frame_68.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_68.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_131 = QHBoxLayout(self.frame_68)
        self.horizontalLayout_131.setObjectName(u"horizontalLayout_131")
        self.horizontalLayout_131.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_9 = QLabel(self.frame_68)
        self.feedLabel_9.setObjectName(u"feedLabel_9")
        self.feedLabel_9.setFont(font5)
        self.feedLabel_9.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_9.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_131.addWidget(self.feedLabel_9)

        self.x1mmLineEdit = QLineEdit(self.frame_68)
        self.x1mmLineEdit.setObjectName(u"x1mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x1mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x1mmLineEdit.setSizePolicy(sizePolicy2)
        self.x1mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x1mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x1mmLineEdit.setFont(font5)
        self.x1mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x1mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_131.addWidget(self.x1mmLineEdit)

        self.y1mmLineEdit = QLineEdit(self.frame_68)
        self.y1mmLineEdit.setObjectName(u"y1mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y1mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y1mmLineEdit.setSizePolicy(sizePolicy2)
        self.y1mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y1mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y1mmLineEdit.setFont(font5)
        self.y1mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y1mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_131.addWidget(self.y1mmLineEdit)

        self.feedLabel_10 = QLabel(self.frame_68)
        self.feedLabel_10.setObjectName(u"feedLabel_10")
        self.feedLabel_10.setFont(font17)
        self.feedLabel_10.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_10.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_131.addWidget(self.feedLabel_10, 0, Qt.AlignmentFlag.AlignHCenter)

        self.horizontalLayout_131.setStretch(1, 2)
        self.horizontalLayout_131.setStretch(2, 2)
        self.horizontalLayout_131.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_68)

        self.frame_69 = QFrame(self.ez2Frame)
        self.frame_69.setObjectName(u"frame_69")
        self.frame_69.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_69.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_132 = QHBoxLayout(self.frame_69)
        self.horizontalLayout_132.setObjectName(u"horizontalLayout_132")
        self.horizontalLayout_132.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_11 = QLabel(self.frame_69)
        self.feedLabel_11.setObjectName(u"feedLabel_11")
        self.feedLabel_11.setFont(font5)
        self.feedLabel_11.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_11.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_132.addWidget(self.feedLabel_11)

        self.x2mmLineEdit = QLineEdit(self.frame_69)
        self.x2mmLineEdit.setObjectName(u"x2mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x2mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x2mmLineEdit.setSizePolicy(sizePolicy2)
        self.x2mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x2mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x2mmLineEdit.setFont(font5)
        self.x2mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x2mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_132.addWidget(self.x2mmLineEdit)

        self.y2mmLineEdit = QLineEdit(self.frame_69)
        self.y2mmLineEdit.setObjectName(u"y2mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y2mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y2mmLineEdit.setSizePolicy(sizePolicy2)
        self.y2mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y2mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y2mmLineEdit.setFont(font5)
        self.y2mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y2mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_132.addWidget(self.y2mmLineEdit)

        self.feedLabel_12 = QLabel(self.frame_69)
        self.feedLabel_12.setObjectName(u"feedLabel_12")
        self.feedLabel_12.setFont(font9)
        self.feedLabel_12.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_12.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_132.addWidget(self.feedLabel_12)

        self.horizontalLayout_132.setStretch(1, 2)
        self.horizontalLayout_132.setStretch(2, 2)
        self.horizontalLayout_132.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_69)

        self.frame_75 = QFrame(self.ez2Frame)
        self.frame_75.setObjectName(u"frame_75")
        self.frame_75.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_75.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_138 = QHBoxLayout(self.frame_75)
        self.horizontalLayout_138.setObjectName(u"horizontalLayout_138")
        self.horizontalLayout_138.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_23 = QLabel(self.frame_75)
        self.feedLabel_23.setObjectName(u"feedLabel_23")
        self.feedLabel_23.setFont(font5)
        self.feedLabel_23.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_23.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_138.addWidget(self.feedLabel_23)

        self.x3mmLineEdit = QLineEdit(self.frame_75)
        self.x3mmLineEdit.setObjectName(u"x3mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x3mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x3mmLineEdit.setSizePolicy(sizePolicy2)
        self.x3mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x3mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x3mmLineEdit.setFont(font5)
        self.x3mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x3mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_138.addWidget(self.x3mmLineEdit)

        self.y3mmLineEdit = QLineEdit(self.frame_75)
        self.y3mmLineEdit.setObjectName(u"y3mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y3mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y3mmLineEdit.setSizePolicy(sizePolicy2)
        self.y3mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y3mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y3mmLineEdit.setFont(font5)
        self.y3mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y3mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_138.addWidget(self.y3mmLineEdit)

        self.feedLabel_24 = QLabel(self.frame_75)
        self.feedLabel_24.setObjectName(u"feedLabel_24")
        self.feedLabel_24.setFont(font5)
        self.feedLabel_24.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_24.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_138.addWidget(self.feedLabel_24)

        self.horizontalLayout_138.setStretch(1, 2)
        self.horizontalLayout_138.setStretch(2, 2)
        self.horizontalLayout_138.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_75)

        self.frame_70 = QFrame(self.ez2Frame)
        self.frame_70.setObjectName(u"frame_70")
        self.frame_70.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_70.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_133 = QHBoxLayout(self.frame_70)
        self.horizontalLayout_133.setObjectName(u"horizontalLayout_133")
        self.horizontalLayout_133.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_13 = QLabel(self.frame_70)
        self.feedLabel_13.setObjectName(u"feedLabel_13")
        self.feedLabel_13.setFont(font5)
        self.feedLabel_13.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_13.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_133.addWidget(self.feedLabel_13)

        self.x4mmLineEdit = QLineEdit(self.frame_70)
        self.x4mmLineEdit.setObjectName(u"x4mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x4mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x4mmLineEdit.setSizePolicy(sizePolicy2)
        self.x4mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x4mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x4mmLineEdit.setFont(font5)
        self.x4mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x4mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_133.addWidget(self.x4mmLineEdit)

        self.y4mmLineEdit = QLineEdit(self.frame_70)
        self.y4mmLineEdit.setObjectName(u"y4mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y4mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y4mmLineEdit.setSizePolicy(sizePolicy2)
        self.y4mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y4mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y4mmLineEdit.setFont(font5)
        self.y4mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y4mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_133.addWidget(self.y4mmLineEdit)

        self.feedLabel_14 = QLabel(self.frame_70)
        self.feedLabel_14.setObjectName(u"feedLabel_14")
        self.feedLabel_14.setFont(font5)
        self.feedLabel_14.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_14.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_133.addWidget(self.feedLabel_14)

        self.horizontalLayout_133.setStretch(1, 2)
        self.horizontalLayout_133.setStretch(2, 2)
        self.horizontalLayout_133.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_70)

        self.frame_71 = QFrame(self.ez2Frame)
        self.frame_71.setObjectName(u"frame_71")
        self.frame_71.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_71.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_134 = QHBoxLayout(self.frame_71)
        self.horizontalLayout_134.setObjectName(u"horizontalLayout_134")
        self.horizontalLayout_134.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_15 = QLabel(self.frame_71)
        self.feedLabel_15.setObjectName(u"feedLabel_15")
        self.feedLabel_15.setFont(font5)
        self.feedLabel_15.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_15.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_134.addWidget(self.feedLabel_15)

        self.x5mmLineEdit = QLineEdit(self.frame_71)
        self.x5mmLineEdit.setObjectName(u"x5mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x5mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x5mmLineEdit.setSizePolicy(sizePolicy2)
        self.x5mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x5mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x5mmLineEdit.setFont(font5)
        self.x5mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x5mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_134.addWidget(self.x5mmLineEdit)

        self.y5mmLineEdit = QLineEdit(self.frame_71)
        self.y5mmLineEdit.setObjectName(u"y5mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y5mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y5mmLineEdit.setSizePolicy(sizePolicy2)
        self.y5mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y5mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y5mmLineEdit.setFont(font5)
        self.y5mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y5mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_134.addWidget(self.y5mmLineEdit)

        self.feedLabel_16 = QLabel(self.frame_71)
        self.feedLabel_16.setObjectName(u"feedLabel_16")
        self.feedLabel_16.setFont(font5)
        self.feedLabel_16.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_16.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_134.addWidget(self.feedLabel_16)

        self.horizontalLayout_134.setStretch(1, 2)
        self.horizontalLayout_134.setStretch(2, 2)
        self.horizontalLayout_134.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_71)

        self.frame_72 = QFrame(self.ez2Frame)
        self.frame_72.setObjectName(u"frame_72")
        self.frame_72.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_72.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_135 = QHBoxLayout(self.frame_72)
        self.horizontalLayout_135.setObjectName(u"horizontalLayout_135")
        self.horizontalLayout_135.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_17 = QLabel(self.frame_72)
        self.feedLabel_17.setObjectName(u"feedLabel_17")
        self.feedLabel_17.setFont(font5)
        self.feedLabel_17.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_17.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_135.addWidget(self.feedLabel_17)

        self.x6mmLineEdit = QLineEdit(self.frame_72)
        self.x6mmLineEdit.setObjectName(u"x6mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x6mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x6mmLineEdit.setSizePolicy(sizePolicy2)
        self.x6mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x6mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x6mmLineEdit.setFont(font5)
        self.x6mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x6mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_135.addWidget(self.x6mmLineEdit)

        self.y6mmLineEdit = QLineEdit(self.frame_72)
        self.y6mmLineEdit.setObjectName(u"y6mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y6mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y6mmLineEdit.setSizePolicy(sizePolicy2)
        self.y6mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y6mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y6mmLineEdit.setFont(font5)
        self.y6mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y6mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_135.addWidget(self.y6mmLineEdit)

        self.feedLabel_18 = QLabel(self.frame_72)
        self.feedLabel_18.setObjectName(u"feedLabel_18")
        self.feedLabel_18.setFont(font5)
        self.feedLabel_18.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_18.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_135.addWidget(self.feedLabel_18)

        self.horizontalLayout_135.setStretch(1, 2)
        self.horizontalLayout_135.setStretch(2, 2)
        self.horizontalLayout_135.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_72)

        self.frame_74 = QFrame(self.ez2Frame)
        self.frame_74.setObjectName(u"frame_74")
        self.frame_74.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_74.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_137 = QHBoxLayout(self.frame_74)
        self.horizontalLayout_137.setObjectName(u"horizontalLayout_137")
        self.horizontalLayout_137.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_21 = QLabel(self.frame_74)
        self.feedLabel_21.setObjectName(u"feedLabel_21")
        self.feedLabel_21.setFont(font5)
        self.feedLabel_21.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_21.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_137.addWidget(self.feedLabel_21)

        self.x7mmLineEdit = QLineEdit(self.frame_74)
        self.x7mmLineEdit.setObjectName(u"x7mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x7mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x7mmLineEdit.setSizePolicy(sizePolicy2)
        self.x7mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x7mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x7mmLineEdit.setFont(font5)
        self.x7mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x7mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_137.addWidget(self.x7mmLineEdit)

        self.y7mmLineEdit = QLineEdit(self.frame_74)
        self.y7mmLineEdit.setObjectName(u"y7mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y7mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y7mmLineEdit.setSizePolicy(sizePolicy2)
        self.y7mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y7mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y7mmLineEdit.setFont(font5)
        self.y7mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y7mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_137.addWidget(self.y7mmLineEdit)

        self.feedLabel_22 = QLabel(self.frame_74)
        self.feedLabel_22.setObjectName(u"feedLabel_22")
        self.feedLabel_22.setFont(font17)
        self.feedLabel_22.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_22.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_137.addWidget(self.feedLabel_22)

        self.horizontalLayout_137.setStretch(1, 2)
        self.horizontalLayout_137.setStretch(2, 2)
        self.horizontalLayout_137.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_74)

        self.frame_73 = QFrame(self.ez2Frame)
        self.frame_73.setObjectName(u"frame_73")
        self.frame_73.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_73.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_136 = QHBoxLayout(self.frame_73)
        self.horizontalLayout_136.setObjectName(u"horizontalLayout_136")
        self.horizontalLayout_136.setContentsMargins(-1, 0, -1, 0)
        self.feedLabel_19 = QLabel(self.frame_73)
        self.feedLabel_19.setObjectName(u"feedLabel_19")
        self.feedLabel_19.setFont(font5)
        self.feedLabel_19.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_19.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_136.addWidget(self.feedLabel_19)

        self.x8mmLineEdit = QLineEdit(self.frame_73)
        self.x8mmLineEdit.setObjectName(u"x8mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x8mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x8mmLineEdit.setSizePolicy(sizePolicy2)
        self.x8mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x8mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x8mmLineEdit.setFont(font5)
        self.x8mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x8mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_136.addWidget(self.x8mmLineEdit)

        self.y8mmLineEdit = QLineEdit(self.frame_73)
        self.y8mmLineEdit.setObjectName(u"y8mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y8mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y8mmLineEdit.setSizePolicy(sizePolicy2)
        self.y8mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y8mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y8mmLineEdit.setFont(font5)
        self.y8mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y8mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_136.addWidget(self.y8mmLineEdit)

        self.feedLabel_20 = QLabel(self.frame_73)
        self.feedLabel_20.setObjectName(u"feedLabel_20")
        self.feedLabel_20.setFont(font5)
        self.feedLabel_20.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_20.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_136.addWidget(self.feedLabel_20)

        self.horizontalLayout_136.setStretch(1, 2)
        self.horizontalLayout_136.setStretch(2, 2)
        self.horizontalLayout_136.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_73)

        self.frame_84 = QFrame(self.ez2Frame)
        self.frame_84.setObjectName(u"frame_84")
        self.frame_84.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_84.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_146 = QHBoxLayout(self.frame_84)
        self.horizontalLayout_146.setObjectName(u"horizontalLayout_146")
        self.horizontalLayout_146.setContentsMargins(-1, 0, -1, 9)
        self.feedLabel_27 = QLabel(self.frame_84)
        self.feedLabel_27.setObjectName(u"feedLabel_27")
        self.feedLabel_27.setFont(font5)
        self.feedLabel_27.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_27.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_146.addWidget(self.feedLabel_27)

        self.x9mmLineEdit = QLineEdit(self.frame_84)
        self.x9mmLineEdit.setObjectName(u"x9mmLineEdit")
        sizePolicy2.setHeightForWidth(self.x9mmLineEdit.sizePolicy().hasHeightForWidth())
        self.x9mmLineEdit.setSizePolicy(sizePolicy2)
        self.x9mmLineEdit.setMinimumSize(QSize(0, 0))
        self.x9mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.x9mmLineEdit.setFont(font5)
        self.x9mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.x9mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_146.addWidget(self.x9mmLineEdit)

        self.y9mmLineEdit = QLineEdit(self.frame_84)
        self.y9mmLineEdit.setObjectName(u"y9mmLineEdit")
        sizePolicy2.setHeightForWidth(self.y9mmLineEdit.sizePolicy().hasHeightForWidth())
        self.y9mmLineEdit.setSizePolicy(sizePolicy2)
        self.y9mmLineEdit.setMinimumSize(QSize(0, 0))
        self.y9mmLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.y9mmLineEdit.setFont(font5)
        self.y9mmLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.y9mmLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_146.addWidget(self.y9mmLineEdit)

        self.feedLabel_28 = QLabel(self.frame_84)
        self.feedLabel_28.setObjectName(u"feedLabel_28")
        self.feedLabel_28.setFont(font17)
        self.feedLabel_28.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_28.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_146.addWidget(self.feedLabel_28)

        self.horizontalLayout_146.setStretch(1, 2)
        self.horizontalLayout_146.setStretch(2, 2)
        self.horizontalLayout_146.setStretch(3, 2)

        self.verticalLayout_90.addWidget(self.frame_84)


        self.horizontalLayout_139.addWidget(self.ez2Frame)


        self.verticalLayout_93.addWidget(self.frame_62)

        self.frame_76 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_76.setObjectName(u"frame_76")
        self.frame_76.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_76.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_145 = QHBoxLayout(self.frame_76)
        self.horizontalLayout_145.setObjectName(u"horizontalLayout_145")
        self.horizontalLayout_145.setContentsMargins(0, 0, 0, 0)
        self.ez3Frame = QFrame(self.frame_76)
        self.ez3Frame.setObjectName(u"ez3Frame")
        self.ez3Frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.ez3Frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_91 = QVBoxLayout(self.ez3Frame)
        self.verticalLayout_91.setObjectName(u"verticalLayout_91")
        self.verticalLayout_91.setContentsMargins(0, 5, 0, 0)
        self.indexLabel_2 = QLabel(self.ez3Frame)
        self.indexLabel_2.setObjectName(u"indexLabel_2")
        self.indexLabel_2.setFont(font5)
        self.indexLabel_2.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_91.addWidget(self.indexLabel_2)

        self.frame_79 = QFrame(self.ez3Frame)
        self.frame_79.setObjectName(u"frame_79")
        self.frame_79.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_79.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_140 = QHBoxLayout(self.frame_79)
        self.horizontalLayout_140.setObjectName(u"horizontalLayout_140")
        self.indexLabel_3 = QLabel(self.frame_79)
        self.indexLabel_3.setObjectName(u"indexLabel_3")
        self.indexLabel_3.setFont(font5)
        self.indexLabel_3.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_140.addWidget(self.indexLabel_3)

        self.powerHorizontalSlider = QSlider(self.frame_79)
        self.powerHorizontalSlider.setObjectName(u"powerHorizontalSlider")
        self.powerHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_140.addWidget(self.powerHorizontalSlider)

        self.indexLabel_4 = QLabel(self.frame_79)
        self.indexLabel_4.setObjectName(u"indexLabel_4")
        self.indexLabel_4.setFont(font5)
        self.indexLabel_4.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_140.addWidget(self.indexLabel_4)

        self.indexLabel_5 = QLabel(self.frame_79)
        self.indexLabel_5.setObjectName(u"indexLabel_5")
        self.indexLabel_5.setFont(font5)
        self.indexLabel_5.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_140.addWidget(self.indexLabel_5)

        self.freqHorizontalSlider = QSlider(self.frame_79)
        self.freqHorizontalSlider.setObjectName(u"freqHorizontalSlider")
        self.freqHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_140.addWidget(self.freqHorizontalSlider)

        self.indexLabel_6 = QLabel(self.frame_79)
        self.indexLabel_6.setObjectName(u"indexLabel_6")
        self.indexLabel_6.setFont(font5)
        self.indexLabel_6.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_140.addWidget(self.indexLabel_6)


        self.verticalLayout_91.addWidget(self.frame_79)

        self.frame_80 = QFrame(self.ez3Frame)
        self.frame_80.setObjectName(u"frame_80")
        self.frame_80.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_80.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_141 = QHBoxLayout(self.frame_80)
        self.horizontalLayout_141.setObjectName(u"horizontalLayout_141")
        self.feedLabel_25 = QLabel(self.frame_80)
        self.feedLabel_25.setObjectName(u"feedLabel_25")
        self.feedLabel_25.setFont(font5)
        self.feedLabel_25.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_25.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_141.addWidget(self.feedLabel_25)

        self.markspeedLineEdit = QLineEdit(self.frame_80)
        self.markspeedLineEdit.setObjectName(u"markspeedLineEdit")
        sizePolicy2.setHeightForWidth(self.markspeedLineEdit.sizePolicy().hasHeightForWidth())
        self.markspeedLineEdit.setSizePolicy(sizePolicy2)
        self.markspeedLineEdit.setMinimumSize(QSize(0, 0))
        self.markspeedLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.markspeedLineEdit.setFont(font5)
        self.markspeedLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.markspeedLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_141.addWidget(self.markspeedLineEdit)

        self.feedLabel_26 = QLabel(self.frame_80)
        self.feedLabel_26.setObjectName(u"feedLabel_26")
        self.feedLabel_26.setFont(font5)
        self.feedLabel_26.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.feedLabel_26.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_141.addWidget(self.feedLabel_26)

        self.jumpspeedLineEdit = QLineEdit(self.frame_80)
        self.jumpspeedLineEdit.setObjectName(u"jumpspeedLineEdit")
        sizePolicy2.setHeightForWidth(self.jumpspeedLineEdit.sizePolicy().hasHeightForWidth())
        self.jumpspeedLineEdit.setSizePolicy(sizePolicy2)
        self.jumpspeedLineEdit.setMinimumSize(QSize(0, 0))
        self.jumpspeedLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.jumpspeedLineEdit.setFont(font5)
        self.jumpspeedLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border: 2px solid #102a83;\n"
"    border-radius: 6px;       /* Optional: for rounded corners */\n"
"    padding: 4px;             /* Optional: inner spacing */\n"
"    color: #102a83;           /* Text color inside the line edit */\n"
"}\n"
"")
        self.jumpspeedLineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_141.addWidget(self.jumpspeedLineEdit)


        self.verticalLayout_91.addWidget(self.frame_80)

        self.frame_81 = QFrame(self.ez3Frame)
        self.frame_81.setObjectName(u"frame_81")
        self.frame_81.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_81.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_142 = QHBoxLayout(self.frame_81)
        self.horizontalLayout_142.setObjectName(u"horizontalLayout_142")
        self.reddotPushButton = QPushButton(self.frame_81)
        self.reddotPushButton.setObjectName(u"reddotPushButton")
        self.reddotPushButton.setFont(font5)
        self.reddotPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_142.addWidget(self.reddotPushButton)

        self.markcalgridPushButton = QPushButton(self.frame_81)
        self.markcalgridPushButton.setObjectName(u"markcalgridPushButton")
        self.markcalgridPushButton.setFont(font5)
        self.markcalgridPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_142.addWidget(self.markcalgridPushButton)

        self.stopPushButton = QPushButton(self.frame_81)
        self.stopPushButton.setObjectName(u"stopPushButton")
        self.stopPushButton.setFont(font5)
        self.stopPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_142.addWidget(self.stopPushButton)


        self.verticalLayout_91.addWidget(self.frame_81)


        self.horizontalLayout_145.addWidget(self.ez3Frame)

        self.frame_65 = QFrame(self.frame_76)
        self.frame_65.setObjectName(u"frame_65")
        self.frame_65.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_65.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_95 = QVBoxLayout(self.frame_65)
        self.verticalLayout_95.setObjectName(u"verticalLayout_95")
        self.verticalLayout_95.setContentsMargins(0, 0, 0, 0)
        self.ez4Frame = QFrame(self.frame_65)
        self.ez4Frame.setObjectName(u"ez4Frame")
        self.ez4Frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.ez4Frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_92 = QVBoxLayout(self.ez4Frame)
        self.verticalLayout_92.setObjectName(u"verticalLayout_92")
        self.indexLabel_7 = QLabel(self.ez4Frame)
        self.indexLabel_7.setObjectName(u"indexLabel_7")
        self.indexLabel_7.setFont(font5)
        self.indexLabel_7.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_92.addWidget(self.indexLabel_7)

        self.frame_82 = QFrame(self.ez4Frame)
        self.frame_82.setObjectName(u"frame_82")
        self.frame_82.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_82.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_143 = QHBoxLayout(self.frame_82)
        self.horizontalLayout_143.setObjectName(u"horizontalLayout_143")
        self.indexLabel_8 = QLabel(self.frame_82)
        self.indexLabel_8.setObjectName(u"indexLabel_8")
        self.indexLabel_8.setFont(font5)
        self.indexLabel_8.setStyleSheet(u"QLabel {\n"
"    color: rgb(16, 42, 131);\n"
"    font-weight: bold;\n"
"}")
        self.indexLabel_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_143.addWidget(self.indexLabel_8, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_92.addWidget(self.frame_82)

        self.frame_83 = QFrame(self.ez4Frame)
        self.frame_83.setObjectName(u"frame_83")
        self.frame_83.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_83.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_144 = QHBoxLayout(self.frame_83)
        self.horizontalLayout_144.setObjectName(u"horizontalLayout_144")
        self.horizontalLayout_144.setContentsMargins(0, 0, 0, 0)
        self.calapplyPushButton = QPushButton(self.frame_83)
        self.calapplyPushButton.setObjectName(u"calapplyPushButton")
        self.calapplyPushButton.setFont(font5)
        self.calapplyPushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_144.addWidget(self.calapplyPushButton)

        self.markvershapePushButton = QPushButton(self.frame_83)
        self.markvershapePushButton.setObjectName(u"markvershapePushButton")
        self.markvershapePushButton.setFont(font5)
        self.markvershapePushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_144.addWidget(self.markvershapePushButton)


        self.verticalLayout_92.addWidget(self.frame_83)


        self.verticalLayout_95.addWidget(self.ez4Frame)

        self.frame_63 = QFrame(self.frame_65)
        self.frame_63.setObjectName(u"frame_63")
        self.frame_63.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_63.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_147 = QHBoxLayout(self.frame_63)
        self.horizontalLayout_147.setObjectName(u"horizontalLayout_147")
        self.horizontalSpacer_12 = QSpacerItem(170, 9, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_147.addItem(self.horizontalSpacer_12)

        self.ezcadclosePushButton = QPushButton(self.frame_63)
        self.ezcadclosePushButton.setObjectName(u"ezcadclosePushButton")
        self.ezcadclosePushButton.setFont(font5)
        self.ezcadclosePushButton.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_147.addWidget(self.ezcadclosePushButton)

        self.horizontalLayout_147.setStretch(0, 3)
        self.horizontalLayout_147.setStretch(1, 2)

        self.verticalLayout_95.addWidget(self.frame_63)


        self.horizontalLayout_145.addWidget(self.frame_65)


        self.verticalLayout_93.addWidget(self.frame_76)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.horizontalLayout_127.addWidget(self.scrollArea_3)


        self.verticalLayout_88.addWidget(self.ezcadFrame)

        self.mainPages.addWidget(self.ezcadPage)

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
        icon25 = QIcon()
        icon25.addFile(u":/icons/icons/x-octagon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeNotifyPushButton.setIcon(icon25)
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

        self.centerMenuPages.setCurrentIndex(1)
        self.infoSubPages.setCurrentIndex(0)
        self.mainPages.setCurrentIndex(11)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.menuPushButton.setText("")
        self.homePushButton.setText(QCoreApplication.translate("MainWindow", u" Home", None))
        self.laserPushButton.setText(QCoreApplication.translate("MainWindow", u"Lasers", None))
        self.programsPushButton.setText(QCoreApplication.translate("MainWindow", u" Programs", None))
        self.printPushButton.setText(QCoreApplication.translate("MainWindow", u" Print", None))
        self.cameraPushButton.setText(QCoreApplication.translate("MainWindow", u" Camera", None))
        self.cameraonoffoffsetPushButton.setText(QCoreApplication.translate("MainWindow", u"Camera Jog", None))
        self.joggalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Jog Page", None))
        self.laserconfgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Lasers Config", None))
        self.programsgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u" Programs Page", None))
        self.printgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u" Print Page", None))
        self.terminalPushButton.setText(QCoreApplication.translate("MainWindow", u"Terminal", None))
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
        self.mainconnectgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.maindisconnectgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Disconnect", None))
        self.settingsLabel.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.indexLabel.setText(QCoreApplication.translate("MainWindow", u"Index Position :", None))
        self.feedLabel_2.setText(QCoreApplication.translate("MainWindow", u"Camera Offset:", None))
        self.cameraoffsetPushButton.setText(QCoreApplication.translate("MainWindow", u"ON", None))
        self.setconfigPushButton.setText(QCoreApplication.translate("MainWindow", u"CONFIG", None))
        self.setadvancalPushButton.setText(QCoreApplication.translate("MainWindow", u"Advanced\n"
"Calibration", None))
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
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"PATTERNING MACHINE", None))
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
        self.ftravelPushButton.setText(QCoreApplication.translate("MainWindow", u"1", None))
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
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Feedrate :", None))
        self.pgmfeedLineEdit.setText(QCoreApplication.translate("MainWindow", u"500", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"mm/min", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Laser Selection :", None))
        self.pgmsavePushButton.setText(QCoreApplication.translate("MainWindow", u"SAVE", None))
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
        self.page1Label_3.setText(QCoreApplication.translate("MainWindow", u"JOG", None))
        self.homeLabel_3.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.galvohomePushButton.setText(QCoreApplication.translate("MainWindow", u"GALVO", None))
        self.galvozhomePushButton.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.galvoallhomePushButton.setText(QCoreApplication.translate("MainWindow", u"ALL", None))
        self.label_50.setText(QCoreApplication.translate("MainWindow", u"Test Pattern", None))
        self.circlePushButton.setText("")
        self.trianglePushButton.setText("")
        self.squarePushButton.setText("")
        self.label_49.setText(QCoreApplication.translate("MainWindow", u"Z Axis", None))
        self.zplusgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.ztravelPushButton.setText(QCoreApplication.translate("MainWindow", u"10", None))
        self.zminusgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.page3Label_5.setText(QCoreApplication.translate("MainWindow", u"Laser Config", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Set Focus", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"Object Height :", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Main Laser :", None))
        self.flasergalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"ON", None))
        self.label_109.setText(QCoreApplication.translate("MainWindow", u"Reddot Laser :", None))
        self.freddotlasergalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"ON", None))
        self.fplusgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.ftravelgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.fminusgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.fsetgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.label_45.setText(QCoreApplication.translate("MainWindow", u"Laser Parameters", None))
        self.label_108.setText(QCoreApplication.translate("MainWindow", u"Laser Power :", None))
        self.powersetgalvoPushButton_2.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Laser Freq :    ", None))
        self.freqsetgalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"SET", None))
        self.page2Label_2.setText(QCoreApplication.translate("MainWindow", u"PROGRAM", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Design File :", None))
        self.pgmfilegalvoPushButton.setText(QCoreApplication.translate("MainWindow", u"SELECT", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Sample Height :", None))
        self.pgmheightgalvoLineEdit.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Mark Speed :", None))
        self.pgmmarkspeedgalvoLineEdit.setText("")
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"Jump Speed :", None))
        self.pgmjumpspeedLineEdit.setText("")
        self.label_37.setText(QCoreApplication.translate("MainWindow", u"Loop Count :", None))
        self.pgmloopcountLineEdit.setText("")
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"Start Position ", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"X :", None))
        self.pgmstartposxLineEdit.setText("")
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"Y :", None))
        self.pgmstartposyLineEdit.setText("")
        self.label_41.setText(QCoreApplication.translate("MainWindow", u"Enable Hatching :", None))
        self.pgmenablehatchCheckBox.setText("")
        self.label_54.setText(QCoreApplication.translate("MainWindow", u"Mark Contour :", None))
        self.pgmmarkcontourCheckBox.setText("")
        self.label_55.setText(QCoreApplication.translate("MainWindow", u"Hatch :", None))
        self.pgmhatch1_RadioButton.setText("")
        self.label_79.setText(QCoreApplication.translate("MainWindow", u"Hatch 1", None))
        self.pgmhatch2_RadioButton.setText("")
        self.label_80.setText(QCoreApplication.translate("MainWindow", u"Hatch 2", None))
        self.pgmhatch3_RadioButton.setText("")
        self.label_81.setText(QCoreApplication.translate("MainWindow", u"Hatch 3", None))
        self.label_78.setText(QCoreApplication.translate("MainWindow", u"Enable :", None))
        self.pgmenableCheckBox.setText("")
        self.label_56.setText(QCoreApplication.translate("MainWindow", u"All Calc :", None))
        self.pgmallcalcCheckBox.setText("")
        self.label_57.setText(QCoreApplication.translate("MainWindow", u"Follow Edge\n"
"once :", None))
        self.pgmfolloedgCheckBox.setText("")
        self.label_58.setText(QCoreApplication.translate("MainWindow", u"Cross Hatch :", None))
        self.pgmcrosshatchCheckBox.setText("")
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Type :", None))
        self.label_48.setText(QCoreApplication.translate("MainWindow", u"Angle :", None))
        self.pgmangleLineEdit.setText("")
        self.label_59.setText(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.label_60.setText(QCoreApplication.translate("MainWindow", u"Count :", None))
        self.pgmcountLineEdit.setText("")
        self.label_61.setText(QCoreApplication.translate("MainWindow", u"Line Space :", None))
        self.pgmlinespaceLineEdit.setText("")
        self.label_62.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_63.setText(QCoreApplication.translate("MainWindow", u"Average Distribute Line: :", None))
        self.pgmavgdistCheckBox.setText("")
        self.label_64.setText(QCoreApplication.translate("MainWindow", u"Edge Offset:", None))
        self.pgmedgeoffLineEdit.setText("")
        self.label_75.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_65.setText("")
        self.label_66.setText(QCoreApplication.translate("MainWindow", u"Start Offset :", None))
        self.pgmstartoffLineEdit.setText("")
        self.label_77.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_67.setText(QCoreApplication.translate("MainWindow", u"End Offset :", None))
        self.pgmendoffLineEdit.setText("")
        self.label_68.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_69.setText(QCoreApplication.translate("MainWindow", u"Line \n"
"Reduction :", None))
        self.pgmlineredLineEdit.setText("")
        self.label_70.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_71.setText(QCoreApplication.translate("MainWindow", u"Numloops :", None))
        self.pgmnumloopsLineEdit.setText("")
        self.label_72.setText(QCoreApplication.translate("MainWindow", u"Loop\n"
"Distance:", None))
        self.pgmloopdistLineEdit.setText("")
        self.label_73.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_76.setText(QCoreApplication.translate("MainWindow", u"Auto Rotate Hatch Angle : ", None))
        self.pgmautorotangleCheckBox.setText("")
        self.pgmautorotanglLineEdit.setText("")
        self.label_74.setText(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.pgmgalvosavePushButton.setText(QCoreApplication.translate("MainWindow", u"SAVE", None))
        self.page3Label_6.setText(QCoreApplication.translate("MainWindow", u"PRINT", None))
        self.label_51.setText(QCoreApplication.translate("MainWindow", u"Image Plot", None))
        self.label_52.setText(QCoreApplication.translate("MainWindow", u"Operation", None))
#if QT_CONFIG(tooltip)
        self.printrungalvoPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Run", None))
#endif // QT_CONFIG(tooltip)
        self.printrungalvoPushButton.setText("")
#if QT_CONFIG(tooltip)
        self.printabortgalvoPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Abort", None))
#endif // QT_CONFIG(tooltip)
        self.printabortgalvoPushButton.setText("")
#if QT_CONFIG(tooltip)
        self.redlightprePushButton.setToolTip(QCoreApplication.translate("MainWindow", u"Red Light Preview", None))
#endif // QT_CONFIG(tooltip)
        self.redlightprePushButton.setText("")
        self.label_53.setText(QCoreApplication.translate("MainWindow", u"Progress :", None))
        self.printgalvoProgressBar.setFormat("")
        self.progressLabel_2.setText(QCoreApplication.translate("MainWindow", u"0%", None))
        self.page3Label_7.setText(QCoreApplication.translate("MainWindow", u"CONFIG", None))
        self.label_82.setText(QCoreApplication.translate("MainWindow", u"Aspect", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"Field Size :", None))
        self.fieldsizeconfLineEdit.setText("")
        self.label_104.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"Offset X :", None))
        self.offxconfLineEdit.setText("")
        self.label_105.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_42.setText(QCoreApplication.translate("MainWindow", u"Offset Y :", None))
        self.offyconfLineEdit.setText("")
        self.label_106.setText(QCoreApplication.translate("MainWindow", u"mm", None))
        self.label_46.setText(QCoreApplication.translate("MainWindow", u"Angle :", None))
        self.angleconfLineEdit.setText("")
        self.label_107.setText(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.galvo1confRadioButton.setText("")
        self.label_43.setText(QCoreApplication.translate("MainWindow", u"Galvo 1 = X ", None))
        self.galvo2confRadioButton.setText("")
        self.label_44.setText(QCoreApplication.translate("MainWindow", u"Galvo 2 = X ", None))
        self.label_88.setText(QCoreApplication.translate("MainWindow", u"Galvo 1", None))
        self.label_94.setText(QCoreApplication.translate("MainWindow", u"Negate :", None))
        self.neggalvo1confCheckBox.setText("")
        self.label_96.setText(QCoreApplication.translate("MainWindow", u"Scale :", None))
        self.confscalegalvo1LineEdit.setText("")
        self.confscalegalvo1PushButton.setText(QCoreApplication.translate("MainWindow", u">>", None))
        self.label_98.setText(QCoreApplication.translate("MainWindow", u"Barrel/Bulge :", None))
        self.confbargalvo1LineEdit.setText("")
        self.label_97.setText(QCoreApplication.translate("MainWindow", u"Parallelogram :", None))
        self.confpargalvo1LineEdit.setText("")
        self.label_103.setText(QCoreApplication.translate("MainWindow", u"Trapezoid :", None))
        self.conftrapgalvo1LineEdit.setText("")
        self.label_89.setText(QCoreApplication.translate("MainWindow", u"Galvo 2", None))
        self.label_95.setText(QCoreApplication.translate("MainWindow", u"Negate :", None))
        self.neggalvo2confCheckBox.setText("")
        self.label_99.setText(QCoreApplication.translate("MainWindow", u"Scale :", None))
        self.confscalegalvo2LineEdit.setText("")
        self.confscalegalvo2PushButton.setText(QCoreApplication.translate("MainWindow", u">>", None))
        self.label_100.setText(QCoreApplication.translate("MainWindow", u"Barrel/Bulge :", None))
        self.confbargalvo2LineEdit.setText("")
        self.label_101.setText(QCoreApplication.translate("MainWindow", u"Parallelogram :", None))
        self.confpargalvo2LineEdit.setText("")
        self.label_102.setText(QCoreApplication.translate("MainWindow", u"Trapezoid :", None))
        self.conftrapgalvo2LineEdit.setText("")
        self.label_84.setText(QCoreApplication.translate("MainWindow", u"Go to Pos After Mark ", None))
        self.confnomovRadioButton.setText("")
        self.label_83.setText(QCoreApplication.translate("MainWindow", u"No Movement ", None))
        self.confgalvocentRadioButton.setText("")
        self.label_86.setText(QCoreApplication.translate("MainWindow", u"Galvo Center", None))
        self.conftopleftRadioButton.setText("")
        self.label_85.setText(QCoreApplication.translate("MainWindow", u"Top Left", None))
        self.conftoprightRadioButton.setText("")
        self.label_87.setText(QCoreApplication.translate("MainWindow", u"Top Right", None))
        self.confbotrightRadioButton.setText("")
        self.label_90.setText(QCoreApplication.translate("MainWindow", u"Bottom Right", None))
        self.confbotleftRadioButton.setText("")
        self.label_92.setText(QCoreApplication.translate("MainWindow", u"Bottom Left", None))
        self.confspecposRadioButton.setText("")
        self.label_93.setText(QCoreApplication.translate("MainWindow", u"Special Pos", None))
        self.label_47.setText(QCoreApplication.translate("MainWindow", u"X :", None))
        self.confxmarkLineEdit.setText("")
        self.label_91.setText(QCoreApplication.translate("MainWindow", u"Y :", None))
        self.confymarkLineEdit.setText("")
        self.confokPushButton.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.confcancelPushButton.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.confapplyPushButton.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.page3Label_2.setText(QCoreApplication.translate("MainWindow", u"TERMINAL", None))
        self.termsendPushButton.setText("")
        self.page3Label_8.setText(QCoreApplication.translate("MainWindow", u"EZCAD 9-Point Calibration Studio", None))
        self.label_110.setText(QCoreApplication.translate("MainWindow", u"Visual Orientation(Match Physical Mark)", None))
        self.feedLabel_3.setText(QCoreApplication.translate("MainWindow", u"Image:", None))
        self.changeimgPushButton.setText(QCoreApplication.translate("MainWindow", u"Change Image>>", None))
        self.label_111.setText(QCoreApplication.translate("MainWindow", u"Measured Distances from Center(mm)'", None))
        self.feedLabel_4.setText(QCoreApplication.translate("MainWindow", u"Target Half-Width(W)", None))
        self.feedLabel_29.setText(QCoreApplication.translate("MainWindow", u"mm(Nominal \n"
"Field=2*W)", None))
        self.resettonominalPushButton.setText(QCoreApplication.translate("MainWindow", u"Reset to Nominal", None))
        self.feedLabel_8.setText(QCoreApplication.translate("MainWindow", u"Pt", None))
        self.feedLabel_7.setText(QCoreApplication.translate("MainWindow", u"X Distance(mm)", None))
        self.feedLabel_6.setText(QCoreApplication.translate("MainWindow", u"Y Distance(mm)", None))
        self.feedLabel_5.setText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.feedLabel_9.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.feedLabel_10.setText(QCoreApplication.translate("MainWindow", u"Top-Left Corner", None))
        self.feedLabel_11.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.feedLabel_12.setText(QCoreApplication.translate("MainWindow", u"Top Center", None))
        self.feedLabel_23.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.feedLabel_24.setText(QCoreApplication.translate("MainWindow", u"Top-Right Corner", None))
        self.feedLabel_13.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.feedLabel_14.setText(QCoreApplication.translate("MainWindow", u"Left Center", None))
        self.feedLabel_15.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.feedLabel_16.setText(QCoreApplication.translate("MainWindow", u"Center(0,0)", None))
        self.feedLabel_17.setText(QCoreApplication.translate("MainWindow", u"6", None))
        self.feedLabel_18.setText(QCoreApplication.translate("MainWindow", u"Right Center", None))
        self.feedLabel_21.setText(QCoreApplication.translate("MainWindow", u"7", None))
        self.feedLabel_22.setText(QCoreApplication.translate("MainWindow", u"Bottom-Left Corner", None))
        self.feedLabel_19.setText(QCoreApplication.translate("MainWindow", u"8", None))
        self.feedLabel_20.setText(QCoreApplication.translate("MainWindow", u"Bottom Center", None))
        self.feedLabel_27.setText(QCoreApplication.translate("MainWindow", u"9", None))
        self.feedLabel_28.setText(QCoreApplication.translate("MainWindow", u"Bottom-Right Corner", None))
        self.indexLabel_2.setText(QCoreApplication.translate("MainWindow", u"Laser Marking Controls", None))
        self.indexLabel_3.setText(QCoreApplication.translate("MainWindow", u"Power(%)", None))
        self.indexLabel_4.setText(QCoreApplication.translate("MainWindow", u"100", None))
        self.indexLabel_5.setText(QCoreApplication.translate("MainWindow", u"Freq(kHz)", None))
        self.indexLabel_6.setText(QCoreApplication.translate("MainWindow", u"30", None))
        self.feedLabel_25.setText(QCoreApplication.translate("MainWindow", u"Mark Speed:", None))
        self.feedLabel_26.setText(QCoreApplication.translate("MainWindow", u"Jump Speed:", None))
        self.reddotPushButton.setText(QCoreApplication.translate("MainWindow", u"Red Dot Frame", None))
        self.markcalgridPushButton.setText(QCoreApplication.translate("MainWindow", u"Mark Calibration Grid", None))
        self.stopPushButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.indexLabel_7.setText(QCoreApplication.translate("MainWindow", u"Apply Verification Calibration", None))
        self.indexLabel_8.setText(QCoreApplication.translate("MainWindow", u"Status : Ready", None))
        self.calapplyPushButton.setText(QCoreApplication.translate("MainWindow", u"Calculate Apply\n"
" Calibration", None))
        self.markvershapePushButton.setText(QCoreApplication.translate("MainWindow", u"Mark Verification \n"
"Shape", None))
        self.ezcadclosePushButton.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.notifyLabel.setText(QCoreApplication.translate("MainWindow", u"Notification", None))
        self.notifyTextEdit.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Notification Message</p></body></html>", None))
        self.footerLabel.setText(QCoreApplication.translate("MainWindow", u"Copyright Sp\u00e9cialis\u00e9 Products Pvt. Ltd.", None))
    # retranslateUi

