# Data Model: UI Theme for Professional UI

## Theme Structure

### Color Palette
- **Primary**: Navy Blue (#1e3a8a) - for primary actions and headers
- **Secondary**: Light Gray (#e2e8f0) - for backgrounds and subtle elements
- **Accent**: Professional Blue (#3b82f6) - for interactive elements and highlights
- **Text**: Dark Gray (#1f2937) - for primary text
- **Text Secondary**: Medium Gray (#6b7280) - for secondary text
- **Success**: Green (#10b981) - for positive feedback
- **Error**: Red (#ef4444) - for errors and destructive actions
- **Warning**: Amber (#f59e0b) - for warnings and alerts
- **Background**: White (#ffffff) - for main background
- **Surface**: Off-white (#f9fafb) - for card backgrounds

### Typography
- **Primary Font**: System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto)
- **Font Sizes**:
  - H1: 2.5rem (40px)
  - H2: 2rem (32px)
  - H3: 1.75rem (28px)
  - H4: 1.5rem (24px)
  - Body: 1rem (16px)
  - Small: 0.875rem (14px)
  - Caption: 0.75rem (12px)
- **Font Weights**: Regular (400), Medium (500), Semibold (600), Bold (700)

### Spacing System
- **Base Unit**: 4px (0.25rem)
- **Scale**: 0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24
- **Applied to**: margins, padding, gaps, and positioning

### Component Styles
- **Buttons**: Rounded corners (0.375rem), consistent padding (0.5rem 1rem), proper hover/focus states
- **Forms**: Consistent input styling with proper spacing and validation states
- **Cards**: Subtle shadows, consistent padding, appropriate borders
- **Navigation**: Clear visual hierarchy, proper hover states, mobile responsiveness

### Responsive Breakpoints
- **Mobile**: 0px to 767px
- **Tablet**: 768px to 1023px
- **Desktop**: 1024px and above

### Accessibility Features
- **Focus Indicators**: Visible focus rings for keyboard navigation
- **Contrast Ratios**: All text meets WCAG 2.1 AA standards (4.5:1 for normal text, 3:1 for large text)
- **Semantic HTML**: Proper heading hierarchy, appropriate ARIA attributes
- **Keyboard Navigation**: All interactive elements accessible via keyboard