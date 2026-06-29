---
name: Vibrant Cravings
colors:
  surface: '#fff8f7'
  surface-dim: '#f0d3d2'
  surface-bright: '#fff8f7'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff0ef'
  surface-container: '#ffe9e8'
  surface-container-high: '#ffe1e0'
  surface-container-highest: '#f9dcda'
  on-surface: '#271717'
  on-surface-variant: '#5b403f'
  inverse-surface: '#3e2c2b'
  inverse-on-surface: '#ffedeb'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#5d5f5f'
  on-secondary: '#ffffff'
  secondary-container: '#dfe0e0'
  on-secondary-container: '#616363'
  tertiary: '#5d5c5b'
  on-tertiary: '#ffffff'
  tertiary-container: '#757474'
  on-tertiary-container: '#fffcfb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1b1b1b'
  on-tertiary-fixed-variant: '#474746'
  background: '#fff8f7'
  on-background: '#271717'
  surface-variant: '#f9dcda'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-bold:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 16px
  gutter: 12px
---

## Brand & Style
The design system is engineered to evoke an immediate appetite and a sense of high-energy exploration. It targets urban food enthusiasts who value speed, variety, and visual delight. The aesthetic is a fusion of **Modern Corporate** efficiency and **Tactile** warmth, ensuring that while the interface remains highly functional and reliable, the food photography remains the hero. The emotional response should be one of "craving"—using vibrant pops of color against expansive, clean backgrounds to make the imagery "leap" off the screen.

## Colors
This design system utilizes a high-contrast palette to drive user action. The **Primary Red** is the energetic heartbeat of the UI, reserved for critical calls-to-action, price highlights, and brand markers. The **Secondary Light Grey** provides a soft canvas that prevents eye strain, while **Pure White** is used strictly for elevated cards and content containers to create clear separation. Success Green and Warning Amber are utilized for functional metadata like ratings, status indicators, and delivery time alerts.

## Typography
The typographic hierarchy prioritizes legibility under "on-the-go" conditions. **Plus Jakarta Sans** is selected for headlines to provide a friendly, rounded contemporary feel that complements the food imagery. **Inter** is used for all functional body and metadata text due to its exceptional clarity at small sizes. Restaurant names should always utilize `headline-lg`, while pricing and ratings use `label-bold` to ensure they are scannable at a glance.

## Layout & Spacing
The design system follows a **Fluid Grid** model optimized for mobile-first consumption. It uses a 4-column structure for mobile devices with a 16px outer margin. Spacing follows a strict 4px base unit. Vertical rhythm is maintained by using `md` (16px) spacing between related elements within a card and `lg` (24px) spacing between distinct sections or categories. Horizontal scrolling carousels are encouraged for "Cuisines" or "Top Rated" sections to maximize vertical screen real estate.

## Elevation & Depth
Depth is created through a combination of **Tonal Layers** and **Ambient Shadows**. The base background is the `secondary_color` (#F8F8F8). Primary content containers (like restaurant cards) are set in White (#FFFFFF) with a soft, diffused shadow: `0px 4px 12px rgba(0, 0, 0, 0.06)`. When an item is pressed or active, the shadow should slightly deepen to `0px 8px 20px rgba(0, 0, 0, 0.1)` to simulate physical movement toward the user.

## Shapes
The shape language is consistently "Soft-Rounded." Standard cards and primary buttons utilize a **12px corner radius**. Large promotional banners or featured containers use an increased **16px radius** (`rounded-lg`). Small elements like input fields, search bars, and tags utilize an **8px radius**. This creates a welcoming, approachable UI that avoids the clinical feel of sharp corners.

## Components
- **Buttons:** Primary buttons are Solid Red (#E23744) with White text, using 12px rounding. Secondary buttons are outline-only or Light Grey with dark text for lower hierarchy actions.
- **Restaurant Cards:** Feature a full-bleed top image (aspect ratio 16:9), followed by a 12px padded content area. Include a floating "Rating Badge" in the top right corner of the image using `success_color`.
- **Chips:** Used for cuisine types and filters. They should have an 8px radius, a 1px Light Grey border, and use `label-sm` typography. When selected, the border and text switch to the Primary Red.
- **Search Bar:** A prominent 12px rounded field with a soft shadow, containing a subtle "Search for dishes or restaurants" placeholder and a magnifying glass icon.
- **Lists:** Order history and menu items should use a clean horizontal layout with 8px spacing between the item name and the "Add" button, separated by a thin 1px #EEEEEE divider.
- **Input Fields:** Use an 8px radius with a 1px border. On focus, the border should transition to Primary Red.