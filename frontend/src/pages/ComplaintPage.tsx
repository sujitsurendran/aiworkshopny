/**
 * ComplaintPage - Complaint Management
 * Matches wireframe_complaint_management.html structure and styling exactly.
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';

interface Complaint {
  id: string;
  caseId: string;
  status: 'open' | 'in-progress' | 'resolved';
  category: string;
  created: string;
  summary: string;
}

export function ComplaintPage() {
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('open');
  const [ownerFilter, setOwnerFilter] = useState('me');
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint>({
    id: 'CMPL-2024-00012',
    caseId: 'CASE-2024-00123',
    status: 'open',
    category: 'Delayed Fulfilment',
    created: 'Aug 18, 2024',
    summary: 'Customer reports delayed fulfilment after order release approval. Expected delivery date passed without shipment notification.',
  });
  const [updateStatus, setUpdateStatus] = useState('open');
  const [resolutionNotes, setResolutionNotes] = useState('Contacted fulfilment team to investigate delay. Shipment was held due to inventory allocation issue. Expedited shipping arranged for August 28, 2024. Customer notified of revised delivery date and provided tracking information.');

  const complaints: Complaint[] = [
    { id: 'CMPL-2024-00012', caseId: 'CASE-2024-00123', status: 'open', category: 'Delayed Fulfilment', created: 'Aug 18, 2024', summary: 'Customer reports delayed fulfilment after order release approval. Expected delivery date passed without shipment notification.' },
    { id: 'CMPL-2024-00011', caseId: 'CASE-2024-00118', status: 'in-progress', category: 'Terms Dispute', created: 'Aug 16, 2024', summary: 'Dispute regarding payment terms modification. Customer expected original terms to remain unchanged.' },
    { id: 'CMPL-2024-00010', caseId: 'CASE-2024-00115', status: 'open', category: 'Declined Order', created: 'Aug 15, 2024', summary: 'Customer questions declined order decision. Requests review of credit assessment rationale.' },
  ];

  const getStatusBadgeStyle = (status: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'inline-flex',
      alignItems: 'center',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: '600',
    };
    switch (status) {
      case 'open':
        return { ...baseStyle, background: '#FEE2E2', color: '#991B1B' };
      case 'in-progress':
        return { ...baseStyle, background: '#DBEAFE', color: '#1E40AF' };
      case 'resolved':
        return { ...baseStyle, background: '#D1FAE5', color: '#065F46' };
      default:
        return baseStyle;
    }
  };

  const handleSaveUpdates = async () => {
    try {
      await apiClient.submitOperation(123, {
        operationType: 'complaint',
        complaint_id: selectedComplaint.id,
        status: updateStatus,
        resolution_notes: resolutionNotes,
      });
      alert('Complaint updated successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update complaint');
    }
  };

  return (
    <div className="main-content" style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '32px' }}>
        <div>
          <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
            Complaint Management
          </h1>
          <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
            Track and resolve customer complaints linked to credit review cases
          </p>
        </div>
        <button className="btn btn-primary" style={{ height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}>
          + New Complaint
        </button>
      </div>

      <div className="content-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        <div>
          <div className="filter-panel" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', height: 'fit-content' }}>
            <h3 className="filter-title" style={{ fontSize: '16px', fontWeight: '700', color: '#111827', marginBottom: '20px' }}>
              Filters
            </h3>

            <div className="filter-group" style={{ marginBottom: '20px' }}>
              <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', display: 'block' }}>
                Category
              </label>
              <select className="filter-input" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} style={{ width: '100%', height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
                <option value="">All Categories</option>
                <option value="delayed">Delayed Fulfilment</option>
                <option value="declined">Declined Order</option>
                <option value="terms">Terms Dispute</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="filter-group" style={{ marginBottom: '20px' }}>
              <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', display: 'block' }}>
                Status
              </label>
              <select className="filter-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ width: '100%', height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="in-progress">In Progress</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>

            <div className="filter-group" style={{ marginBottom: '20px' }}>
              <label className="filter-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', display: 'block' }}>
                Owner
              </label>
              <select className="filter-input" value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)} style={{ width: '100%', height: '44px', padding: '0 12px', border: '1px solid #E5E7EB', borderRadius: '6px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
                <option value="">All Owners</option>
                <option value="me">Assigned to Me</option>
                <option value="team">My Team</option>
              </select>
            </div>

            <button className="btn btn-primary" style={{ width: '100%', height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF', marginTop: '12px' }}>
              Apply Filters
            </button>
          </div>

          <div style={{ marginTop: '24px', padding: '16px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '8px' }}>
            <div style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', marginBottom: '8px' }}>SUMMARY</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px', color: '#111827' }}>Total Complaints</span>
              <span style={{ fontWeight: '700', color: '#111827' }}>23</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px', color: '#111827' }}>Open</span>
              <span style={{ fontWeight: '700', color: '#EF4444' }}>15</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '14px', color: '#111827' }}>Resolved This Week</span>
              <span style={{ fontWeight: '700', color: '#10B981' }}>8</span>
            </div>
          </div>
        </div>

        <div>
          <div className="complaint-list" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {complaints.map((complaint) => (
              <div key={complaint.id} onClick={() => setSelectedComplaint(complaint)} className={`complaint-card ${selectedComplaint.id === complaint.id ? 'selected' : ''}`} style={{ background: selectedComplaint.id === complaint.id ? '#EFF6FF' : '#F9FAFB', border: selectedComplaint.id === complaint.id ? '1px solid #0066CC' : '1px solid #E5E7EB', borderRadius: '12px', padding: '20px', cursor: 'pointer' }}>
                <div className="complaint-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                  <div className="complaint-id" style={{ fontSize: '16px', fontWeight: '700', color: '#0066CC' }}>
                    {complaint.id}
                  </div>
                  <div className="status-badge" style={getStatusBadgeStyle(complaint.status)}>
                    {complaint.status === 'open' ? 'Open' : complaint.status === 'in-progress' ? 'In Progress' : 'Resolved'}
                  </div>
                </div>
                <div className="complaint-meta" style={{ display: 'flex', gap: '16px', fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                  <span>Case: {complaint.caseId}</span>
                  <span>•</span>
                  <span>Created: {complaint.created}</span>
                </div>
                <div className="complaint-summary" style={{ fontSize: '14px', color: '#111827', lineHeight: '1.5' }}>
                  {complaint.summary}
                </div>
              </div>
            ))}
          </div>

          <div className="detail-panel" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginTop: '24px' }}>
            <h2 className="detail-title" style={{ fontSize: '20px', fontWeight: '700', color: '#111827', marginBottom: '20px' }}>
              Complaint Detail: {selectedComplaint.id}
            </h2>

            <div className="info-section" style={{ marginBottom: '24px' }}>
              <div className="section-label" style={{ fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
                Complaint Information
              </div>
              <div className="info-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px' }}>
                <div className="info-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div className="info-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>Complaint ID</div>
                  <div className="info-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{selectedComplaint.id}</div>
                </div>
                <div className="info-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div className="info-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>Status</div>
                  <div className="info-value" style={{ fontSize: '14px', fontWeight: '600', color: '#EF4444' }}>{selectedComplaint.status === 'open' ? 'Open' : selectedComplaint.status === 'in-progress' ? 'In Progress' : 'Resolved'}</div>
                </div>
                <div className="info-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div className="info-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>Category</div>
                  <div className="info-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{selectedComplaint.category}</div>
                </div>
                <div className="info-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div className="info-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>Owner</div>
                  <div className="info-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>Sarah Johnson</div>
                </div>
                <div className="info-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div className="info-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>Linked Case</div>
                  <div className="info-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                    <Link to={`/cases/${selectedComplaint.caseId.split('-')[2]}`} style={{ color: '#0066CC', textDecoration: 'none' }}>
                      {selectedComplaint.caseId}
                    </Link>
                  </div>
                </div>
                <div className="info-item" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div className="info-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280' }}>Originating Outcome</div>
                  <div className="info-value" style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>Release</div>
                </div>
              </div>
            </div>

            <div className="info-section" style={{ marginBottom: '24px' }}>
              <div className="section-label" style={{ fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
                Complaint Summary
              </div>
              <div className="text-box" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px', fontSize: '14px', color: '#111827', lineHeight: '1.6' }}>
                Customer reports delayed fulfilment after order release approval. Expected delivery date of August 25, 2024 has passed without shipment notification or tracking information. Customer has contacted support twice requesting status update. Order was approved on August 17, 2024 with standard fulfilment terms.
              </div>
            </div>

            <div className="info-section">
              <div className="section-label" style={{ fontSize: '12px', fontWeight: '700', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px' }}>
                Resolution Notes
              </div>
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
                  Update Status
                </label>
                <select className="form-input" value={updateStatus} onChange={(e) => setUpdateStatus(e.target.value)} style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF' }}>
                  <option value="open">Open</option>
                  <option value="in-progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
                  Resolution Notes
                </label>
                <textarea className="form-input" value={resolutionNotes} onChange={(e) => setResolutionNotes(e.target.value)} placeholder="Add resolution notes..." style={{ width: '100%', minHeight: '100px', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#FFFFFF', resize: 'vertical' }} />
              </div>
            </div>

            <div className="action-bar" style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', paddingTop: '20px', borderTop: '1px solid #E5E7EB' }}>
              <button className="btn btn-secondary" style={{ height: '44px', padding: '0 20px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}>
                Cancel
              </button>
              <button onClick={handleSaveUpdates} className="btn btn-primary" style={{ height: '44px', padding: '0 20px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}>
                Save Updates
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
