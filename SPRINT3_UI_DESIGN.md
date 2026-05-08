# 🎨 Sprint 3 Dashboard - UI/UX Design

## Preview Description

The dashboard at `/dashboard/anomalies` provides a complete anomaly management interface.

---

## 📱 Layout Overview

```
┌─────────────────────────────────────────────────────────┐
│  SmartMeter Platform - Dark Theme (#0f1117)             │
└─────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════╗
║  🚨 Anomalies Détectées                                 ║
║  Gestion des anomalies de consommation avec scores HF   ║
╚═════════════════════════════════════════════════════════╝

┌───────────┬───────────┬───────────┬───────────┐
│ Nouvelles │ Critiques │Consultées │Acquittées │
│     5     │     2     │     1     │     3     │
│  (cyan)   │   (red)   │  (blue)   │   (gray)  │
└───────────┴───────────┴───────────┴───────────┘

╔═════════════════════════════════════════════════════════╗
║  Statut:  [ Tous ] [NOUVELLE] [CONSULTEE] [ACQUITTEE]  ║
║  Sévérité:[ Tous ] [BASSE] [MOYENNE] [HAUTE] [CRITIQUE]║
╚═════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════╗
║ Foyer │ Date│Consomm.│  Score HF  │Sévérité│Statut  │Action  ║
╠════════════════════════════════════════════════════════════════╣
║ F001  │2024 │ 95.5   │ |████| 95% │ 🔴     │🆕 Nvl  │Acqui.  ║
║       │5-04 │ kWh    │ (Rouge)    │        │        │✓       ║
║       │14:30│        │            │        │        │        ║
╠════════════════════════════════════════════════════════════════╣
║ F002  │2024 │ 78.2   │ |███| 72%  │ 🟠     │🆕 Nvl  │Acqui.  ║
║       │5-04 │ kWh    │ (Orange)   │        │        │✓       ║
║       │15:45│        │            │        │        │        ║
╠════════════════════════════════════════════════════════════════╣
║ F003  │2024 │ 45.0   │ |█| 38%    │ 🟡     │✓ Cons. │Acqui.  ║
║       │5-03 │ kWh    │ (Amber)    │        │        │✓       ║
║       │09:15│        │            │        │        │        ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Components Details

### Statistics Cards

```
┌──────────────────┬──────────────────┐
│                  │                  │
│  Nouvelles       │  Critiques       │
│  ●●●●●           │  ●●               │
│                  │                  │
│  Cyan Glow       │  Red Glow        │
└──────────────────┴──────────────────┘

┌──────────────────┬──────────────────┐
│                  │                  │
│  Consultées      │  Acquittées      │
│  ●                │  ●●●             │
│                  │                  │
│  Blue Glow       │  Gray Glow       │
└──────────────────┴──────────────────┘
```

**Animation:** Stagger in on load (0, 100ms, 200ms, 300ms)

### Filter Buttons

```
STATUS:
[ Tous ] ← Active (cyan bg)
[NOUVELLE] [CONSULTEE] [ACQUITTEE]

