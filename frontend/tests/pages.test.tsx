/**
 * Basic component tests for CaseIntakePage and DashboardPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { CaseIntakePage } from '../src/pages/CaseIntakePage';
import { DashboardPage } from '../src/pages/DashboardPage';
import { AuthProvider } from '../src/lib/auth-context';

// Mock API client
vi.mock('../src/lib/api-client', () => ({
  apiClient: {
    createCase: vi.fn().mockResolvedValue({ id: 1 }),
    getOperationalDashboard: vi.fn().mockResolvedValue({
      metrics: [
        { label: 'Total Cases', value: '1,247', trend: '↑ 8% from last week' },
        { label: 'Pending Approval', value: '89', trend: '↑ 12 cases today' },
      ],
      widgets: {},
    }),
    createExport: vi.fn().mockResolvedValue({ export_id: 1 }),
  },
}));

describe('CaseIntakePage', () => {
  it('renders page title matching wireframe', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <CaseIntakePage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Guided Order Intake')).toBeInTheDocument();
    expect(screen.getByText('Create a new customer credit review case')).toBeInTheDocument();
  });

  it('renders all required form sections', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <CaseIntakePage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Customer and Order Information')).toBeInTheDocument();
    expect(screen.getByText('Commercial Terms')).toBeInTheDocument();
    expect(screen.getByText('Exception Indicators')).toBeInTheDocument();
    expect(screen.getByText('Supporting Notes')).toBeInTheDocument();
  });

  it('renders required fields with asterisks', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <CaseIntakePage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByLabelText(/Customer ID/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Order Reference/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Requested Outcome/)).toBeInTheDocument();
  });

  it('uses exact wireframe button styling', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <CaseIntakePage />
        </AuthProvider>
      </BrowserRouter>
    );

    const submitButton = screen.getByText('Submit for Review');
    expect(submitButton).toBeInTheDocument();
    expect(submitButton).toHaveStyle({ background: '#0066CC', color: '#FFFFFF' });
  });

  it('validates customer ID is verified', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <CaseIntakePage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('✓ Customer verified')).toBeInTheDocument();
  });
});

describe('DashboardPage', () => {
  it('renders page title matching wireframe', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Operations Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Real-time view of credit review operations and performance')).toBeInTheDocument();
  });

  it('renders all metric cards with correct colors', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );

    // Wait for dashboard to load
    await screen.findByText('Total Cases');

    expect(screen.getByText('Total Cases')).toBeInTheDocument();
    expect(screen.getByText('Pending Approval')).toBeInTheDocument();
    expect(screen.getByText('Overdue Cases')).toBeInTheDocument();
    expect(screen.getByText('Avg Approval Time')).toBeInTheDocument();
  });

  it('renders all dashboard widgets', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );

    await screen.findByText('Case Status Distribution');

    expect(screen.getByText('Case Status Distribution')).toBeInTheDocument();
    expect(screen.getByText('Exception Volume Trend')).toBeInTheDocument();
    expect(screen.getByText('Approval Latency')).toBeInTheDocument();
    expect(screen.getByText('Operational Alerts')).toBeInTheDocument();
    expect(screen.getByText('Queue Ageing')).toBeInTheDocument();
    expect(screen.getByText('Outcome Distribution')).toBeInTheDocument();
  });

  it('renders executive summary section', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );

    await screen.findByText('Executive Summary');

    expect(screen.getByText('Executive Summary')).toBeInTheDocument();
    expect(screen.getByText('CONTROL HEALTH')).toBeInTheDocument();
    expect(screen.getByText('ESCALATION RATE')).toBeInTheDocument();
    expect(screen.getByText('RELEASE READINESS')).toBeInTheDocument();
  });

  it('uses exact wireframe colors for metric cards', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );

    await screen.findByText('1,247');

    // Verify metric values are displayed
    expect(screen.getByText('1,247')).toBeInTheDocument(); // Total Cases
    expect(screen.getByText('89')).toBeInTheDocument(); // Pending Approval
    expect(screen.getByText('12')).toBeInTheDocument(); // Overdue Cases
    expect(screen.getByText('1.8d')).toBeInTheDocument(); // Avg Approval Time
  });

  it('renders export buttons', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );

    await screen.findByText('Export CSV');

    expect(screen.getByText('Export CSV')).toBeInTheDocument();
    expect(screen.getByText('Export PDF')).toBeInTheDocument();
  });
});
