# Visual Verification Checklist for TASK-8

This document provides manual visual verification steps to confirm that the implemented pages match the wireframe designs exactly.

## Prerequisites
- Backend running at http://localhost:9000
- Frontend running at http://localhost:5173
- Login with: analyst@example.com / password123

## CaseIntakePage Verification (`/cases/new`)

### Structure Matching wireframe_guided_order_intake.html
- [ ] Page title "Guided Order Intake" in 28px bold font
- [ ] Subtitle "Create a new customer credit review case" in 14px gray text
- [ ] Four main form sections with exact titles:
  - [ ] "Customer and Order Information"
  - [ ] "Commercial Terms"
  - [ ] "Exception Indicators"
  - [ ] "Supporting Notes"

### Color Matching
- [ ] Primary button color: #0066CC (Submit for Review)
- [ ] Exception indicator background: #FEF3C7 with #F59E0B border
- [ ] Exception icon: #F59E0B background with white "!" text
- [ ] Validation check color: #10B981 with "✓ Customer verified"

### Layout
- [ ] Form rows use 2-column grid layout
- [ ] All input heights: 48px
- [ ] Border radius: 6px for inputs, 8px for buttons, 12px for cards
- [ ] Card background: #F9FAFB with #E5E7EB border
- [ ] Section titles have 2px solid #E5E7EB bottom border

### Fields
- [ ] Customer ID field has red asterisk (required)
- [ ] Order Reference field has red asterisk (required)
- [ ] Requested Outcome dropdown has release/hold/amend/decline options
- [ ] Requested Discount shows help text "Enter discount percentage if applicable"
- [ ] Exception indicator banner shows with warning icon
- [ ] File upload area shows "Drop files here or click to upload"

### Actions
- [ ] "Save Draft" button: white background with gray border
- [ ] "Submit for Review" button: #0066CC background with white text
- [ ] Both buttons: 48px height with 8px border-radius

## CaseDetailPage Verification (`/cases/:caseId`)

### Structure Matching wireframe_analyst_case_view.html
- [ ] Case header with CASE-XXXX format in 24px bold
- [ ] Customer and order reference in subtitle
- [ ] Status badge with colored dot indicator
- [ ] Four meta items: Assignee, Created, Last Updated, Exposure
- [ ] 2-column content grid (main content 2fr, sidebar 1fr)

### Main Content Area
- [ ] "Intake Summary" card with 5 info rows
- [ ] "Credit Assessment Workspace" card with:
  - [ ] Risk Level dropdown
  - [ ] Findings textarea
  - [ ] 4-option recommendation grid (Release/Hold/Amend/Decline)
  - [ ] Rationale textarea

### Recommendation Grid
- [ ] 4 equal-width cards in grid
- [ ] Selected option: 2px solid #0066CC border with #EFF6FF background
- [ ] Unselected: 2px solid #E5E7EB border with white background
- [ ] Each card shows option name and description

### Sidebar
- [ ] "Approval Status" card with yellow banner if exception
- [ ] "Fulfilment Tracking" card with status and target date
- [ ] "Audit Timeline" card with numbered circular icons (#DBEAFE background)
- [ ] Timeline items show action and metadata in gray text

### Colors
- [ ] In Review status: #DBEAFE background, #1E40AF text
- [ ] Pending Approval status: #FEF3C7 background, #92400E text
- [ ] Approved status: #D1FAE5 background, #065F46 text
- [ ] Exception banner: #FEF3C7 background, #F59E0B border

## DashboardPage Verification (`/`)

### Structure Matching wireframe_dashboard.html
- [ ] Page title "Operations Dashboard" in 28px bold
- [ ] Subtitle "Real-time view of credit review operations and performance"
- [ ] Filter bar with date range dropdown and export buttons
- [ ] 4-column metrics grid at top
- [ ] 2-column dashboard widgets grid

### Metric Cards (4 across)
- [ ] Total Cases: default color (gray)
- [ ] Pending Approval: #F59E0B (warning orange)
- [ ] Overdue Cases: #EF4444 (danger red)
- [ ] Avg Approval Time: #10B981 (success green)
- [ ] All cards: #F9FAFB background, #E5E7EB border, 12px border-radius
- [ ] Metric values: 32px bold font
- [ ] Trend text: 13px gray font

### Dashboard Widgets (2 columns, 3 rows)
- [ ] Case Status Distribution: StatusCard components with progress bars
- [ ] Exception Volume Trend: chart placeholder with gray border
- [ ] Approval Latency: chart placeholder with metadata below
- [ ] Operational Alerts: colored left border (red/orange/blue)
- [ ] Queue Ageing: 3 items with colored values (green/orange/red)
- [ ] Outcome Distribution: chart with legend showing 4 outcomes

### Alert Severity Colors
- [ ] High severity: #EF4444 left border, #FEF2F2 background
- [ ] Medium severity: #F59E0B left border, #FFFBEB background
- [ ] Low severity: #3B82F6 left border, #EFF6FF background

### Executive Summary
- [ ] 3-column grid at bottom
- [ ] "CONTROL HEALTH" shows 98.5% in #10B981 (green)
- [ ] "ESCALATION RATE" shows 7.1% in default gray
- [ ] "RELEASE READINESS" shows "Ready" in #10B981 (green)
- [ ] Section labels: 12px bold uppercase gray
- [ ] Values: 20px bold
- [ ] Descriptions: 13px gray

### Export Buttons
- [ ] "Export CSV" button: white background with gray border
- [ ] "Export PDF" button: #0066CC background with white text
- [ ] Both buttons: 44px height

## Accessibility (WCAG 2.1 AA)
- [ ] All buttons keyboard navigable (Tab key)
- [ ] Forms navigable with Tab/Shift+Tab
- [ ] Contrast ratios meet AA standards:
  - [ ] #0066CC on white: 4.59:1 (passes AA for large text)
  - [ ] #111827 on white: 14.69:1 (passes AAA)
  - [ ] #6B7280 on white: 4.59:1 (passes AA)

## Cross-Page Consistency
- [ ] All pages use same card style (#F9FAFB background, #E5E7EB border, 12px radius)
- [ ] All pages use same section title style (18px bold, 2px bottom border)
- [ ] All pages use same button styles (48px/44px height, 8px radius)
- [ ] All pages use same color palette:
  - Primary: #0066CC
  - Success: #10B981
  - Warning: #F59E0B
  - Danger: #EF4444
  - Gray-900: #111827
  - Gray-500: #6B7280
  - Gray-200: #E5E7EB
  - Gray-50: #F9FAFB
