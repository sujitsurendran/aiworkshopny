/**
 * ApprovalQueuePage - List view of pending approvals
 * Links to ApprovalDecisionPage for detail view
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { formatDateTime } from '../lib/utils';

interface ApprovalItem {
  id: number;
  case_id: number;
  status: string;
  created_at: string;
}

export function ApprovalQueuePage() {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getApprovals({ status: 'pending' });
      const items = Array.isArray(data) ? data : (data as any)?.items || [];
      setApprovals(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading approvals...</div>;
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
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Approval Queue
        </h1>
        <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
          Review and act on pending approval requests assigned to you
        </p>
      </div>

      <div className="metrics-bar" style={{ display: 'flex', gap: '24px', marginBottom: '32px' }}>
        <div className="metric-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px 20px', minWidth: '140px' }}>
          <div className="metric-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
            Total
          </div>
          <div className="metric-value" style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
            {approvals.length}
          </div>
        </div>
        <div className="metric-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px 20px', minWidth: '140px' }}>
          <div className="metric-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
            Pending
          </div>
          <div className="metric-value" style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
            {approvals.filter(a => a.status === 'pending').length}
          </div>
        </div>
      </div>

      <div className="table-container" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: '#FFFFFF', borderBottom: '2px solid #E5E7EB' }}>
            <tr>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Case Number
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Status
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Submitted
              </th>
              <th style={{ padding: '16px 20px', textAlign: 'left', fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {approvals.map((approval) => (
              <tr key={approval.id} style={{ borderBottom: '1px solid #E5E7EB' }}>
                <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                  <Link 
                    to={`/approvals/${approval.case_id}`} 
                    style={{ color: '#0066CC', fontWeight: '600', textDecoration: 'none' }}
                  >
                    CASE-{String(approval.case_id).padStart(4, '0')}
                  </Link>
                </td>
                <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                  <span style={{ 
                    display: 'inline-block', 
                    padding: '4px 12px', 
                    borderRadius: '12px', 
                    fontSize: '12px', 
                    fontWeight: '600',
                    background: '#FEF3C7',
                    color: '#92400E'
                  }}>
                    {approval.status}
                  </span>
                </td>
                <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                  {formatDateTime(approval.created_at)}
                </td>
                <td style={{ padding: '16px 20px', fontSize: '14px', color: '#111827' }}>
                  <Link 
                    to={`/approvals/${approval.case_id}`}
                    style={{ 
                      padding: '6px 12px', 
                      border: '1px solid #E5E7EB', 
                      borderRadius: '6px', 
                      fontSize: '12px', 
                      fontWeight: '600', 
                      background: '#FFFFFF', 
                      color: '#111827',
                      textDecoration: 'none',
                      display: 'inline-block'
                    }}
                  >
                    Review
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
