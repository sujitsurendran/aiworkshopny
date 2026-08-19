/**
 * RefundPage - Refund Authorisation
 * Matches wireframe_refund_authorisation.html structure and styling exactly.
 */

import React, { useState } from 'react';
import { apiClient } from '../lib/api-client';
import { formatCurrency } from '../lib/utils';

export function RefundPage() {
  const [linkedCase, setLinkedCase] = useState('CASE-2024-00123');
  const [actionType, setActionType] = useState('partial-refund');
  const [amount, setAmount] = useState('$2,500.00');
  const [currency, setCurrency] = useState('USD');
  const [reason, setReason] = useState('Customer experienced delayed fulfilment beyond committed delivery date. Partial refund authorized as service recovery measure per customer success policy. Amount represents 10% of order value as compensation for delivery delay.');
  const [status, setStatus] = useState('pending');
  const [owner, setOwner] = useState('me');
  const [financialImpactFlag, setFinancialImpactFlag] = useState(true);

  const handleSaveRefund = async () => {
    try {
      // Extract numeric amount
      const numericAmount = parseFloat(amount.replace(/[$,]/g, ''));
      
      // Validate financial impact flag for significant refunds
      if (financialImpactFlag && numericAmount > 1000 && status === 'pending') {
        alert('Financial impact flag is set. Please ensure evidence is confirmed before submitting for approval.');
        return;
      }

      const caseId = parseInt(linkedCase.split('-')[2]);
      await apiClient.submitOperation(caseId, {
        operationType: 'refund',
        action_type: actionType,
        amount: numericAmount,
        currency,
        reason,
        status,
        financial_impact_flag: financialImpactFlag,
        evidence_confirmed: status !== 'pending',
      });
      alert('Refund action saved successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save refund';
      if (errorMessage.includes('422') || errorMessage.includes('evidence')) {
        alert('Validation Error: Financial impact refunds require evidence confirmation before approval.');
      } else {
        alert(errorMessage);
      }
    }
  };

  const refunds = [
    { id: 'RFND-2024-00005', caseId: 'CASE-2024-00123', type: 'Partial Refund', created: 'Aug 18, 2024', status: 'pending', amount: '$2,500.00' },
    { id: 'RFND-2024-00004', caseId: 'CASE-2024-00118', type: 'Full Refund', created: 'Aug 16, 2024', status: 'approved', amount: '$18,750.00' },
    { id: 'RFND-2024-00003', caseId: 'CASE-2024-00112', type: 'Partial Refund', created: 'Aug 14, 2024', status: 'completed', amount: '$1,200.00' },
    { id: 'RFND-2024-00002', caseId: 'CASE-2024-00106', type: 'Return Processing', created: 'Aug 12, 2024', status: 'completed', amount: '$5,400.00' },
  ];

  const getStatusBadgeStyle = (status: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: '600',
      marginTop: '4px',
    };
    switch (status) {
      case 'pending':
        return { ...baseStyle, background: '#FEF3C7', color: '#92400E' };
      case 'approved':
        return { ...baseStyle, background: '#D1FAE5', color: '#065F46' };
      case 'completed':
        return { ...baseStyle, background: '#E0E7FF', color: '#3730A3' };
      default:
        return baseStyle;
    }
  };

  return (
    <div className="main-content" style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '32px' }}>
        <div>
          <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
            Refund Authorisation
          </h1>
          <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
            Manage refund and return actions linked to credit review cases
          </p>
        </div>
        <button className="btn btn-primary" style={{ height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}>
          + New Refund Action
        </button>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Create Refund Action
        </h2>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Linked Case<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <input type="text" className="form-input" value={linkedCase} onChange={(e) => setLinkedCase(e.target.value)} placeholder="CASE-2024-00123" style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }} />
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Action Type<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <select className="form-input" value={actionType} onChange={(e) => setActionType(e.target.value)} style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
              <option value="">Select action type...</option>
              <option value="full-refund">Full Refund</option>
              <option value="partial-refund">Partial Refund</option>
              <option value="return">Return Processing</option>
              <option value="credit-note">Credit Note</option>
            </select>
          </div>
        </div>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Amount (USD)<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <input type="text" className="form-input" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="$0.00" style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }} />
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Currency
            </label>
            <select className="form-input" value={currency} onChange={(e) => setCurrency(e.target.value)} style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </select>
          </div>
        </div>

        {financialImpactFlag && (
          <div className="financial-impact-banner" style={{ background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: '8px', padding: '16px', marginBottom: '20px', display: 'flex', alignItems: 'start', gap: '12px' }}>
            <div className="banner-icon" style={{ width: '20px', height: '20px', background: '#F59E0B', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF', fontWeight: '700', fontSize: '12px' }}>
              $
            </div>
            <div className="banner-text" style={{ flex: 1 }}>
              <div className="banner-title" style={{ fontWeight: '600', color: '#92400E', marginBottom: '4px' }}>
                Financial Impact Flag
              </div>
              <div className="banner-desc" style={{ fontSize: '13px', color: '#78350F' }}>
                This refund amount exceeds the financial significance threshold and requires additional approval and evidence documentation.
              </div>
            </div>
          </div>
        )}

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            Reason<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
          </label>
          <textarea className="form-input" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Enter reason for refund action..." style={{ height: '120px', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF', resize: 'vertical' }} />
        </div>

        <div className="evidence-section" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}>
          <div className="evidence-title" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>
            Evidence Attachments
          </div>
          <div className="evidence-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '6px', marginBottom: '8px' }}>
            <div>
              <div className="evidence-name" style={{ fontSize: '14px', color: '#111827' }}>Delivery_Delay_Documentation.pdf</div>
              <div className="evidence-meta" style={{ fontSize: '12px', color: '#6B7280' }}>Uploaded Aug 18, 2024 • 245 KB</div>
            </div>
          </div>
          <div className="evidence-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '6px', marginBottom: '8px' }}>
            <div>
              <div className="evidence-name" style={{ fontSize: '14px', color: '#111827' }}>Customer_Communication_Log.pdf</div>
              <div className="evidence-meta" style={{ fontSize: '12px', color: '#6B7280' }}>Uploaded Aug 18, 2024 • 182 KB</div>
            </div>
          </div>
          <div style={{ marginTop: '12px' }}>
            <button className="btn btn-secondary" style={{ height: '40px', padding: '0 16px', fontSize: '13px', border: '1px solid #E5E7EB', borderRadius: '8px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}>
              + Add Evidence
            </button>
          </div>
        </div>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Status
            </label>
            <select className="form-input" value={status} onChange={(e) => setStatus(e.target.value)} style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
              <option value="pending">Pending Evidence</option>
              <option value="ready">Ready for Approval</option>
              <option value="approved">Approved</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Owner
            </label>
            <select className="form-input" value={owner} onChange={(e) => setOwner(e.target.value)} style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
              <option value="me">Sarah Johnson</option>
              <option value="other">Reassign...</option>
            </select>
          </div>
        </div>

        <div className="action-bar" style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', paddingTop: '24px', borderTop: '1px solid #E5E7EB' }}>
          <button className="btn btn-secondary" style={{ height: '44px', padding: '0 20px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}>
            Cancel
          </button>
          <button onClick={handleSaveRefund} className="btn btn-primary" style={{ height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}>
            Save Refund Action
          </button>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Recent Refund Actions
        </h2>

        <div style={{ marginBottom: '16px', display: 'flex', gap: '12px' }}>
          <select className="form-input" style={{ maxWidth: '200px', height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="completed">Completed</option>
          </select>
          <select className="form-input" style={{ maxWidth: '200px', height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
            <option value="">All Types</option>
            <option value="full">Full Refund</option>
            <option value="partial">Partial Refund</option>
            <option value="return">Return</option>
          </select>
        </div>

        <div className="refund-list" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', overflow: 'hidden' }}>
          {refunds.map((refund) => (
            <div key={refund.id} className="refund-item" style={{ padding: '16px', borderBottom: refund.id !== refunds[refunds.length - 1].id ? '1px solid #E5E7EB' : 'none', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="refund-info" style={{ flex: 1 }}>
                <div className="refund-id" style={{ fontWeight: '700', color: '#0066CC', marginBottom: '4px' }}>
                  {refund.id}
                </div>
                <div className="refund-meta" style={{ fontSize: '13px', color: '#6B7280' }}>
                  Case: {refund.caseId} • {refund.type} • Created {refund.created}
                </div>
                <div className="status-badge" style={getStatusBadgeStyle(refund.status)}>
                  {refund.status === 'pending' ? 'Pending Evidence' : refund.status === 'approved' ? 'Approved' : 'Completed'}
                </div>
              </div>
              <div className="refund-amount" style={{ fontSize: '18px', fontWeight: '700', color: '#111827', textAlign: 'right' }}>
                {refund.amount}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
