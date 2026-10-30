import QtQuick
import QtQuick.Controls

Item {
    id: root
    width: 400
    height: 400

    property var myList: [
        { name: "A", locked: false },
        { name: "B", locked: false }
    ]

    Column {
        spacing: 10
        Button {
            text: "Toggle Lock 0"
            onClicked: {
                var copy = root.myList.slice()
                var item = Object.assign({}, copy[0])
                item.locked = !item.locked
                copy[0] = item
                root.myList = copy
                console.log("Updated myList, item 0 locked is now:", root.myList[0].locked)
            }
        }

        Repeater {
            model: root.myList
            Rectangle {
                width: 200
                height: 30
                color: modelData.locked ? "red" : "green"
                Text {
                    text: modelData.name + " locked=" + modelData.locked
                }
            }
        }
    }
}

