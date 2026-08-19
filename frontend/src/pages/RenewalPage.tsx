/**
 * RenewalPage - Renewal Review
 * Matches wireframe_renewal_review.html structure and styling exactly.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';

export function RenewalPage() {
  const [riskCategory, setRiskCategory] = useState('high');
  const [renewalNotes, setRenewalNotes] = useState('Account shows high renewal risk due to two unresolved complaints and pending refund. Customer has expressed dissatisfaction with fulfilment delays and service recovery response time. Recommend executive review before renewal discussions. Consider enhanced service terms or additional concessions to retain account. Total refund exposure of $8,200 represents 32% of annual contract value, indicating significant service delivery issues that must be addressed before renewal commitment.');
  const [recommendedActions, setRecommendedActions] = useState('1. Escalate to VP Sales for executive review\n2. Schedule customer success meeting to address open complaints\n3. Expedite pending refund approval and processing\n4. Conduct root cause analysis of fulfilment delays\n5. Prepare service recovery plan with enhanced SLA commitments\n6. Consider retention pricing or service credits for renewal negotiation');

  const handleSaveAssessment = async () => {
    try {
      await apiClient.submitOperation(123, {
        operationType: 'renewal',
        account_id: 'ACCT-2024-00456',
        risk_category: riskCategory,
        renewal_notes: renewalNotes,
        recommended_actions: recommendedActions,
      });
      alert('Renewal assessment saved successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save assessment');
    }
  };

  const linkedCases = [
    { caseId: 'CASE-2024-00123', outcome: 'Release', status: 'unresolved', statusLabel: 'Complaint Open' },
    { caseId: 'CASE-2024-00118', outcome: 'Release', status: 'unresolved', statusLabel: 'Refund Pending' },
    { caseId: 'CASE-2024-00098', outcome: 'Amend', status: 'resolved', statusLabel: 'Resolved' },
  ];

  const getIssueBadgeStyle = (status: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: '600',
    };
    if (status === 'unresolved') {
      return { ...baseStyle, background: '#FEE2E2', color: '#991B1B' };
    } else {
      return { ...baseStyle, background: '#D1FAE5', color: '#065F46' };
    }
  };

  return (
    <div className="main-content" style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Renewal Review
        </h1>
        <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
          Assess renewal risk for accounts with credit review history
        </p>
      </div>

      <div className="risk-banner" style={{ background: '#FEE2E2', border: '1px solid #EF4444', borderRadius: '12px', padding: '20px 24px', marginBottom: '24px', display: 'flex', alignItems: 'start', gap: '16px' }}>
        <div className="risk-icon" style={{ width: '24px', height: '24px', background: '#EF4444', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF', fontWeight: '700', fontSize: '14px' }}>
          !
        </div>
        <div className="risk-content" style={{ flex: 1 }}>
          <div className="risk-title" style={{ fontSize: '16px', fontWeight: '700', color: '#991B1B', marginBottom: '4px' }}>
            High Renewal Risk Detected
          </div>
          <div className="risk-text" style={{ fontSize: '14px', color: '#7F1D1D' }}>
            This account has unresolved issues that may impact renewal. Review linked cases, complaints, and refunds before proceeding with renewal discussions.
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Renewal Risk Summary
        </h2>
        <div className="summary-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Account ID
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              ACCT-2024-00456
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Renewal Window
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              Sep 15, 2024
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Risk Category
            </div>
            <div className="summary-value risk-high" style={{ fontSize: '20px', fontWeight: '600', color: '#EF4444' }}>
              High Risk
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Linked Cases
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              3 Cases
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Unresolved Issues
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#EF4444' }}>
              2 Open
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Total Refunds
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              $8,200.00
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Linked Case History
        </h2>
        <div className="history-section" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px' }}>
          {linkedCases.map((item, index) => (
            <div key={item.caseId} className="history-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: index < linkedCases.length - 1 ? '1px solid #E5E7EB' : 'none' }}>
              <div>
                <div className="history-label" style={{ fontSize: '14px', color: '#6B7280' }}>Case Number</div>
                <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                  <Link to={`/cases/${item.caseId.split('-')[2]}`} style={{ color: '#0066CC', textDecoration: 'none' }}>
                    {item.caseId}
                  </Link>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="history-label" style={{ fontSize: '14px', color: '#6B7280' }}>Outcome</div>
                <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                  {item.outcome}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="history-label" style={{ fontSize: '14px', color: '#6B7280' }}>Status</div>
                <div className="issue-badge" style={getIssueBadgeStyle(item.status)}>
                  {item.statusLabel}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Complaint and Refund Summary
        </h2>
        <div className="history-section" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px' }}>
          <div className="history-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
            <div className="history-label" style={{ fontSize: '14px', color: '#111827' }}>Open Complaints</div>
            <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#EF4444' }}>2 Active</div>
          </div>
          <div className="history-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
            <div className="history-label" style={{ fontSize: '14px', color: '#111827' }}>Resolved Complaints</div>
            <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>1 Closed</div>
          </div>
          <div className="history-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
            <div className="history-label" style={{ fontSize: '14px', color: '#111827' }}>Total Refunds Issued</div>
            <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>$8,200.00 USD</div>
          </div>
          <div className="history-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
            <div className="history-label" style={{ fontSize: '14px', color: '#111827' }}>Pending Refunds</div>
            <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#F59E0B' }}>$2,500.00 USD</div>
          </div>
          <div className="history-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
            <div className="history-label" style={{ fontSize: '14px', color: '#111827' }}>Last Complaint Date</div>
            <div className="history-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>Aug 18, 2024</div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Renewal Risk Assessment
        </h2>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            Risk Category
          </label>
          <select className="form-input" value={riskCategory} onChange={(e) => setRiskCategory(e.target.value)} style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
            <option value="">Select risk category...</option>
            <option value="low">Low Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="high">High Risk</option>
            <option value="critical">Critical Risk</option>
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            Renewal Notes
          </label>
          <textarea className="form-input" value={renewalNotes} onChange={(e) => setRenewalNotes(e.target.value)} placeholder="Add renewal assessment notes..." style={{ width: '100%', minHeight: '120px', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF', resize: 'vertical' }} />
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            Recommended Actions
          </label>
          <textarea className="form-input" value={recommendedActions} onChange={(e) => setRecommendedActions(e.target.value)} placeholder="List recommended actions..." style={{ width: '100%', minHeight: '120px', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF', resize: 'vertical' }} />
        </div>

        <div className="risk-actions" style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
          <button className="btn btn-danger" style={{ height: '48px', padding: '0 24px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#EF4444', color: '#FFFFFF' }}>
            Flag for Executive Review
          </button>
          <button className="btn btn-secondary" style={{ height: '48px', padding: '0 24px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}>
            Schedule Customer Meeting
          </button>
          <button onClick={handleSaveAssessment} className="btn btn-primary" style={{ height: '48px', padding: '0 24px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}>
            Save Assessment
          </button>
        </div>
      </div>
    </div>
  );
}
