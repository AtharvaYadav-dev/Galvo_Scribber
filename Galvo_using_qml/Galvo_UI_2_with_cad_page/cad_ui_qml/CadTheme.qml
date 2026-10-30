pragma Singleton
import QtQuick

QtObject {
    id: theme

    // Toggleable reactive Dark / Light theme state
    property bool isDark: true

    function toggleTheme() {
        isDark = !isDark
    }

    // --- Backgrounds & Surface Foundations ---
    readonly property color bgApp: isDark ? "#0A0F1D" : "#F3F6FA"
    readonly property color bgWorkspace: isDark ? "#060A14" : "#EAEFF6"
    readonly property color bgHeader: isDark ? "#0F172A" : "#FFFFFF"
    readonly property color bgCard: isDark ? "#10192D" : "#FFFFFF"
    readonly property color bgCardAlt: isDark ? "#141F36" : "#F8FAFC"
    readonly property color bgCardHeader: isDark ? "#17233D" : "#F1F5F9"
    readonly property color bgToolbox: isDark ? "#0D1527" : "#FFFFFF"
    readonly property color bgRuler: isDark ? "#0A0F1D" : "#F8FAFC"

    // --- Borders & Separators ---
    readonly property color borderMuted: isDark ? "#19243C" : "#E2E8F0"
    readonly property color borderCard: isDark ? "#1E2C4A" : "#DCE3EE"
    readonly property color borderActive: isDark ? "#00E5FF" : "#192D78"
    readonly property color borderHighlight: isDark ? "#38BDF8" : "#2563EB"

    // --- Inputs & Controls ---
    readonly property color bgInput: isDark ? "#0B1120" : "#F1F5F9"
    readonly property color borderInput: isDark ? "#223150" : "#CBD5E1"
    readonly property color borderInputFocus: isDark ? "#00E5FF" : "#1D4ED8"
    readonly property color placeholderInput: isDark ? "#4B5E80" : "#94A3B8"

    // --- Typography Colors ---
    readonly property color textPrimary: isDark ? "#FFFFFF" : "#0F172A"
    readonly property color textSecondary: isDark ? "#94A3B8" : "#475569"
    readonly property color textMuted: isDark ? "#64748B" : "#94A3B8"
    readonly property color textBrand: isDark ? "#00E5FF" : "#192D78"
    readonly property color textCode: isDark ? "#38BDF8" : "#0F172A"

    // --- Brand & Functional Accents ---
    readonly property color accentCyan: isDark ? "#00E5FF" : "#0284C7"
    readonly property color accentAmber: isDark ? "#F59E0B" : "#D97706"
    readonly property color accentGreen: isDark ? "#10B981" : "#059669"
    readonly property color accentRed: isDark ? "#EF4444" : "#DC2626"
    readonly property color accentBlue: isDark ? "#3B82F6" : "#1D4ED8"
    readonly property color accentPurple: isDark ? "#A855F7" : "#7C3AED"

    // --- Buttons ---
    readonly property color btnPrimaryBg: isDark ? "#1D4ED8" : "#192D78"
    readonly property color btnPrimaryHover: isDark ? "#2563EB" : "#10204D"
    readonly property color btnPrimaryText: "#FFFFFF"

    readonly property color btnSecondaryBg: isDark ? "#17233D" : "#FFFFFF"
    readonly property color btnSecondaryHover: isDark ? "#203052" : "#F1F5F9"
    readonly property color btnSecondaryText: isDark ? "#E2E8F0" : "#1E293B"
    readonly property color btnSecondaryBorder: isDark ? "#26395E" : "#CBD5E1"

    readonly property color btnRedPointerBg: isDark ? "#7C2D12" : "#FEF3C7"
    readonly property color btnRedPointerHover: isDark ? "#9A3412" : "#FDE68A"
    readonly property color btnRedPointerText: isDark ? "#FDBA74" : "#B45309"
    readonly property color btnRedPointerBorder: isDark ? "#EA580C" : "#F59E0B"

    readonly property color btnMarkBg: isDark ? "#064E3B" : "#D1FAE5"
    readonly property color btnMarkHover: isDark ? "#065F46" : "#A7F3D0"
    readonly property color btnMarkText: isDark ? "#6EE7B7" : "#065F46"
    readonly property color btnMarkBorder: isDark ? "#10B981" : "#059669"

    // --- CAD Canvas Rendering System ---
    readonly property color canvasBg: isDark ? "#070B14" : "#F8FAFC"
    readonly property color canvasGridMinor: isDark ? "#0E1626" : "#EDF2F7"
    readonly property color canvasGridMajor: isDark ? "#18243C" : "#DDE5EF"
    readonly property color canvasAxis: isDark ? "#2A3A54" : "#94A3B8"
    readonly property color canvasBedBorder: isDark ? "#00E5FF" : "#192D78"
    readonly property color canvasBedFill: isDark ? Qt.rgba(0, 229, 255, 0.015) : Qt.rgba(25, 45, 120, 0.02)
    readonly property color canvasSelectionBox: isDark ? "#00E5FF" : "#1D4ED8"
    readonly property color canvasHandleFill: isDark ? "#00E5FF" : "#1D4ED8"
    readonly property color canvasHandleBorder: "#FFFFFF"
    readonly property color canvasRulerText: isDark ? "#64748B" : "#64728A"
    readonly property color canvasRulerTick: isDark ? "#223150" : "#CBD5E1"
    readonly property color canvasRulerTracker: isDark ? "#00E5FF" : "#192D78"

    // --- 8 Industrial Laser Pens / Layers Palette ---
    readonly property var penPalette: [
        { id: 0, name: "Pen 0 (Default)", color: isDark ? "#FFFFFF" : "#000000", speed: 1200, power: 50, freq: 35, passes: 1 },
        { id: 1, name: "Pen 1 (Blue)",    color: "#2563EB", speed: 1800, power: 40, freq: 45, passes: 1 },
        { id: 2, name: "Pen 2 (Red)",     color: "#EF4444", speed: 800,  power: 75, freq: 30, passes: 2 },
        { id: 3, name: "Pen 3 (Green)",   color: "#10B981", speed: 2000, power: 30, freq: 60, passes: 1 },
        { id: 4, name: "Pen 4 (Amber)",   color: "#F59E0B", speed: 1500, power: 60, freq: 40, passes: 1 },
        { id: 5, name: "Pen 5 (Purple)",  color: "#A855F7", speed: 1000, power: 70, freq: 35, passes: 1 },
        { id: 6, name: "Pen 6 (Cyan)",    color: "#06B6D4", speed: 2200, power: 25, freq: 70, passes: 1 },
        { id: 7, name: "Pen 7 (Brown)",   color: "#854D0E", speed: 600,  power: 85, freq: 25, passes: 3 }
    ]
}
