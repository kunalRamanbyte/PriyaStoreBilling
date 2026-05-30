# Product Design — Apple-Level Standard
**Author:** renat  
**Date Added:** 2026-03-06  
**Source:** Community  
**Risk:** None  

## Overview
Elite Apple-level product design — visual systems, UX flows, accessibility, proprietary visual language, design tokens, prototyping, and handoff. Covers Figma, design systems, typography, color, spacing, motion design, and cognitive design principles. 

*Activate for: building design systems, defining visual language, conducting UX audits, establishing design tokens, product branding, and structured UI critiques.*

---

## Jony Ive's 10 Apple Design Principles
1. **Radical Simplicity:** Strip away everything that is not absolutely essential to the user's primary goal.
2. **Material Honesty:** Every component, texture, and element must exist for a clear structural or context-driven reason.
3. **Restraint is Design:** True elegance comes from deliberate exclusion; "less is more" is a product discipline.
4. **Systemic Coherence:** Every button, card, and icon belongs to a single, unified visual family and ecosystem.
5. **Obsession with Detail:** Users feel the quality of details (margins, transitions, border curvatures) even if they cannot consciously name them.
6. **Function Governs Form:** Aesthetic appeal should always serve to explain, enhance, and guide function.
7. **Timeless Longevity:** Design products that age gracefully, avoiding passing trends in favor of deep structural clarity.
8. **Accessibility by Default:** Inclusivity is not an add-on or a checklist; it is an foundational requirement of high quality.
9. **Fluid Continuity:** The experience should feel like a single, continuous stream across devices and layout viewports.
10. **Delightful Surprises:** Infuse micro-interactions and animations that surprise and charm the user at key moments of success.

---

## Cognitive Product Design
* **Zero Cognitive Load:** Design interfaces so intuitive that the user never has to spend mental cycles figuring out "how" to complete their task.
* **Obvious Affordances:** Interactive elements must visually communicate their clickability (using depth, hover states, clear iconography, and text casing).
* **Instant Tactile Feedback:** Every touch or click gets an immediate visual response (active scaling, color changes, wave animations).
* **Pervasive Error Prevention:** Build flows that make user errors impossible by hiding invalid actions or providing instant context-aware warnings.

---

## Elite Design System Architecture
```
design-system/
├── tokens/
│   ├── colors.json       # Color palette with semantic mapping
│   ├── typography.json   # Hierarchy, scale, weight, and line-heights
│   ├── spacing.json      # Grid boundaries and layout intervals
│   ├── shadows.json      # Elevation, depth, and glassmorphism levels
│   ├── motion.json       # Transition durations, easing curves, and keyframes
│   └── radius.json       # Corner rounding rules (squircles)
├── components/
│   ├── atoms/            # Buttons, Inputs, Icons, Badges, Checkboxes
│   ├── molecules/        # Cards, FilterBars, NavigationItems, FormGroups
│   └── organisms/        # PageHeaders, Sidebars, Modals, Heatmaps
├── patterns/
│   ├── onboarding.md     # First-time access tutorials
│   ├── empty-states.md   # Zero-data feedback illustrations
│   ├── loading.md        # Skeleton screens and progress tracking
│   └── errors.md         # Contextual recovery and input validation
└── guidelines/
    ├── voice-tone.md     # Voice UI personality, hooks, and cadences
    ├── imagery.md        # Proprietary photography, icons, and illustrations
    └── accessibility.md  # WCAG 2.2 AA and keyboard navigation mappings
```

---

## Core Design Tokens Example (Auri System)
```json
{
  "color": {
    "brand": {
      "primary": "#6C63FF",
      "primary-dark": "#5A52E0",
      "accent": "#FF6B6B",
      "surface": "#F8F7FF"
    },
    "semantic": {
      "success": "#22C55E",
      "warning": "#F59E0B",
      "error": "#EF4444",
      "info": "#3B82F6"
    },
    "neutral": {
      "900": "#111827",
      "800": "#1F2937",
      "600": "#4B5563",
      "400": "#9CA3AF",
      "200": "#E5E7EB",
      "50":  "#F9FAFB"
    }
  },
  "typography": {
    "display": { "size": "48px", "weight": "700", "line": "1.1" },
    "h1": { "size": "36px", "weight": "700", "line": "1.2" },
    "h2": { "size": "28px", "weight": "600", "line": "1.3" },
    "body": { "size": "16px", "weight": "400", "line": "1.6" },
    "small": { "size": "14px", "weight": "400", "line": "1.5" }
  },
  "spacing": {
    "xs": "4px", "sm": "8px", "md": "16px",
    "lg": "24px", "xl": "32px", "2xl": "48px", "3xl": "64px"
  },
  "radius": {
    "sm": "4px", "md": "8px", "lg": "12px",
    "xl": "16px", "full": "9999px"
  },
  "shadow": {
    "sm": "0 1px 3px rgba(0,0,0,0.12)",
    "md": "0 4px 12px rgba(0,0,0,0.15)",
    "lg": "0 8px 24px rgba(0,0,0,0.18)",
    "xl": "0 20px 60px rgba(0,0,0,0.22)"
  },
  "motion": {
    "fast": "150ms cubic-bezier(0.25, 0.1, 0.25, 1)",
    "normal": "250ms cubic-bezier(0.25, 0.1, 0.25, 1)",
    "slow": "400ms cubic-bezier(0.34, 1.56, 0.64, 1)"
  }
}
```

