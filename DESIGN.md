---
name: Luminous Minimalist
colors:
  surface: '#faf9f7'
  surface-dim: '#dadad8'
  surface-bright: '#faf9f7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeec'
  surface-container-high: '#e9e8e6'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1b'
  on-surface-variant: '#464555'
  inverse-surface: '#2f3130'
  inverse-on-surface: '#f1f1ef'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#904d00'
  on-secondary: '#ffffff'
  secondary-container: '#fe932c'
  on-secondary-container: '#663500'
  tertiary: '#7e3000'
  on-tertiary: '#ffffff'
  tertiary-container: '#a44100'
  on-tertiary-container: '#ffd2be'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#ffdcc3'
  secondary-fixed-dim: '#ffb77d'
  on-secondary-fixed: '#2f1500'
  on-secondary-fixed-variant: '#6e3900'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7b2f00'
  background: '#faf9f7'
  on-background: '#1a1c1b'
  surface-variant: '#e3e2e0'
typography:
  h1:
    fontFamily: Manrope
    fontSize: 2.5rem
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h2:
    fontFamily: Manrope
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Manrope
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: '1.7'
  body-md:
    fontFamily: Manrope
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: '1.6'
  code:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-chat: 768px
  container-artifact: minmax(400px, 1fr)
  gutter: 2rem
  margin-page: 1.5rem
  stack-sm: 0.5rem
  stack-md: 1.5rem
  stack-lg: 3rem
---

## Brand & Style

This design system is anchored in the concept of "Digital Zen"—a philosophy that prioritizes cognitive ease, intellectual clarity, and a warm, humanistic approach to artificial intelligence. It moves away from the cold, clinical blues often associated with tech, opting instead for a palette of parchment whites and stone grays that feel tactile and grounded.

The style is a refined blend of **Minimalism** and **Tonal Layering**. It utilizes expansive whitespace not just as a design choice, but as a functional tool to reduce user anxiety and focus attention on the conversation. The interaction model is quiet and unobtrusive, aiming to evoke a sense of working within a high-end stationery suite or a modern architectural studio.

## Colors

The color strategy centers on a "warm neutral" foundation. The primary background is not a pure digital white, but a soft parchment (#F9F8F6) to reduce eye strain during long reading sessions. 

- **Primary:** A deep Indigo (#4F46E5) used sparingly for primary actions and focused states.
- **Accents:** Hints of soft Amber are used for cautionary or secondary highlights.
- **Neutrals:** A spectrum of warm grays with subtle brown undertones ensures the UI feels "organic" rather than mechanical.
- **Indigo Infusion:** Use very low-opacity indigo tints (2-5%) for hover states on neutral backgrounds to maintain a cohesive brand thread.

## Typography

This design system uses **Manrope** as the primary typeface for its unique balance between geometric precision and organic warmth. Its open counters and modern curves ensure high readability in dense chat logs and technical documents.

- **Body Text:** Always prioritize line height (1.6x+) to facilitate deep reading.
- **Headlines:** Set with slight negative letter-spacing to feel tight and authoritative.
- **Code & UI Labels:** Switch to **Inter** for its utilitarian clarity in functional areas, such as the artifact panel and system metadata.

## Layout & Spacing

The layout follows a **Hybrid Fixed-Fluid Model**. 
- **The Chat Container:** Centrally aligned with a maximum width of 768px to ensure optimal line length for reading. It uses generous vertical padding between message blocks.
- **The Artifact Panel:** Slides in from the right, taking up the remaining viewport space with a minimum width of 400px. It features its own internal scrolling and independent padding.
- **The Rhythm:** Based on a 4px baseline, but defaults to larger increments (16px, 24px, 48px) to reinforce the sense of "room to breathe."

## Elevation & Depth

Depth is communicated through **Tonal Layering** rather than heavy shadows. 
- **Level 0 (Base):** The parchment-toned background.
- **Level 1 (Cards/Messages):** Pure white surfaces with a very soft, high-diffusion shadow (0px 4px 20px rgba(0,0,0,0.03)) and a subtle 1px border (#E5E2DE).
- **Level 2 (Modals/Popovers):** Slightly more pronounced shadows with a subtle indigo tint in the blur to suggest active focus.
- **The Artifact Panel:** Treated as a "sheet" that sits on the same plane as the chat but is separated by a vertical hairline border and a slight shift in background value.

## Shapes

The shape language is approachable and soft. 
- **Standard Elements:** Use a 0.5rem (8px) radius for buttons, input fields, and small containers.
- **Large Containers:** Chat bubbles and the main Artifact panel use 1rem (16px) or 1.5rem (24px) for a "pouch-like" feel that avoids sharp institutional corners.
- **Interactive States:** Soften even further on hover to provide a subtle "squishy" feedback, indicating responsiveness.

## Components

- **Buttons:** Primary buttons use the Indigo background with white text. Secondary buttons are "ghost" style with a 1px neutral border that turns Indigo on hover.
- **Chat Bubbles:** User messages are subtly differentiated with a slightly darker neutral background, while AI responses sit on the clean white surface. No harsh speech-bubble "tails" are used; rely on alignment and spacing.
- **Input Field:** The central chat input is a large, expansive text area with a 24px corner radius, appearing as a soft "tray" at the bottom of the screen.
- **Artifacts:** Code blocks use a specialized dark theme (monochrome with indigo highlights) to create a clear visual distinction from the warm-toned chat interface.
- **Chips/Tags:** Used for quick actions or category labels, featuring a 0.25rem radius and low-contrast background colors.