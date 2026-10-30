import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../.."

ComboBox {
    id: control

    property int customRadius: 5
    property color customBg: Theme.bgInput
    property color customBorder: activeFocus ? Theme.accentCyan : (hovered ? Theme.accentCyan : Theme.borderInput)

    // Searchable capabilities
    property bool searchable: false
    property string searchPlaceholder: "Search..."
    property string searchFilter: ""
    property var filteredModel: []

    implicitWidth: 160
    implicitHeight: 32

    font.family: "Segoe UI, Inter, sans-serif"
    font.pixelSize: 11
    font.weight: Font.DemiBold

    leftPadding: 10
    rightPadding: 26
    topPadding: 0
    bottomPadding: 0

    function updateFilteredModel() {
        if (!control.model) {
            filteredModel = []
            return
        }
        var raw = control.model
        if (!searchable || !searchFilter || searchFilter.trim() === "") {
            filteredModel = (typeof raw.slice === "function") ? raw.slice() : raw
            return
        }
        var q = searchFilter.trim().toLowerCase()
        var res = []
        var len = raw.length || 0
        for (var i = 0; i < len; i++) {
            var item = raw[i]
            var itemStr = (control.textRole && item[control.textRole]) ? item[control.textRole] : String(item)
            if (itemStr.toLowerCase().indexOf(q) !== -1) {
                res.push(item)
            }
        }
        filteredModel = res
    }

    onModelChanged: updateFilteredModel()
    onSearchFilterChanged: updateFilteredModel()
    Component.onCompleted: updateFilteredModel()

    contentItem: RowLayout {
        spacing: 6
        Text {
            visible: control.searchable
            text: "🔍"
            font.pixelSize: 10
            color: control.down || control.hovered ? Theme.accentCyan : (Theme.isDark ? "#94A3B8" : "#64748B")
            Layout.alignment: Qt.AlignVCenter
        }
        Text {
            Layout.fillWidth: true
            text: control.displayText
            font: control.font
            color: control.enabled ? Theme.textPrimary : Theme.textMuted
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }

    indicator: Text {
        x: control.width - width - 10
        anchors.verticalCenter: control.verticalCenter
        text: "▾"
        font.pixelSize: 12
        font.bold: true
        color: control.down ? Theme.accentCyan : (control.hovered ? Theme.accentCyan : (Theme.isDark ? "#94A3B8" : "#64748B"))
    }

    background: Rectangle {
        implicitWidth: control.implicitWidth
        implicitHeight: control.implicitHeight
        color: control.customBg
        border.color: control.customBorder
        border.width: 1
        radius: control.customRadius

        Behavior on border.color { ColorAnimation { duration: 120 } }
    }

    popup: Popup {
        id: comboPopup
        y: control.height + 2
        width: control.searchable ? Math.max(control.width, 240) : control.width
        implicitHeight: control.searchable ? 260 : Math.min(240, (control.count || 0) * 28 + 16)
        padding: 4

        onAboutToShow: {
            if (control.searchable) {
                control.searchFilter = ""
                control.updateFilteredModel()
                Qt.callLater(function() {
                    if (typeof searchInput !== "undefined" && searchInput) {
                        searchInput.forceActiveFocus()
                    }
                })
            }
        }

        contentItem: ColumnLayout {
            spacing: 4

            // Top Search Bar (Only shown when searchable is true)
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 30
                visible: control.searchable
                radius: 4
                color: Theme.bgInput
                border.color: (typeof searchInput !== "undefined" && searchInput.activeFocus) ? Theme.accentCyan : Theme.borderInput
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 8
                    spacing: 6

                    Text {
                        text: "🔍"
                        font.pixelSize: 10
                        color: Theme.accentCyan
                    }

                    TextInput {
                        id: searchInput
                        Layout.fillWidth: true
                        font.family: "Segoe UI, Inter, sans-serif"
                        font.pixelSize: 11
                        color: Theme.textPrimary
                        selectByMouse: true
                        clip: true
                        text: control.searchFilter

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: control.searchPlaceholder
                            visible: !searchInput.text && !searchInput.activeFocus
                            color: Theme.textMuted
                            font: searchInput.font
                        }

                        onTextChanged: control.searchFilter = text

                        Keys.onReturnPressed: function(event) {
                            if (control.filteredModel && control.filteredModel.length > 0) {
                                control.selectItem(control.filteredModel[0])
                            }
                            event.accepted = true
                        }
                        Keys.onEnterPressed: function(event) {
                            if (control.filteredModel && control.filteredModel.length > 0) {
                                control.selectItem(control.filteredModel[0])
                            }
                            event.accepted = true
                        }
                        Keys.onEscapePressed: function(event) {
                            comboPopup.close()
                            event.accepted = true
                        }
                    }

                    // Count badge
                    Text {
                        text: (control.filteredModel ? control.filteredModel.length : 0) + (control.model ? ("/" + control.model.length) : "")
                        font.pixelSize: 9
                        font.family: "Consolas, monospace"
                        color: Theme.textMuted
                        visible: control.searchable && control.model && control.model.length > 5
                    }

                    // Clear button
                    Text {
                        text: "✕"
                        font.pixelSize: 10
                        color: clearMa.containsMouse ? Theme.accentCyan : Theme.textMuted
                        visible: searchInput.text.length > 0
                        MouseArea {
                            id: clearMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                searchInput.text = ""
                                control.searchFilter = ""
                                searchInput.forceActiveFocus()
                            }
                        }
                    }
                }
            }

            // Results List
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ListView {
                    id: popupListView
                    anchors.fill: parent
                    clip: true
                    model: control.searchable ? control.filteredModel : (control.popup.visible ? control.delegateModel : null)
                    currentIndex: control.searchable ? -1 : control.highlightedIndex

                    delegate: ItemDelegate {
                        width: popupListView.width
                        implicitHeight: 28
                        highlighted: {
                            if (control.searchable) {
                                var val = (typeof modelData !== "undefined") ? (control.textRole ? modelData[control.textRole] : modelData) : ""
                                return val === control.currentText
                            }
                            return control.highlightedIndex === index
                        }

                        contentItem: Text {
                            text: (typeof modelData !== "undefined") ? (control.textRole ? modelData[control.textRole] : modelData) : ""
                            color: highlighted ? Theme.accentCyan : Theme.textPrimary
                            font: control.font
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                            leftPadding: 8
                        }

                        background: Rectangle {
                            radius: 4
                            color: highlighted ? (Theme.isDark ? "#1C2B48" : "#E2E8F0") : (hovered ? (Theme.isDark ? "#162035" : "#F1F5F9") : "transparent")
                        }

                        onClicked: {
                            if (control.searchable) {
                                var val = (typeof modelData !== "undefined") ? (control.textRole ? modelData[control.textRole] : modelData) : ""
                                control.selectItem(val)
                            }
                        }
                    }

                    ScrollIndicator.vertical: ScrollIndicator { }
                }

                // Empty Results Placeholder
                Text {
                    anchors.centerIn: parent
                    visible: control.searchable && control.filteredModel && control.filteredModel.length === 0
                    text: "No fonts matching \"" + control.searchFilter + "\""
                    font.family: "Segoe UI, Inter, sans-serif"
                    font.pixelSize: 11
                    color: Theme.textMuted
                }
            }
        }

        background: Rectangle {
            color: Theme.bgCard
            border.color: Theme.borderCard
            border.width: 1
            radius: control.customRadius
        }
    }

    function selectItem(val) {
        var strVal = (control.textRole && val[control.textRole]) ? val[control.textRole] : String(val)
        var fullIdx = -1
        if (control.model) {
            for (var i = 0; i < control.model.length; i++) {
                var mStr = (control.textRole && control.model[i][control.textRole]) ? control.model[i][control.textRole] : String(control.model[i])
                if (mStr === strVal) {
                    fullIdx = i
                    break
                }
            }
        }
        if (fullIdx >= 0) {
            control.currentIndex = fullIdx
        }
        control.displayText = strVal
        control.activated(fullIdx)
        control.popup.close()
    }
}
