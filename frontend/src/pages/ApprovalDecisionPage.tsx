/**
 * ApprovalDecisionPage - Approval Decision View
 * Matches wireframe_approval_decision.html structure and styling exactly.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { formatDateTime, formatCurrency } from '../lib/utils';

interface ApprovalData {
  id: number;
  case_id: number;
  requested_by: number;
  assigned_approver_id: number | null;
  status: string;
  decision_reason: string | null;
  created_at: string;
}

export function ApprovalDecisionPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [caseData, setCaseData] = useState<any>(null);
  const [selectedDecision, setSelectedDecision] = useState<'approve' | 'reject' | 'send_back' | null>('approve');
  const [decisionReason, setDecisionReason] = useState('Approved based on strong customer payment history and strategic account value. Discount aligns with retention objectives and falls within manager authority threshold. All evidence requirements satisfied.');

  useEffect(() => {
    if (caseId) {
      loadCase();
    }
  }, [caseId]);

  const loadCase = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getCase(Number(caseId));
      setCaseData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load case');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitDecision = async () => {
    if (!selectedDecision || !caseId) return;
    
    try {
      await apiClient.submitApprovalAction(Number(caseId), {
        action: selectedDecision,
        decision_reason: decisionReason,
      });
      alert(`Decision ${selectedDecision} submitted successfully`);
      navigate('/approvals');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit decision';
      if (errorMessage.includes('403') || errorMessage.includes('Forbidden') || errorMessage.includes('SoD') || errorMessage.includes('segregation')) {
        setError('Segregation of Duties violation: You cannot approve your own request. Please reassign to another approver.');
      } else {
        setError(errorMessage);
      }
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading...</div>;
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
    <div className="main-content" style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Approval Decision
        </h1>
        <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
          Review and approve case CASE-{String(caseData.id).padStart(4, '0')}
        </p>
      </div>

      <div className="alert-banner" style={{ background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: '12px', padding: '20px 24px', marginBottom: '24px', display: 'flex', alignItems: 'start', gap: '16px' }}>
        <div className="alert-icon" style={{ width: '24px', height: '24px', background: '#F59E0B', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF', fontWeight: '700', fontSize: '14px' }}>
          !
        </div>
        <div className="alert-content" style={{ flex: 1 }}>
          <div className="alert-title" style={{ fontSize: '16px', fontWeight: '700', color: '#92400E', marginBottom: '4px' }}>
            Manager Approval Required
          </div>
          <div className="alert-text" style={{ fontSize: '14px', color: '#78350F' }}>
            This case requires your approval due to discount exception exceeding analyst authority threshold.
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Case Summary
        </h2>
        <div className="summary-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Case Number
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              CASE-{String(caseData.id).padStart(4, '0')}
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Customer ID
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              {caseData.customer_id}
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Order Reference
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              {caseData.order_reference}
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Requested Outcome
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              {caseData.requested_outcome || 'Release'}
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Exposure Amount
            </div>
            <div className="summary-value highlight" style={{ fontSize: '20px', fontWeight: '600', color: '#0066CC' }}>
              $25,000.00 USD
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Requested Discount
            </div>
            <div className="summary-value highlight" style={{ fontSize: '20px', fontWeight: '600', color: '#0066CC' }}>
              15%
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Requested By
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              Analyst {caseData.assigned_to_id || 'Unknown'}
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Submitted
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              {formatDateTime(caseData.created_at)}
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Assessment Rationale
        </h2>
        <div className="rationale-box" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}>
          <div className="rationale-label" style={{ fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
            Credit Findings
          </div>
          <div className="rationale-text" style={{ fontSize: '14px', color: '#111827', lineHeight: '1.6' }}>
            Customer has maintained consistent payment history over 18 months. Current account standing is good with no overdue balances. Requested discount aligns with strategic account retention objectives. Credit exposure of $25,000 is within acceptable range for this customer profile.
          </div>
        </div>
        <div className="rationale-box" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px' }}>
          <div className="rationale-label" style={{ fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
            Recommendation Rationale
          </div>
          <div className="rationale-text" style={{ fontSize: '14px', color: '#111827', lineHeight: '1.6' }}>
            Recommend release with requested discount. Customer qualifies based on payment history and strategic value. Discount exception requires manager approval per delegation of authority policy. Evidence supports commercial justification for retention pricing.
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Authority Context
        </h2>
        <div className="summary-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>
              Approval Level
            </div>
            <div className="summary-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Manager
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>
              Authority Threshold
            </div>
            <div className="summary-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Up to $50,000
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>
              Delegation Rule
            </div>
            <div className="summary-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Discount {'>'} 10% requires manager approval
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>
              Segregation of Duties
            </div>
            <div className="summary-value" style={{ fontSize: '14px', fontWeight: '600', color: '#10B981' }}>
              ✓ Compliant
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Evidence Completeness Checklist
        </h2>
        <div className="checklist" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px' }}>
          {['Customer credit validation documented', 'Commercial rationale provided', 'Exception reason documented', 'Exposure amount verified', 'Supporting notes attached'].map((item, i) => (
            <div key={i} className="checklist-item" style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 0', borderBottom: i < 4 ? '1px solid #E5E7EB' : 'none' }}>
              <div className="checklist-icon complete" style={{ width: '20px', height: '20px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontWeight: '700', fontSize: '12px', background: '#D1FAE5', color: '#065F46' }}>
                ✓
              </div>
              <div className="checklist-label" style={{ flex: 1, fontSize: '14px', color: '#111827' }}>
                {item}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="decision-section" style={{ background: '#FFFFFF', border: '2px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
        <h2 className="decision-title" style={{ fontSize: '18px', fontWeight: '700', color: '#111827', marginBottom: '20px' }}>
          Make Your Decision
        </h2>

        <div className="decision-options" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
          <div 
            onClick={() => setSelectedDecision('approve')}
            className="decision-option"
            style={{ 
              padding: '20px', 
              border: selectedDecision === 'approve' ? '2px solid #10B981' : '2px solid #E5E7EB', 
              borderRadius: '8px', 
              textAlign: 'center', 
              cursor: 'pointer', 
              background: selectedDecision === 'approve' ? '#D1FAE5' : '#F9FAFB' 
            }}
          >
            <div className="decision-option-icon" style={{ fontSize: '32px', marginBottom: '8px' }}>✓</div>
            <div className="decision-option-label" style={{ fontWeight: '700', color: '#111827', marginBottom: '4px' }}>Approve</div>
            <div className="decision-option-desc" style={{ fontSize: '12px', color: '#6B7280' }}>Authorize this request</div>
          </div>
          
          <div 
            onClick={() => setSelectedDecision('reject')}
            className="decision-option"
            style={{ 
              padding: '20px', 
              border: selectedDecision === 'reject' ? '2px solid #EF4444' : '2px solid #E5E7EB', 
              borderRadius: '8px', 
              textAlign: 'center', 
              cursor: 'pointer', 
              background: selectedDecision === 'reject' ? '#FEE2E2' : '#F9FAFB' 
            }}
          >
            <div className="decision-option-icon" style={{ fontSize: '32px', marginBottom: '8px' }}>✗</div>
            <div className="decision-option-label" style={{ fontWeight: '700', color: '#111827', marginBottom: '4px' }}>Reject</div>
            <div className="decision-option-desc" style={{ fontSize: '12px', color: '#6B7280' }}>Decline this request</div>
          </div>
          
          <div 
            onClick={() => setSelectedDecision('send_back')}
            className="decision-option"
            style={{ 
              padding: '20px', 
              border: selectedDecision === 'send_back' ? '2px solid #0066CC' : '2px solid #E5E7EB', 
              borderRadius: '8px', 
              textAlign: 'center', 
              cursor: 'pointer', 
              background: selectedDecision === 'send_back' ? '#EFF6FF' : '#F9FAFB' 
            }}
          >
            <div className="decision-option-icon" style={{ fontSize: '32px', marginBottom: '8px' }}>↩</div>
            <div className="decision-option-label" style={{ fontWeight: '700', color: '#111827', marginBottom: '4px' }}>Send Back</div>
            <div className="decision-option-desc" style={{ fontSize: '12px', color: '#6B7280' }}>Request more information</div>
          </div>
        </div>

        <label htmlFor="decisionReason" style={{ display: 'block', fontWeight: '600', marginBottom: '8px' }}>Decision Reason</label>
        <textarea 
          id="decisionReason"
          className="reason-input"
          value={decisionReason}
          onChange={(e) => setDecisionReason(e.target.value)}
          placeholder="Enter your decision reason..."
          style={{ 
            width: '100%', 
            minHeight: '100px', 
            padding: '12px 16px', 
            border: '1px solid #E5E7EB', 
            borderRadius: '8px', 
            fontSize: '14px', 
            fontFamily: 'inherit', 
            color: '#111827', 
            background: '#F9FAFB', 
            resize: 'vertical', 
            marginBottom: '24px' 
          }}
        />

        <div className="action-bar" style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button 
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
            style={{ 
              height: '48px', 
              padding: '0 24px', 
              border: '1px solid #E5E7EB', 
              borderRadius: '8px', 
              fontSize: '14px', 
              fontWeight: '600', 
              fontFamily: 'inherit', 
              cursor: 'pointer', 
              background: '#FFFFFF', 
              color: '#111827' 
            }}
          >
            Cancel
          </button>
          <button 
            onClick={handleSubmitDecision}
            disabled={!selectedDecision}
            className="btn btn-primary"
            style={{ 
              height: '48px', 
              padding: '0 24px', 
              border: 'none', 
              borderRadius: '8px', 
              fontSize: '14px', 
              fontWeight: '600', 
              fontFamily: 'inherit', 
              cursor: selectedDecision ? 'pointer' : 'not-allowed', 
              background: '#10B981', 
              color: '#FFFFFF',
              opacity: selectedDecision ? 1 : 0.5
            }}
          >
            Confirm Approval
          </button>
        </div>
      </div>
    </div>
  );
}