---

## Elite UX Flow Architecture
1. **Entry Point:** How does the user discover this flow? What triggers their entry?
2. **Context:** What is the user's current goal, device layout, and emotional state?
3. **Action:** What is the single, friction-free action they are prompted to complete?
4. **Immediate Feedback:** What visual confirmation shows the action succeeded?
5. **Outcome:** What did the user successfully achieve? Show them the value immediately.
6. **Natural Next Step:** Where does the experience flow logically to maintain engagement?

---

## Onboarding Excellence (First 5 Minutes)
* **Step 1: The Promise (Core Value Proposition)**
  * A clear, bold, impact-focused tagline.
  * A stunning visual representation showing the final value.
  * Action-focused CTA: **"Start"** or **"Explore"** (never "Sign Up" or "Create Account").
* **Step 2: Immediate Utility (First Value Before Friction)**
  * Allow the user to play, generate, or experiment with a core feature before demanding registration.
  * Form inputs are reduced to absolute minimums (e.g., email or guest pass).
  * Visible steps indicator (e.g., Progress 1 of 3) to outline duration.
* **Step 3: Subtle Personalization**
  * Ask a maximum of three curated questions to tailor the interface.
  * Use visual cards or selectors instead of text inputs.
  * Always provide an obvious **"Skip"** button to prioritize velocity.
* **Step 4: The AHA Success Moment**
  * The user experiences their first real, positive output.
  * Celebrate with premium, restrained micro-animations.
  * Display a simple success message: *"You have just created your first X!"*

---

## Delightful Empty States
Never show a blank slate with *"No items found."* Instead, build engagement:
* **Contextual Graphic:** A beautiful, soft illustration matching the feature context.
* **Opportunity Statement:** *"You haven't created any feedback reports yet. Let's build your first department review!"*
* **Primary Call-To-Action:** A clear, visible, rounded button to launch creation.
* **Quick-Start Tip:** A brief, helpful hint on how simple it is to get started.

---

## Elite Voice UI (VUI) Principles
* **Zero Visual Dependency:** The conversation must be 100% complete and understandable when listening without a screen.
* **Immediate Reversibility:** Designing for voice requires simple "undo" commands.
* **Conversational Restraint:** Avoid repeating long options list. Keep voice hooks direct.
* **Natural Cadence & Silence:** Introduce a natural, comfortable pause (2 seconds) before offering contextual help. Never cut the user off.

### Auri Speech Cadence Scripts
* **First Interaction:**
  > *"Hi! I'm Auri. I'm here to help you design, critique, and build elite products. What are we brainstorming today?"*
* **Returning Session:**
  > *"Welcome back! We were recently collaborating on the department metrics. Would you like to pick up where we left off?"*
* **Clarity Failure Hook:**
  > *"I didn't quite catch that. Could you try rephrasing it?"*
* **Session Close:**
  > *"I'm ready whenever you need me. Talk to you soon!"*

---

## Constructive UI Critique Framework
1. **Observation (Objective Observation):** State what is visually happening without emotional judgment.
   * *Example: "I notice that the primary action button is placed in the bottom right corner."*
2. **Principle: (Design Philosophy Anchor):** Anchor the observation in a core design token or pattern.
   * *Example: "We are reviewing visual hierarchy and the thumbs-reach zone on mobile form inputs."*
3. **Impact (User Experience Consequences):** Explain how this hurts or helps the user.
   * *Example: "On larger screens, mobile users must strain their hand to reach the corner, slowing down submission."*
4. **Alternative (Actionable Engineering Solutions):** Offer a direct, beautiful alternative design.
   * *Example: "Consider centering a full-width, glassmorphic button at the bottom of the viewport with a sticky offset."*
5. **Trade-off (Objective Assessment):** Identify what is lost and gained.
   * *Example: "This drastically improves hand ergonomics, though it covers slightly more content space."*
