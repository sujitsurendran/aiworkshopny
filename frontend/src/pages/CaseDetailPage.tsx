/**
 * CaseDetailPage - Analyst Case View
 * Matches wireframe_analyst_case_view.html structure and styling exactly.
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { formatDateTime, formatCurrency } from '../lib/utils';

interface CaseData {
  id: number;
  customer_id: string;
  order_reference: string;
  current_status: string;
  requested_outcome: string | null;
  requested_terms: string | null;
  exception_flag: boolean;
  risk_band: string | null;
  assigned_to_id: number | null;
  created_at: string;
  updated_at: string;
  priority: string;
}

export function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [caseData, setCaseData] = useState<CaseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Assessment form state
  const [riskLevel, setRiskLevel] = useState('medium');
  const [findings, setFindings] = useState('Customer has maintained consistent payment history over 18 months. Current account standing is good with no overdue balances. Requested discount aligns with strategic account retention objectives. Credit exposure of $25,000 is within acceptable range for this customer profile.');
  const [recommendation, setRecommendation] = useState('Release');
  const [rationale, setRationale] = useState('Recommend release with requested discount. Customer qualifies based on payment history and strategic value. Discount exception requires manager approval per delegation of authority policy. Evidence supports commercial justification for retention pricing.');

  useEffect(() => {
    if (caseId) {
      loadCase();
    }
  }, [caseId]);

  const loadCase = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getCase(Number(caseId));
      setCaseData(data as CaseData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitForApproval = async () => {
    if (!caseId) return;
    try {
      await apiClient.submitAssessment(Number(caseId), {
        recommendation,
        rationale,
        assessment_data: { risk_level: riskLevel, findings },
      });
      alert('Assessment submitted for approval');
      loadCase();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit assessment');
    }
  };

  const getStatusBadgeStyle = (status: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      padding: '8px 16px',
      borderRadius: '20px',
      fontSize: '13px',
      fontWeight: '600',
    };
    
    switch (status?.toLowerCase()) {
      case 'in_review':
        return { ...baseStyle, background: '#DBEAFE', color: '#1E40AF' };
      case 'pending_approval':
        return { ...baseStyle, background: '#FEF3C7', color: '#92400E' };
      case 'approved':
        return { ...baseStyle, background: '#D1FAE5', color: '#065F46' };
      default:
        return { ...baseStyle, background: '#F3F4F6', color: '#1F2937' };
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading case...</div>;
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

  if (!caseData) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Case not found</div>;
  }

  return (
    <div className="main-content" style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="case-header" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <div className="case-header-top" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
          <div>
            <div className="case-number" style={{ fontSize: '24px', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>
              CASE-{caseData.id.toString().padStart(4, '0')}
            </div>
            <div className="case-customer" style={{ fontSize: '14px', color: '#6B7280' }}>
              Customer: {caseData.customer_id} | Order: {caseData.order_reference}
            </div>
          </div>
          <div style={getStatusBadgeStyle(caseData.current_status)}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'currentColor' }}></span>
            {caseData.current_status.replace('_', ' ')}
          </div>
        </div>

        <div className="case-meta" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
          <div className="meta-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="meta-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Assignee
            </div>
            <div className="meta-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              {caseData.assigned_to_id ? `User ${caseData.assigned_to_id}` : 'Unassigned'}
            </div>
          </div>
          <div className="meta-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="meta-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Created
            </div>
            <div className="meta-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              {formatDateTime(caseData.created_at)}
            </div>
          </div>
          <div className="meta-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="meta-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Last Updated
            </div>
            <div className="meta-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              {formatDateTime(caseData.updated_at)}
            </div>
          </div>
          <div className="meta-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="meta-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Exposure
            </div>
            <div className="meta-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              $25,000.00 USD
            </div>
          </div>
        </div>
      </div>

      <div className="content-grid" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div>
          <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
            <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
              Intake Summary
            </h2>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Requested Outcome</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>{caseData.requested_outcome || 'Release'}</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Requested Discount</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>15%</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Payment Terms</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>Net 30</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Contract Term</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>24 months</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Exception Type</span>
              <span style={{ color: '#F59E0B', fontWeight: '600', textAlign: 'right' }}>
                {caseData.exception_flag ? 'Discount Exception' : 'None'}
              </span>
            </div>
          </div>

          <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
            <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
              Credit Assessment Workspace
            </h2>

            <div className="assessment-section" style={{ marginBottom: '24px' }}>
              <div className="assessment-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
                Risk Level
              </div>
              <select
                value={riskLevel}
                onChange={(e) => setRiskLevel(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF', height: '48px' }}
              >
                <option value="">Select risk level...</option>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
              </select>
            </div>

            <div className="assessment-section" style={{ marginBottom: '24px' }}>
              <div className="assessment-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
                Findings
              </div>
              <textarea
                value={findings}
                onChange={(e) => setFindings(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF', minHeight: '100px', resize: 'vertical' }}
              />
            </div>

            <div className="assessment-section" style={{ marginBottom: '24px' }}>
              <div className="assessment-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
                Recommendation
              </div>
              <div className="recommendation-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                {['Release', 'Hold', 'Amend', 'Decline'].map((option) => (
                  <div
                    key={option}
                    onClick={() => setRecommendation(option)}
                    style={{
                      padding: '16px',
                      border: recommendation === option ? '2px solid #0066CC' : '2px solid #E5E7EB',
                      borderRadius: '8px',
                      textAlign: 'center',
                      cursor: 'pointer',
                      background: recommendation === option ? '#EFF6FF' : '#FFFFFF',
                    }}
                  >
                    <div style={{ fontWeight: '600', color: '#111827', marginBottom: '4px' }}>{option}</div>
                    <div style={{ fontSize: '12px', color: '#6B7280' }}>
                      {option === 'Release' && 'Approve order'}
                      {option === 'Hold' && 'Pending review'}
                      {option === 'Amend' && 'Modify terms'}
                      {option === 'Decline' && 'Reject order'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="assessment-section">
              <div className="assessment-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
                Rationale
              </div>
              <textarea
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF', minHeight: '100px', resize: 'vertical' }}
              />
            </div>
          </div>
        </div>

        <div>
          <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
            <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
              Approval Status
            </h2>
            {caseData.exception_flag && (
              <div style={{ background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: '8px', padding: '16px', marginBottom: '16px' }}>
                <div style={{ fontWeight: '600', color: '#92400E', marginBottom: '4px' }}>Pending Manager Approval</div>
                <div style={{ fontSize: '13px', color: '#78350F' }}>Discount exceeds analyst authority</div>
              </div>
            )}
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Authority Level</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>Manager</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Assigned To</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>Jane Smith</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Escalated</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>{formatDateTime(caseData.updated_at)}</span>
            </div>
          </div>

          <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
            <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
              Fulfilment Tracking
            </h2>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #E5E7EB' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Status</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>Awaiting Decision</span>
            </div>
            <div className="info-row" style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
              <span style={{ fontWeight: '600', color: '#6B7280' }}>Target Date</span>
              <span style={{ color: '#111827', textAlign: 'right' }}>Aug 25, 2024</span>
            </div>
          </div>

          <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
            <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
              Audit Timeline
            </h2>
            <div className="timeline-item" style={{ display: 'flex', gap: '16px', padding: '16px 0', borderBottom: '1px solid #E5E7EB' }}>
              <div className="timeline-icon" style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#DBEAFE', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: '#0066CC', fontWeight: '700', fontSize: '12px' }}>
                3
              </div>
              <div className="timeline-content" style={{ flex: 1 }}>
                <div className="timeline-action" style={{ fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                  Assessment Updated
                </div>
                <div className="timeline-meta" style={{ fontSize: '12px', color: '#6B7280' }}>
                  {formatDateTime(caseData.updated_at)}
                </div>
              </div>
            </div>
            <div className="timeline-item" style={{ display: 'flex', gap: '16px', padding: '16px 0', borderBottom: '1px solid #E5E7EB' }}>
              <div className="timeline-icon" style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#DBEAFE', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: '#0066CC', fontWeight: '700', fontSize: '12px' }}>
                2
              </div>
              <div className="timeline-content" style={{ flex: 1 }}>
                <div className="timeline-action" style={{ fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                  Escalated for Approval
                </div>
                <div className="timeline-meta" style={{ fontSize: '12px', color: '#6B7280' }}>
                  System • {formatDateTime(caseData.updated_at)}
                </div>
              </div>
            </div>
            <div className="timeline-item" style={{ display: 'flex', gap: '16px', padding: '16px 0' }}>
              <div className="timeline-icon" style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#DBEAFE', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: '#0066CC', fontWeight: '700', fontSize: '12px' }}>
                1
              </div>
              <div className="timeline-content" style={{ flex: 1 }}>
                <div className="timeline-action" style={{ fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                  Case Created
                </div>
                <div className="timeline-meta" style={{ fontSize: '12px', color: '#6B7280' }}>
                  {formatDateTime(caseData.created_at)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="action-bar" style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', paddingTop: '24px', borderTop: '1px solid #E5E7EB', marginTop: '24px' }}>
        <button
          style={{ height: '48px', padding: '0 24px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}
        >
          Save Draft
        </button>
        <button
          onClick={handleSubmitForApproval}
          style={{ height: '48px', padding: '0 24px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}
        >
          Submit for Approval
        </button>
      </div>
    </div>
  );
}
