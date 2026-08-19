/**
 * DashboardPage - Operations Dashboard
 * Matches wireframe_dashboard.html structure and styling exactly.
 */

import React, { useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';
import { MetricCard } from '../components/ui/MetricCard';
import { StatusCard } from '../components/ui/StatusCard';
import { AlertItem } from '../components/ui/AlertItem';

interface DashboardData {
  metrics: Array<{ label: string; value: string | number; trend: string }>;
  widgets: {
    case_status_distribution?: Array<{ status: string; count: number; percentage: number }>;
    operational_alerts?: Array<{ title: string; description: string; severity: string }>;
    queue_ageing?: Array<{ range: string; count: number; color: string }>;
  };
}

export function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState('week');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  useEffect(() => {
    loadDashboard();
  }, [dateRange]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getOperationalDashboard({ date_range: dateRange });
      
      // Transform API response to expected shape
      const transformedData: DashboardData = {
        metrics: Array.isArray(data) ? [] : (data as any).metrics || [],
        widgets: Array.isArray(data) ? {} : (data as any).widgets || {},
      };
      
      setDashboardData(transformedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      // Set fallback data for demo
      setDashboardData({
        metrics: [
          { label: 'Total Cases', value: '1,247', trend: '↑ 8% from last week' },
          { label: 'Pending Approval', value: '89', trend: '↑ 12 cases today' },
          { label: 'Overdue Cases', value: '12', trend: 'Requires attention' },
          { label: 'Avg Approval Time', value: '1.8d', trend: '↓ 0.3d improvement' },
        ],
        widgets: {
          case_status_distribution: [
            { status: 'New', count: 187, percentage: 15 },
            { status: 'In Review', count: 436, percentage: 35 },
            { status: 'Pending Approval', count: 89, percentage: 7 },
            { status: 'Approved', count: 535, percentage: 43 },
          ],
          operational_alerts: [
            { title: '12 Overdue Cases', description: 'Cases exceeding SLA threshold require immediate attention', severity: 'high' },
            { title: '7 Fulfilment Blockers', description: 'Active blockers preventing order progression', severity: 'medium' },
            { title: '23 Open Complaints', description: 'Customer complaints requiring resolution', severity: 'medium' },
            { title: '8 Renewal Risks', description: 'Accounts with renewal-impacting issues', severity: 'low' },
          ],
          queue_ageing: [
            { range: '0-2 Days', count: 156, color: '#10B981' },
            { range: '3-5 Days', count: 67, color: '#F59E0B' },
            { range: '6+ Days', count: 12, color: '#EF4444' },
          ],
        },
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      await apiClient.createExport({
        source: 'operational_dashboard',
        export_type: 'csv',
        filters: { date_range: dateRange },
      });
      alert('CSV export requested. Check exports page for download.');
    } catch (err) {
      alert('Export failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  const handleExportPDF = async () => {
    try {
      await apiClient.createExport({
        source: 'operational_dashboard',
        export_type: 'pdf',
        filters: { date_range: dateRange },
      });
      alert('PDF export requested. Check exports page for download.');
    } catch (err) {
      alert('Export failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  if (loading && !dashboardData) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading dashboard...</div>;
  }

  const metrics = dashboardData?.metrics || [];
  const widgets = dashboardData?.widgets || {};

  return (
    <div className="main-content" style={{ maxWidth: '1600px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '32px' }}>
        <div>
          <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
            Operations Dashboard
          </h1>
          <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
            Real-time view of credit review operations and performance
          </p>
        </div>
        <div className="filter-bar" style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            style={{ height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
          </select>
          <button
            onClick={handleExportCSV}
            style={{ height: '44px', padding: '0 20px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}
          >
            Export CSV
          </button>
          <button
            onClick={handleExportPDF}
            style={{ height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}
          >
            Export PDF
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '8px', padding: '16px', marginBottom: '24px', color: '#991B1B' }}>
          {error} (Showing fallback data)
        </div>
      )}

      <div className="metrics-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '32px' }}>
        {metrics.length > 0 ? (
          metrics.map((metric, index) => (
            <MetricCard
              key={index}
              label={metric.label}
              value={metric.value}
              trend={metric.trend}
              variant={
                metric.label === 'Avg Approval Time' ? 'success' :
                metric.label === 'Pending Approval' ? 'warning' :
                metric.label === 'Overdue Cases' ? 'danger' : 'default'
              }
            />
          ))
        ) : (
          <>
            <MetricCard label="Total Cases" value="1,247" trend="↑ 8% from last week" />
            <MetricCard label="Pending Approval" value="89" trend="↑ 12 cases today" variant="warning" />
            <MetricCard label="Overdue Cases" value="12" trend="Requires attention" variant="danger" />
            <MetricCard label="Avg Approval Time" value="1.8d" trend="↓ 0.3d improvement" variant="success" />
          </>
        )}
      </div>

      <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
        <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
          <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
            Case Status Distribution
          </h2>
          <div className="status-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {widgets.case_status_distribution && widgets.case_status_distribution.length > 0 ? (
              widgets.case_status_distribution.map((item, index) => (
                <StatusCard
                  key={index}
                  label={item.status}
                  value={item.count}
                  percentage={item.percentage}
                  barColor={item.status === 'Approved' ? '#10B981' : '#0066CC'}
                />
              ))
            ) : (
              <>
                <StatusCard label="New" value={187} percentage={15} />
                <StatusCard label="In Review" value={436} percentage={35} />
                <StatusCard label="Pending Approval" value={89} percentage={7} />
                <StatusCard label="Approved" value={535} percentage={43} barColor="#10B981" />
              </>
            )}
          </div>
        </div>

        <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
          <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
            Exception Volume Trend
          </h2>
          <div className="chart-visual" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', height: '240px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7280', fontSize: '14px' }}>
            Exception volume trend visualization
          </div>
          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#6B7280' }}>
            <span>Current: 34 exceptions</span>
            <span>Avg: 28 exceptions/week</span>
          </div>
        </div>

        <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
          <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
            Approval Latency
          </h2>
          <div className="chart-visual" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', height: '240px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7280', fontSize: '14px' }}>
            Approval turnaround time by authority level
          </div>
          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#6B7280' }}>
            <span>Manager: 1.5 days</span>
            <span>Executive: 3.2 days</span>
          </div>
        </div>

        <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
          <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
            Operational Alerts
          </h2>
          <div className="alert-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {widgets.operational_alerts && widgets.operational_alerts.length > 0 ? (
              widgets.operational_alerts.map((alert, index) => (
                <AlertItem
                  key={index}
                  title={alert.title}
                  description={alert.description}
                  severity={alert.severity as 'high' | 'medium' | 'low'}
                />
              ))
            ) : (
              <>
                <AlertItem title="12 Overdue Cases" description="Cases exceeding SLA threshold require immediate attention" severity="high" />
                <AlertItem title="7 Fulfilment Blockers" description="Active blockers preventing order progression" severity="medium" />
                <AlertItem title="23 Open Complaints" description="Customer complaints requiring resolution" severity="medium" />
                <AlertItem title="8 Renewal Risks" description="Accounts with renewal-impacting issues" severity="low" />
              </>
            )}
          </div>
        </div>

        <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
          <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
            Queue Ageing
          </h2>
          <div className="status-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {widgets.queue_ageing && widgets.queue_ageing.length > 0 ? (
              widgets.queue_ageing.map((item, index) => (
                <div key={index} className="status-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}>
                  <div className="status-label" style={{ fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                    {item.range}
                  </div>
                  <div className="status-value" style={{ fontSize: '18px', fontWeight: '700', color: item.color }}>
                    {item.count}
                  </div>
                </div>
              ))
            ) : (
              <>
                <div className="status-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}>
                  <div className="status-label" style={{ fontSize: '14px', color: '#111827', fontWeight: '500' }}>0-2 Days</div>
                  <div className="status-value" style={{ fontSize: '18px', fontWeight: '700', color: '#10B981' }}>156</div>
                </div>
                <div className="status-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}>
                  <div className="status-label" style={{ fontSize: '14px', color: '#111827', fontWeight: '500' }}>3-5 Days</div>
                  <div className="status-value" style={{ fontSize: '18px', fontWeight: '700', color: '#F59E0B' }}>67</div>
                </div>
                <div className="status-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px' }}>
                  <div className="status-label" style={{ fontSize: '14px', color: '#111827', fontWeight: '500' }}>6+ Days</div>
                  <div className="status-value" style={{ fontSize: '18px', fontWeight: '700', color: '#EF4444' }}>12</div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
          <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
            Outcome Distribution
          </h2>
          <div className="chart-visual" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', height: '240px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6B7280', fontSize: '14px' }}>
            Decision outcome distribution visualization
          </div>
          <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '13px' }}>
            <div><span style={{ color: '#10B981' }}>●</span> Release: 68%</div>
            <div><span style={{ color: '#F59E0B' }}>●</span> Hold: 18%</div>
            <div><span style={{ color: '#3B82F6' }}>●</span> Amend: 10%</div>
            <div><span style={{ color: '#EF4444' }}>●</span> Decline: 4%</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginTop: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Executive Summary
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', marginBottom: '8px' }}>CONTROL HEALTH</div>
            <div style={{ fontSize: '20px', fontWeight: '700', color: '#10B981', marginBottom: '4px' }}>98.5%</div>
            <div style={{ fontSize: '13px', color: '#6B7280' }}>Evidence completeness rate</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', marginBottom: '8px' }}>ESCALATION RATE</div>
            <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>7.1%</div>
            <div style={{ fontSize: '13px', color: '#6B7280' }}>Cases requiring executive review</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', marginBottom: '8px' }}>RELEASE READINESS</div>
            <div style={{ fontSize: '20px', fontWeight: '700', color: '#10B981', marginBottom: '4px' }}>Ready</div>
            <div style={{ fontSize: '13px', color: '#6B7280' }}>All core flows operational</div>
          </div>
        </div>
      </div>
    </div>
  );
}
