# Professional UI Styling Guidelines

## Overview
This document outlines the styling guidelines for the professional UI implemented in the todo application. These guidelines ensure consistency across all components and maintain the professional appearance of the application.

## Color Palette

### Primary Colors
- **Navy Blue**: #1e3a8a (used for primary actions and headers)
- **Professional Blue**: #3b82f6 (used for interactive elements and highlights)
- **Light Blue**: #eff6ff (used for subtle backgrounds)

### Secondary Colors
- **Light Gray**: #e2e8f0 (used for backgrounds and subtle elements)
- **Medium Gray**: #6b7280 (used for secondary text)
- **Dark Gray**: #1f2937 (used for primary text)

### Status Colors
- **Success Green**: #10b981 (for positive feedback)
- **Error Red**: #ef4444 (for errors and destructive actions)
- **Warning Amber**: #f59e0b (for warnings and alerts)

### Background Colors
- **White**: #ffffff (main background)
- **Off-white**: #f9fafb (card backgrounds)

## Typography

### Font Stack
- Primary font: System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto)

### Font Sizes
- H1: 2.5rem (40px)
- H2: 2rem (32px)
- H3: 1.75rem (28px)
- H4: 1.5rem (24px)
- Body: 1rem (16px)
- Small: 0.875rem (14px)
- Caption: 0.75rem (12px)

### Font Weights
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## Spacing System

### Base Unit
- Base unit: 4px (0.25rem)

### Scale
- 0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24 (in rem units)

### Applied to
- Margins, padding, gaps, and positioning

## Component Styles

### Buttons
- Border radius: 0.375rem (6px)
- Padding: 0.5rem 1rem (8px 16px)
- Font weight: 500 (Medium)
- Hover effect: Darken background by 10%
- Focus ring: 2px solid #3b82f6 with 2px offset

### Input Fields
- Border: 1px solid #d1d5db (light gray)
- Border radius: 0.375rem (6px)
- Padding: 0.5rem 0.75rem
- Background: White
- Focus border: 2px solid #3b82f6

### Cards
- Background: #f9fafb (off-white)
- Border: 1px solid #e5e7eb (light gray)
- Border radius: 0.5rem (8px)
- Shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1)
- Padding: 1rem (16px)
- Margin: 1rem (16px) between cards

### Navigation
- Background: White
- Height: 4rem (64px)
- Padding: 0 1rem (0 16px)
- Border bottom: 1px solid #e5e7eb
- Link color: #1f2937 (dark gray)
- Active link: #3b82f6 (blue) with bottom border

## Responsive Breakpoints

### Mobile (0px to 767px)
- Navigation: Collapsed to hamburger menu
- Form fields: Full width
- Buttons: Full width on small screens
- Card padding: Reduced to 0.5rem

### Tablet (768px to 1023px)
- Navigation: Expanded but compact
- Layout: Two-column where appropriate
- Card padding: 0.75rem

### Desktop (1024px and above)
- Navigation: Fully expanded
- Layout: Multi-column as appropriate
- Card padding: Full 1rem

## Accessibility Features

### Focus Indicators
- Visible focus rings for keyboard navigation
- 2px solid #3b82f6 with 2px offset

### Contrast Ratios
- All text meets WCAG 2.1 AA standards (4.5:1 for normal text, 3:1 for large text)

### Semantic HTML
- Proper heading hierarchy
- Appropriate ARIA attributes

### Keyboard Navigation
- All interactive elements accessible via keyboard

## Implementation Files

All styling is implemented in the following files:
- `app/styles/theme.css` - Professional color scheme
- `app/styles/components/button.css` - Button styles
- `app/styles/components/form.css` - Form styles
- `app/styles/components/card.css` - Card styles
- `app/styles/components/navigation.css` - Navigation styles
- `app/styles/components/todo-list.css` - Todo list styles
- `app/styles/components/todo-item.css` - Todo item styles
- `app/styles/components/todo-form.css` - Todo form styles
- `app/styles/utilities/spacing.css` - Spacing utilities
- `app/styles/utilities/accessibility.css` - Accessibility features
- `app/styles/responsive.css` - Responsive design
- `app/styles/professional-ui.css` - Main import file
- `app/globals.css` - Global styles and variables
- `tailwind.config.ts` - Tailwind configuration with professional color palette