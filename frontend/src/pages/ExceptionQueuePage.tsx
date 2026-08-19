/**
 * ExceptionQueuePage - Exception Queue View
 * Matches wireframe_exception_queue.html structure and styling exactly.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { formatDateTime } from '../lib/utils';

interface CaseItem {
  id: number;
  customer_id: string;
  requested_outcome: string | null;
  exception_flag: boolean;
  current_status: string;
  assigned_to_id: number | null;
  created_at: string;
  updated_at: string;
}

export function ExceptionQueuePage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [exceptionTypeFilter, setExceptionTypeFilter] = useState('');
  const [assigneeFilter, setAssigneeFilter] = useState('me');
  const [ageFilter, setAgeFilter] = useState('');

  useEffect(() => {
    loadExceptionCases();
  }, []);

  const loadExceptionCases = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getCases({ 
        exception_flag: true,
        status: statusFilter === 'pending' ? 'PENDING_APPROVAL' : undefined
      });
      const items = Array.isArray(data) ? data : (data as any)?.items || [];
      setCases(items.filter((c: CaseItem) => c.exception_flag));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load exception cases');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyFilters = () => {
    loadExceptionCases();
  };

  const handleReset = () => {
    setStatusFilter('pending');
    setExceptionTypeFilter('');
    setAssigneeFilter('me');
    setAgeFilter('');
  };

  const calculateAge = (createdAt: string) => {
    const now = new Date();
    const created = new Date(createdAt);
    const diffMs = now.getTime() - created.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getAgeIndicatorStyle = (days: number): React.CSSProperties => {
    if (days >= 7) {
      return { fontWeight: '600', color: '#EF4444' };
    } else if (days >= 4) {
      return { fontWeight: '600', color: '#F59E0B' };
    } else {
      return { fontWeight: '600', color: '#111827' };
    }
  };

  const getExceptionBadgeStyle = (type: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: '600',
    };
    
    if (type.includes('discount')) {
      return { ...baseStyle, background: '#FEF3C7', color: '#92400E' };
    } else if (type.includes('credit')) {
      return { ...baseStyle, background: '#FEE2E2', color: '#991B1B' };
    } else {
      return { ...baseStyle, background: '#E0E7FF', color: '#3730A3' };
    }
  };

  const totalCases = cases.length;
  const pendingCases = cases.filter(c => c.current_status === 'PENDING_APPROVAL').length;
  const overdueCases = cases.filter(c => calculateAge(c.created_at) >= 7).length;

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading exception queue...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '40px' }}>
        <div style={{ background: '#FEE2E2', border: '1px solid #EF4444', borderRadius: '8px', padding: '16px', color: '#991B1B' }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="main-content" style={{ maxWidth: '1600px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '32px' }}>
        <div>
          <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
            Exception Queue
          </h1>
          <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
            Review and manage cases requiring special approval
          </p>
        </div>
        <div className="metrics-bar" style={{ display: 'flex', gap: '24px' }}>
          <div className="metric-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px 20px', minWidth: '140px' }}>
            <div className="metric-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
              Total
            </div>
            <div className="metric-value" style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
              {totalCases}
            </div>
          </div>
          <div className="metric-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px 20px', minWidth: '140px' }}>
            <div className="metric-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
              Pending
            </div>
            <div className="metric-value" style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
              {pendingCases}
            </div>
          </div>
          <div className="metric-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px 20px', minWidth: '140px' }}>
            <div className="metric-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
              Overdue
            </div>
            <div className="metric-value warning" style={{ fontSize: '24px', fontWeight: '700', color: '#F59E0B' }}>
              {overdueCases}
            </div>
          </div>
        </div>
      </div>

      <div className="filter-bar" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '20px 24px', marginBottom: '24px', display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'end' }}>
        <div className="filter-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '180px' }}>
          <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Status
          </label>
          <select 
            className="filter-input"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <div className="filter-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '180px' }}>
          <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Exception Type
          </label>
          <select 
            className="filter-input"
            value={exceptionTypeFilter}
            onChange={(e) => setExceptionTypeFilter(e.target.value)}
            style={{ height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}
          >
            <option value="">All Types</option>
            <option value="discount">Discount Exception</option>
            <option value="credit">Credit Policy Exception</option>
            <option value="terms">Payment Terms Exception</option>
          </select>
        </div>

        <div className="filter-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '180px' }}>
          <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Assignee
          </label>
          <select 
            className="filter-input"
            value={assigneeFilter}
            onChange={(e) => setAssigneeFilter(e.target.value)}
            style={{ height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}
          >
            <option value="">All Assignees</option>
            <option value="me">Assigned to Me</option>
            <option value="team">My Team</option>
          </select>
        </div>

        <div className="filter-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '180px' }}>
          <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Age
          </label>
          <select 
            className="filter-input"
            value={ageFilter}
            onChange={(e) => setAgeFilter(e.target.value)}
            style={{ height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}
          >
            <option value="">Any Age</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>

        <button 
          onClick={handleApplyFilters}
          className="btn btn-primary"
          style={{ height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF', marginTop: '22px' }}
        >
          Apply Filters
        </button>
        <button 
          onClick={handleReset}
          className="btn btn-secondary"
          style={{ height: '44px', padding: '0 20px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#FFFFFF', color: '#111827', marginTop: '22px' }}
        >
          Reset
        </button>
      </div>

      <div className="table-container" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: '#FFFFFF', borderBottom: '2px solid #E5E7EB' }}>
            <tr>
              <th className="sortable" style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', cursor: 'pointer', userSelect: 'none' }}>
                Case Number ↓
              </th>
              <th className="sortable" style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', cursor: 'pointer', userSelect: 'none' }}>
                Customer
              </th>
              <th className="sortable" style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', cursor: 'pointer', userSelect: 'none' }}>
                Requested Outcome
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Exception Type
              </th>
              <th className="sortable" style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', cursor: 'pointer', userSelect: 'none' }}>
                Age (Days)
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Assignee
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {cases.map((caseItem) => {
              const age = calculateAge(caseItem.created_at);
              return (
                <tr key={caseItem.id} style={{ borderBottom: '1px solid #E5E7EB' }}>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    <Link 
                      to={`/cases/${caseItem.id}`}
                      style={{ color: '#0066CC', fontWeight: '600', textDecoration: 'none' }}
                    >
                      CASE-{String(caseItem.id).padStart(4, '0')}
                    </Link>
                  </td>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    {caseItem.customer_id}
                  </td>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    {caseItem.requested_outcome || 'Release'}
                  </td>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    <span style={getExceptionBadgeStyle('discount')}>
                      Discount Exception
                    </span>
                  </td>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    <span style={getAgeIndicatorStyle(age)}>{age}</span>
                  </td>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    User {caseItem.assigned_to_id || 'Unassigned'}
                  </td>
                  <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                    <div className="action-menu" style={{ display: 'flex', gap: '8px' }}>
                      <Link
                        to={`/cases/${caseItem.id}`}
                        style={{ padding: '6px 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '12px', fontWeight: '600', background: '#FFFFFF', color: '#111827', textDecoration: 'none', display: 'inline-block' }}
                      >
                        Open
                      </Link>
                      <button
                        style={{ padding: '6px 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '12px', fontWeight: '600', background: '#FFFFFF', color: '#111827', cursor: 'pointer' }}
                      >
                        Reassign
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <div className="pagination" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 24px', background: '#FFFFFF' }}>
          <div className="pagination-info" style={{ fontSize: '14px', color: '#6B7280' }}>
            Showing 1-{cases.length} of {cases.length} cases
          </div>
          <div className="pagination-controls" style={{ display: 'flex', gap: '8px' }}>
            <button style={{ width: '36px', height: '36px', border: '1px solid #E5E7EB', borderRadius: '6px', background: '#FFFFFF', color: '#111827', fontWeight: '600', cursor: 'pointer' }}>
              ‹
            </button>
            <button style={{ width: '36px', height: '36px', border: '1px solid #0066CC', borderRadius: '6px', background: '#0066CC', color: '#FFFFFF', fontWeight: '600', cursor: 'pointer' }}>
              1
            </button>
            <button style={{ width: '36px', height: '36px', border: '1px solid #E5E7EB', borderRadius: '6px', background: '#FFFFFF', color: '#111827', fontWeight: '600', cursor: 'pointer' }}>
              ›
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
