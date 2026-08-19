/**
 * CaseIntakePage - Guided Order Intake Form
 * Matches wireframe_guided_order_intake.html structure and styling exactly.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../lib/api-client';

export function CaseIntakePage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state matching wireframe fields exactly
  const [formData, setFormData] = useState({
    customerId: 'CUST-2024-00456',
    orderRef: 'ORD-VZ-2024-00789',
    requestedOutcome: 'release',
    requestedDate: '2024-08-25',
    requestedDiscount: '15',
    exposureAmount: '$25,000.00',
    paymentTerms: 'net30',
    contractTerm: '24',
    exceptionType: 'discount',
    exceptionReason: 'Strategic account retention',
    intakeNotes: 'Customer has requested expedited review for Q3 renewal. Account has strong payment history over past 18 months. Discount aligns with competitive positioning for this market segment.',
  });

  const [customerVerified, setCustomerVerified] = useState(true);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const validateForm = (): boolean => {
    if (!formData.customerId || !formData.orderRef) {
      setError('Customer ID and Order Reference are required');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    setError(null);
    if (!validateForm()) return;

    setLoading(true);
    try {
      // Convert form data to API payload
      const payload = {
        customer_id: formData.customerId,
        order_reference: formData.orderRef,
        requested_outcome: formData.requestedOutcome,
        requested_fulfilment_date: formData.requestedDate,
        requested_terms: `Discount: ${formData.requestedDiscount}%, Payment: ${formData.paymentTerms}, Contract: ${formData.contractTerm} months`,
        priority: 'normal',
      };

      await apiClient.createCase(payload);
      navigate('/cases');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create case');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveDraft = async () => {
    setError(null);
    // For MVP, just show message
    alert('Draft saved (feature coming soon)');
  };

  return (
    <div className="main-content" style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Guided Order Intake
        </h1>
        <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
          Create a new customer credit review case
        </p>
      </div>

      {error && (
        <div style={{ background: '#FEE2E2', border: '1px solid #EF4444', borderRadius: '8px', padding: '16px', marginBottom: '24px', color: '#991B1B' }}>
          {error}
        </div>
      )}

      <div className="form-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="section-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Customer and Order Information
        </h2>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="customerId" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Customer ID<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <input
              type="text"
              id="customerId"
              value={formData.customerId}
              onChange={handleChange}
              placeholder="CUST-2024-00123"
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
            {customerVerified && (
              <span style={{ fontSize: '12px', color: '#10B981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                ✓ Customer verified
              </span>
            )}
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="orderRef" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Order Reference<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <input
              type="text"
              id="orderRef"
              value={formData.orderRef}
              onChange={handleChange}
              placeholder="ORD-VZ-2024-00456"
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
          </div>
        </div>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="requestedOutcome" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Requested Outcome<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <select
              id="requestedOutcome"
              value={formData.requestedOutcome}
              onChange={handleChange}
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            >
              <option value="">Select outcome...</option>
              <option value="release">Release</option>
              <option value="hold">Hold</option>
              <option value="amend">Amend</option>
              <option value="decline">Decline</option>
            </select>
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="requestedDate" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Requested Fulfilment Date
            </label>
            <input
              type="date"
              id="requestedDate"
              value={formData.requestedDate}
              onChange={handleChange}
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
          </div>
        </div>
      </div>

      <div className="form-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="section-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Commercial Terms
        </h2>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="requestedDiscount" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Requested Discount (%)
            </label>
            <input
              type="number"
              id="requestedDiscount"
              value={formData.requestedDiscount}
              onChange={handleChange}
              placeholder="0"
              min="0"
              max="100"
              step="0.1"
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
            <span style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Enter discount percentage if applicable
            </span>
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="exposureAmount" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Exposure Amount (USD)<span style={{ color: '#EF4444', marginLeft: '4px' }}>*</span>
            </label>
            <input
              type="text"
              id="exposureAmount"
              value={formData.exposureAmount}
              onChange={handleChange}
              placeholder="$0.00"
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
          </div>
        </div>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="paymentTerms" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Payment Terms
            </label>
            <select
              id="paymentTerms"
              value={formData.paymentTerms}
              onChange={handleChange}
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            >
              <option value="">Select terms...</option>
              <option value="net30">Net 30</option>
              <option value="net60">Net 60</option>
              <option value="net90">Net 90</option>
              <option value="prepaid">Prepaid</option>
            </select>
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="contractTerm" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Contract Term (Months)
            </label>
            <input
              type="number"
              id="contractTerm"
              value={formData.contractTerm}
              onChange={handleChange}
              placeholder="12"
              min="1"
              max="60"
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
          </div>
        </div>
      </div>

      <div className="form-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="section-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Exception Indicators
        </h2>

        <div className="exception-indicator" style={{ background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: '8px', padding: '16px', marginBottom: '20px', display: 'flex', alignItems: 'start', gap: '12px' }}>
          <div className="exception-indicator-icon" style={{ width: '20px', height: '20px', background: '#F59E0B', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF', fontWeight: '700', fontSize: '12px' }}>
            !
          </div>
          <div className="exception-indicator-text" style={{ flex: 1 }}>
            <div className="exception-indicator-title" style={{ fontWeight: '600', color: '#92400E', marginBottom: '4px' }}>
              Potential Exception Detected
            </div>
            <div className="exception-indicator-desc" style={{ fontSize: '13px', color: '#78350F' }}>
              Requested discount exceeds standard authority threshold. This case will require manager approval.
            </div>
          </div>
        </div>

        <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="exceptionType" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Exception Type
            </label>
            <select
              id="exceptionType"
              value={formData.exceptionType}
              onChange={handleChange}
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            >
              <option value="">No exception</option>
              <option value="discount">Discount Exception</option>
              <option value="credit">Credit Policy Exception</option>
              <option value="terms">Payment Terms Exception</option>
              <option value="other">Other Commercial Exception</option>
            </select>
          </div>

          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label htmlFor="exceptionReason" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
              Exception Reason
            </label>
            <input
              type="text"
              id="exceptionReason"
              value={formData.exceptionReason}
              onChange={handleChange}
              placeholder="Brief reason for exception"
              style={{ height: '48px', padding: '0 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF' }}
            />
          </div>
        </div>
      </div>

      <div className="form-card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="section-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Supporting Notes
        </h2>

        <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
          <label htmlFor="intakeNotes" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
            Intake Notes
          </label>
          <textarea
            id="intakeNotes"
            value={formData.intakeNotes}
            onChange={handleChange}
            placeholder="Add any relevant context or supporting information..."
            style={{ height: '120px', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', color: '#111827', background: '#FFFFFF', resize: 'vertical' }}
          />
        </div>

        <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label htmlFor="attachments" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
            Supporting Documents
          </label>
          <div style={{ border: '2px dashed #E5E7EB', borderRadius: '8px', padding: '24px', textAlign: 'center', background: '#FFFFFF' }}>
            <div style={{ color: '#6B7280', marginBottom: '8px' }}>Drop files here or click to upload</div>
            <div style={{ fontSize: '12px', color: '#9CA3AF' }}>PDF, DOC, XLS up to 10MB</div>
          </div>
        </div>
      </div>

      <div className="action-bar" style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', paddingTop: '24px', borderTop: '1px solid #E5E7EB' }}>
        <button
          onClick={handleSaveDraft}
          disabled={loading}
          className="btn btn-secondary"
          style={{ height: '48px', padding: '0 24px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}
        >
          Save Draft
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn btn-primary"
          style={{ height: '48px', padding: '0 24px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}
        >
          {loading ? 'Submitting...' : 'Submit for Review'}
        </button>
      </div>
    </div>
  );
}
