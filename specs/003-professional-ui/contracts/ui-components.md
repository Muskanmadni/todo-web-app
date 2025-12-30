# UI Component Contract: Professional Todo Application

## Component: Professional Button

### Visual Specifications
- **Background Color**: Primary color (#1e3a8a for primary, #e2e8f0 for secondary)
- **Text Color**: White for primary buttons, dark gray for secondary
- **Border Radius**: 0.375rem (6px)
- **Padding**: 0.5rem 1rem (8px 16px)
- **Font Weight**: 500 (Medium)
- **Hover Effect**: Darken background by 10%
- **Focus Ring**: 2px solid #3b82f6 with 2px offset

### Behavioral Specifications
- **States**: Default, Hover, Active, Focus, Disabled
- **Disabled Opacity**: 50%
- **Loading State**: Show spinner with reduced opacity
- **Size Variants**: Small (0.375rem 0.75rem), Medium (0.5rem 1rem), Large (0.75rem 1.5rem)

## Component: Professional Input Field

### Visual Specifications
- **Border**: 1px solid #d1d5db (light gray)
- **Border Radius**: 0.375rem (6px)
- **Padding**: 0.5rem 0.75rem
- **Background**: White
- **Focus Border**: 2px solid #3b82f6
- **Focus Shadow**: 0 0 0 3px rgba(59, 130, 246, 0.1)

### Behavioral Specifications
- **Placeholder Text**: #6b7280 (medium gray) with italic font
- **Error State**: Border color #ef4444 (red)
- **Success State**: Border color #10b981 (green)

## Component: Professional Card

### Visual Specifications
- **Background**: #f9fafb (off-white)
- **Border**: 1px solid #e5e7eb (light gray)
- **Border Radius**: 0.5rem (8px)
- **Shadow**: 0 1px 3px 0 rgba(0, 0, 0, 0.1)
- **Padding**: 1rem (16px)
- **Margin**: 1rem (16px) between cards

## Component: Professional Navigation

### Visual Specifications
- **Background**: White
- **Height**: 4rem (64px)
- **Padding**: 0 1rem (0 16px)
- **Border Bottom**: 1px solid #e5e7eb
- **Link Color**: #1f2937 (dark gray)
- **Active Link**: #3b82f6 (blue) with bottom border

### Behavioral Specifications
- **Hover Effect**: Link color changes to #3b82f6
- **Mobile Menu**: Hamburger icon that expands to full menu
- **Active State**: Current page highlighted

## Component: Professional Form

### Visual Specifications
- **Field Spacing**: 1rem (16px) between fields
- **Label Position**: Above input fields
- **Label Style**: Font weight 500, dark gray text
- **Required Indicator**: Red asterisk (*)
- **Error Message**: #ef4444 (red) below the field

## Responsive Behavior

### Mobile (0px to 767px)
- **Navigation**: Collapsed to hamburger menu
- **Form Fields**: Full width
- **Buttons**: Full width on small screens
- **Card Padding**: Reduced to 0.5rem

### Tablet (768px to 1023px)
- **Navigation**: Expanded but compact
- **Layout**: Two-column where appropriate
- **Card Padding**: 0.75rem

### Desktop (1024px and above)
- **Navigation**: Fully expanded
- **Layout**: Multi-column as appropriate
- **Card Padding**: Full 1rem