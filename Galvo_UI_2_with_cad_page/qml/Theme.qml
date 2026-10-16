pragma Singleton
import QtQuick

QtObject {
    // Dark Industrial Theme Palette
    readonly property color bgDark: "#0c0e14"
    readonly property color bgSidebar: "#13161f"
    readonly property color bgCard: "#1a1e29"
    readonly property color bgCardHover: "#232837"
    readonly property color bgInput: "#10131a"
    readonly property color border: "#282f40"
    readonly property color borderLight: "#384259"
    
    // Accents
    readonly property color primary: "#00d2ff"
    readonly property color primaryGlow: "#3300d2ff"
    readonly property color accentYellow: "#f5a623"
    readonly property color success: "#2ed573"
    readonly property color danger: "#ff4757"
    readonly property color dangerGlow: "#40ff4757"
    
    // Text colors
    readonly property color textPrimary: "#ffffff"
    readonly property color textSecondary: "#9aa6b8"
    readonly property color textMuted: "#5e697a"
    
    // Dimensions & Radii
    readonly property int radiusSm: 4
    readonly property int radiusMd: 8
    readonly property int radiusLg: 12
}