SEVERITY:
[ Tous ] ← Active (cyan bg)
[BASSE] [MOYENNE] [HAUTE] [CRITIQUE]
```

**Active State:** `bg-cyan-500 text-white`
**Inactive State:** `bg-slate-800 text-gray-400`
**Hover:** Slightly brighter

### Table Header

```
┌────────┬──────┬──────────┬──────────┬───────────┬────────┬────────┐
│ Foyer  │ Date │ Consumm. │ Score HF │ Sévérité  │ Statut │ Action │
│        │      │          │          │           │        │        │
│ Navy bg│ Navy │  Navy bg │  Navy bg │  Navy bg  │ Navy   │ Navy   │
└────────┴──────┴──────────┴──────────┴───────────┴────────┴────────┘
```

### Table Rows

**Alternating:** 
- Even rows: `bg-slate-900/50`
- Odd rows: `bg-slate-800/30`
- Hover: `bg-slate-800/50`

### Foyer Column

```
  F001
  ↑ Monospace, Cyan color (#00d4ff), Bold
```

### Date Column

```
  2024-05-04 14:30
  ↑ Formatted with localeString('fr-FR')
  ↑ Gray color
```

### Consumption Column

```
  95.5 kWh
  ↑ Monospace, White, Bold
```

### Score Bar

```
Low Score (38%):
┌─────────────────────────────────────┐
│ ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  38%
│ ↑ Cyan                              │
└─────────────────────────────────────┘

Medium Score (72%):
┌─────────────────────────────────────┐
│ ██████████████████░░░░░░░░░░░░░░░░  │  72%
│ ↑ Orange                            │
└─────────────────────────────────────┘

High Score (95%):
┌─────────────────────────────────────┐
│ ████████████████████████████████░░  │  95%
│ ↑ Red                               │
└─────────────────────────────────────┘
```

### Severity Badge

```
BASSE:     🟡 Basse
           Amber bg, Amber text

MOYENNE:   🟡 Moyenne
           Amber bg, Amber text

HAUTE:     🟠 Haute
           Orange bg, Orange text

CRITIQUE:  🔴 Critique (PULSING)
           Red bg, Red text
           With animated dot: pulse 1s
```

### Status Badge

```
NOUVELLE:     🆕 Nouvelle
              Cyan bg, Cyan text

CONSULTEE:    👁️ Consultée
              Blue bg, Blue text

ACQUITTEE:    ✓ Acquittée
              Gray bg, Gray text
```

### Acknowledge Button

```
┌──────────────────────────────┐
│ ✓  Acquitter                 │
│ Green bg on hover            │
│ Text-green-400               │
│ Cursor: pointer              │
└──────────────────────────────┘

Click → Toast appears:
┌──────────────────────────────────────┐
│ ✓ Anomalie acquittée                 │
│   L'anomalie a été marquée comme ... │
└──────────────────────────────────────┘
```

### Animations

**Table Row Entry:**
```
Initial:  opacity: 0, x: -10
Animate:  opacity: 1, x: 0
Duration: 0.3s
Delay:    index * 0.03s (stagger)
```

**Stats Cards:**
```
Sequence:
Card 1: 0ms    delay
Card 2: 100ms  delay
Card 3: 200ms  delay
Card 4: 300ms  delay
```

**Score Bar Fill:**
```
Animation: width transition
Duration:  0.5s
Easing:    ease-out
```

---

## 🎨 Color Palette

```
Background:
  Primary:     #0f1117 (slate-900)
  Secondary:   #1e293b (slate-800)
  Tertiary:    #0f172a (slate-950)

Accent Colors:
  Cyan:        #00d4ff (cyan-400)
  Orange:      #f97316 (orange-400)
  Red:         #ff4d6d (red-400)
  Amber:       #ffb800 (amber-400)
  Green:       #22c55e (green-400)

Text Colors:
  Primary:     #ffffff (white)
  Secondary:   #d1d5db (gray-300)
  Muted:       #9ca3af (gray-400)
  Disabled:    #6b7280 (gray-500)
```

---

## 📱 Responsive Behavior

```
Mobile (< 768px):
├─ Stack layout
├─ Single column for stats
├─ Horizontal scroll for table
└─ Full-width buttons

Tablet (768px - 1024px):
├─ 2x2 grid for stats
├─ Normal table
└─ Medium padding

Desktop (> 1024px):
├─ 4 column grid for stats
├─ Full table display
└─ Comfortable spacing
```

---

## 🎬 User Flows

### Flow 1: View Anomalies

```
1. User opens /dashboard/anomalies
   ├─ Loading spinner appears
   ├─ Hook fetches from API
   └─ API returns anomalies list

2. Table renders with animations
   ├─ Each row slides in
   ├─ Staggered 30ms apart
   └─ Takes ~300ms total

3. User sees:
   ├─ Stats cards with counts
   ├─ Animated table
   ├─ Filter options
   └─ Action buttons
```

### Flow 2: Filter Anomalies

```
1. User clicks filter button (e.g., "CRITIQUE")
   ├─ Active state changes to cyan
   └─ State updates in component

2. Hook re-fetches with filters
   ├─ Sends ?severite=CRITIQUE
   └─ API filters results

3. Table updates
   ├─ Old rows animate out
   ├─ New rows slide in
   └─ Stats update
```

### Flow 3: Acknowledge Anomaly

```
1. User clicks "Acquitter" button
   └─ Button shows loading state

2. Hook sends PATCH request
   ├─ POST /api/.../marquer_acquittee/
   └─ Optimistic update: status → ACQUITTEE

3. Server responds
   ├─ Returns updated record
   └─ Toast success appears

4. UI Updates
   ├─ Row status changes to gray
   ├─ Button becomes disabled
   └─ "Acquittée" text appears
```

### Flow 4: Error Handling

```
1. API call fails
   ├─ Toast error appears
   ├─ Row reverts to original state
   └─ Message: "Erreur: impossible d'..."

2. Network timeout
   ├─ Loading spinner shows
   ├─ Retry automatically
   └─ Or show error message

3. No anomalies
   ├─ Loading spinner disappears
   ├─ Empty state shows
   ├─ Message: "✨ Aucune anomalie"
   └─ User can adjust filters
```

---

## ⌨️ Keyboard Navigation

- `Tab`: Navigate buttons and table rows
- `Enter`: Click active button/row
- `Escape`: Close modals (if any)
- `Ctrl+Enter`: Quick acknowledge (can add)

---

## 🔊 Accessibility

✅ Semantic HTML (table, button, etc.)
✅ Color not only indicator (icons + text)
✅ ARIA labels on dynamic content
✅ Keyboard navigation support
✅ Contrast ratios AA standard
✅ Focus states visible

---

## 📊 Data Display Examples

### Example 1: High Risk Anomaly

```
Foyer:     F001 (cyan)
Date:      05-04 14:30
Consumm.:  95.5 kWh
Score:     |████████████████| 95% (Red)
Severity:  🔴 Critique (red, pulsing)
Status:    🆕 Nouvelle (cyan)
Action:    [✓ Acquitter] (green hover)
```

### Example 2: Medium Risk Anomaly

```
Foyer:     F002 (cyan)
Date:      05-04 15:45
Consumm.:  78.2 kWh
Score:     |████████████| 72% (Orange)
Severity:  🟠 Haute (orange)
Status:    🆕 Nouvelle (cyan)
Action:    [✓ Acquitter] (green hover)
```

### Example 3: Low Risk, Consulted

```
Foyer:     F003 (cyan)
Date:      05-03 09:15
Consumm.:  45.0 kWh
Score:     |████| 38% (Cyan)
Severity:  🟡 Basse (amber)
Status:    👁️ Consultée (blue)
Action:    [✓ Acquitter] (green hover)
```

### Example 4: Acknowledged

```
Foyer:     F004 (cyan)
Date:      05-02 11:00
Consumm.:  62.3 kWh
Score:     |██████| 55% (Cyan)
Severity:  🟡 Moyenne (amber)
Status:    ✓ Acquittée (gray)
Action:    Acquittée (gray text)
```

---

## 📈 Performance Metrics

- **Page Load:** < 1s
- **Filter Response:** < 200ms
- **Table Animation:** ~300ms (30 rows)
- **Toast Duration:** 3s default
- **API Timeout:** 15s (Hugging Face)

---

## 🎉 Visual Hierarchy

```
1st Level:  Page title + description
2nd Level:  Statistics cards (4 cards)
3rd Level:  Filter section + table
4th Level:  Individual rows + actions
5th Level:  Toast notifications
```

---

This completes the Sprint 3 UI/UX specification. The implementation uses:
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons
- **Sonner** for notifications
- **Dark theme** with cyan accents
- **Responsive design** (mobile to desktop)
