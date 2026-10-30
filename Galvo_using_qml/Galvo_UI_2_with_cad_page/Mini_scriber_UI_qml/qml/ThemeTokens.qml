import QtQuick

QtObject {
    id: theme

    // Direct reactive binding to python SettingsBridge
    readonly property bool isDark: (typeof settings !== "undefined" && settings) ? settings.isDark : true

    // --- Backgrounds & Surfaces ---
    readonly property color bgApp: isDark ? "#0B1220" : "#F1F4F8"
    readonly property color bgHeader: isDark ? "#0F172A" : "#FFFFFF"
    readonly property color borderHeader: isDark ? "#1E293B" : "#DCE2EC"

    readonly property color bgFooter: isDark ? "#0F172A" : "#FFFFFF"
    readonly property color borderFooter: isDark ? "#1E293B" : "#DCE2EC"

    readonly property color bgSidebar: isDark ? "#0B1220" : "#10204D"
    readonly property color borderSidebar: isDark ? "#1E293B" : "#10204D"
    readonly property color sidebarNavLabel: isDark ? "#64748B" : "#A6B1C4"
    readonly property color sidebarItemHover: isDark ? "#162032" : "#192D78"
    readonly property color sidebarItemActive: isDark ? "#1E293B" : "#192D78"
    readonly property color sidebarItemActiveBorder: isDark ? "#2A3A54" : "#354B94"
    readonly property color sidebarTextInactive: isDark ? "#94A3B8" : "#A6B1C4"
    readonly property color sidebarTextActive: "#FFFFFF"
    readonly property color sidebarIconActive: "#D6AF3E"
    readonly property color sidebarBadgeBg: isDark ? "#172338" : "#172338"

    // --- Cards & Panels ---
    readonly property color bgCard: isDark ? "#0F172A" : "#FFFFFF"
    readonly property color cardBg: bgCard
    readonly property color borderCard: isDark ? "#1E293B" : "#DCE2EC"
    readonly property color bgCardAlt: isDark ? "#111827" : "#F8FAFC"
    readonly property color bgCardHeader: isDark ? "#141A29" : "#F1F4F8"

    // --- Inputs & Controls ---
    readonly property color bgInput: isDark ? "#111827" : "#F1F4F8"
    readonly property color borderInput: isDark ? "#1E293B" : "#DCE2EC"
    readonly property color borderInputFocus: isDark ? "#3B82F6" : "#192D78"
    readonly property color placeholderInput: isDark ? "#475569" : "#94A3B8"

    // --- Typography ---
    readonly property color textPrimary: isDark ? "#FFFFFF" : "#172440"
    readonly property color textSecondary: isDark ? "#94A3B8" : "#64728A"
    readonly property color textMuted: isDark ? "#64748B" : "#94A3B8"
    readonly property color textBrand: isDark ? "#FFFFFF" : "#192D78"
    readonly property color textCode: isDark ? "#E2E8F0" : "#172440"

    // --- Accents & Highlighting (Matching Figma) ---
    readonly property color accentAmber: "#D6AF3E"
    readonly property color accentCyan: isDark ? "#00E5FF" : "#0284C7"
    readonly property color accentGreen: isDark ? "#34D399" : "#13835D"
    readonly property color accentRed: "#C72E36"
    readonly property color accentBlue: isDark ? "#3B82F6" : "#192D78"

    // --- Status Pills ---
    readonly property color pillOnlineBg: isDark ? "#062E20" : "#E6F5EE"
    readonly property color pillOnlineBorder: isDark ? "#065F46" : "#A7F3D0"
    readonly property color pillOnlineText: isDark ? "#34D399" : "#13835D"

    readonly property color pillOfflineBg: isDark ? "#2A0E12" : "#FEE2E2"
    readonly property color pillOfflineBorder: isDark ? "#7F1D1D" : "#FECACA"
    readonly property color pillOfflineText: isDark ? "#F87171" : "#C72E36"

    readonly property color pillRoleBg: isDark ? "#1E293B" : "#F1F4F8"
    readonly property color pillRoleBorder: isDark ? "#334155" : "#DCE2EC"
    readonly property color pillRoleText: isDark ? "#E2E8F0" : "#172440"

    // --- DRO & Motion Readouts ---
    readonly property color droCardBg: isDark ? "#0F172A" : "#FFFFFF"
    readonly property color droBorder: isDark ? "#1E293B" : "#DCE2EC"
    readonly property color droBadgeBg: isDark ? "#1E293B" : "#E9EDF9"
    readonly property color droBadgeText: isDark ? "#E2E8F0" : "#192D78"
    readonly property color droNumber: isDark ? "#FFFFFF" : "#172440"
    readonly property color droUnit: isDark ? "#94A3B8" : "#64728A"

    // --- Jog Stage & Pads ---
    readonly property color jogPlateBg: isDark ? "#0F172A" : "#F1F4F8"
    readonly property color jogPlateBorder: isDark ? "#334155" : "#DCE2EC"
    readonly property color jogBtnBg: isDark ? "#111827" : "#FFFFFF"
    readonly property color jogBtnBorder: isDark ? "#334155" : "#DCE2EC"
    readonly property color jogBtnHover: isDark ? "#1E293B" : "#F8FAFC"
    readonly property color jogBtnText: isDark ? "#D6AF3E" : "#192D78"
    readonly property color jogCenterBg: isDark ? "#1E293B" : "#E9EDF9"
    readonly property color jogCenterBorder: isDark ? "#334155" : "#DCE2EC"
    readonly property color jogCenterText: isDark ? "#D6AF3E" : "#192D78"

    // --- Buttons ---
    readonly property color btnPrimaryBg: isDark ? "#1D4ED8" : "#192D78"
    readonly property color btnPrimaryHover: isDark ? "#2563EB" : "#10204D"
    readonly property color btnPrimaryText: "#FFFFFF"
    readonly property color btnPrimaryBorder: isDark ? "#3B82F6" : "#192D78"

    readonly property color btnSecondaryBg: isDark ? "#111827" : "#FFFFFF"
    readonly property color btnSecondaryHover: isDark ? "#1E293B" : "#F1F4F8"
    readonly property color btnSecondaryText: isDark ? "#E2E8F0" : "#172440"
    readonly property color btnSecondaryBorder: isDark ? "#1E293B" : "#DCE2EC"

    readonly property color btnDangerBg: "#C72E36"
    readonly property color btnDangerHover: "#B91C1C"
    readonly property color btnDangerText: "#FFFFFF"
    readonly property color btnDangerBorder: "#C72E36"

    readonly property color btnAmberBg: isDark ? "#2E2413" : "#FEF3C7"
    readonly property color btnAmberHover: isDark ? "#3E3019" : "#FDE68A"
    readonly property color btnAmberText: isDark ? "#FCD34D" : "#92400E"
    readonly property color btnAmberBorder: isDark ? "#785814" : "#F59E0B"

    // --- Toolpath Preview Canvas ---
    readonly property color canvasBg: isDark ? "#080D18" : "#0F172A"
    readonly property color canvasGrid: isDark ? "#131C2E" : "#1E293B"
    readonly property color canvasGridAxis: isDark ? "#23334E" : "#334155"
    readonly property color canvasBedBorder: isDark ? "#2A3A54" : "#475569"
    readonly property color canvasCut: "#00E5FF"
    readonly property color canvasTravel: isDark ? "#64748B" : "#94A3B8"
    readonly property color canvasLaserHead: "#EF4444"
    readonly property color canvasOrigin: "#D6AF3E"
}
