/**
 * FulfilmentPage - Fulfilment Milestone Tracking
 * Matches wireframe_fulfilment_milestones.html structure and styling exactly.
 */

import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../lib/api-client';
import { formatDateTime } from '../lib/utils';

export function FulfilmentPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const [selectedMilestone, setSelectedMilestone] = useState('shipment');
  const [newStatus, setNewStatus] = useState('blocked');
  const [updateNotes, setUpdateNotes] = useState('Alternative carrier arranged. Shipment rescheduled for August 22, 2024. Customer notified of revised delivery timeline. Expedited shipping applied to minimize delay impact.');

  const handleSaveUpdate = async () => {
    if (!caseId) return;
    try {
      await apiClient.submitOperation(Number(caseId), {
        operationType: 'fulfilment',
        milestone: selectedMilestone,
        status: newStatus,
        notes: updateNotes,
      });
      alert('Fulfilment milestone updated successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update milestone');
    }
  };

  const getMilestoneMarkerStyle = (status: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      position: 'absolute',
      left: '-40px',
      top: 0,
      width: '32px',
      height: '32px',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: '700',
      fontSize: '12px',
      border: '3px solid #FFFFFF',
    };
    
    switch (status) {
      case 'completed':
        return { ...baseStyle, background: '#10B981', color: '#FFFFFF' };
      case 'in-progress':
        return { ...baseStyle, background: '#3B82F6', color: '#FFFFFF' };
      case 'blocked':
        return { ...baseStyle, background: '#EF4444', color: '#FFFFFF' };
      case 'pending':
      default:
        return { ...baseStyle, background: '#E5E7EB', color: '#6B7280' };
    }
  };

  const getMilestoneStatusStyle = (status: string): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      display: 'inline-flex',
      alignItems: 'center',
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: '600',
    };
    
    switch (status) {
      case 'completed':
        return { ...baseStyle, background: '#D1FAE5', color: '#065F46' };
      case 'in-progress':
        return { ...baseStyle, background: '#DBEAFE', color: '#1E40AF' };
      case 'blocked':
        return { ...baseStyle, background: '#FEE2E2', color: '#991B1B' };
      case 'pending':
      default:
        return { ...baseStyle, background: '#F3F4F6', color: '#6B7280' };
    }
  };

  const milestones = [
    { id: 'approved', title: 'Order Approved', status: 'completed', owner: 'Jane Smith', completed: 'Aug 17, 2024 03:30 PM', notes: 'Manager approval completed. Order released for fulfilment processing.', blocker: null },
    { id: 'inventory', title: 'Inventory Allocated', status: 'completed', owner: 'Fulfilment Team', completed: 'Aug 18, 2024 10:15 AM', notes: 'Inventory successfully allocated from warehouse. Ready for shipment preparation.', blocker: null },
    { id: 'shipment', title: 'Shipment Prepared', status: 'blocked', owner: 'Logistics Team', completed: 'Aug 20, 2024 02:45 PM', notes: 'Shipment preparation delayed due to carrier capacity constraints.', blocker: 'Carrier capacity issue. Alternative carrier being arranged. Expected resolution by Aug 22, 2024.' },
    { id: 'transit', title: 'In Transit', status: 'pending', owner: 'Logistics Team', completed: 'Aug 23, 2024', notes: 'Awaiting shipment dispatch and tracking information.', blocker: null },
    { id: 'delivered', title: 'Delivered', status: 'pending', owner: 'Logistics Team', completed: 'Aug 25, 2024', notes: 'Final delivery to customer location.', blocker: null },
  ];

  return (
    <div className="main-content" style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title" style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
          Fulfilment Milestone Tracking
        </h1>
        <p className="page-subtitle" style={{ fontSize: '14px', color: '#6B7280' }}>
          Track post-decision fulfilment progress for CASE-{caseId || '0001'}
        </p>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Case Context
        </h2>
        <div className="case-summary" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Case Number
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              <Link to={`/cases/${caseId}`} style={{ color: '#0066CC', textDecoration: 'none' }}>
                CASE-{caseId || '0001'}
              </Link>
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Customer
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              CUST-2024-00456
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Decision Outcome
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#10B981' }}>
              Release
            </div>
          </div>
          <div className="summary-item" style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div className="summary-label" style={{ fontSize: '12px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Target Date
            </div>
            <div className="summary-value" style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              Aug 25, 2024
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
        <h2 className="card-title" style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '20px', paddingBottom: '12px', borderBottom: '2px solid #E5E7EB' }}>
          Fulfilment Timeline
        </h2>

        <div className="timeline" style={{ position: 'relative', paddingLeft: '40px' }}>
          <div style={{ content: '""', position: 'absolute', left: '15px', top: 0, bottom: 0, width: '2px', background: '#E5E7EB' }} />
          
          {milestones.map((milestone, index) => (
            <div key={milestone.id} className="milestone" style={{ position: 'relative', marginBottom: index < milestones.length - 1 ? '32px' : 0 }}>
              <div className="milestone-marker" style={getMilestoneMarkerStyle(milestone.status)}>
                {milestone.status === 'completed' ? '✓' : milestone.status === 'blocked' ? '!' : index + 1}
              </div>
              <div className="milestone-content" style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', padding: '16px' }}>
                <div className="milestone-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                  <div className="milestone-title" style={{ fontSize: '16px', fontWeight: '700', color: '#111827' }}>
                    {milestone.title}
                  </div>
                  <div className="milestone-status" style={getMilestoneStatusStyle(milestone.status)}>
                    {milestone.status === 'completed' ? 'Completed' : milestone.status === 'in-progress' ? 'In Progress' : milestone.status === 'blocked' ? 'Blocked' : 'Pending'}
                  </div>
                </div>
                <div className="milestone-meta" style={{ display: 'flex', gap: '20px', fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                  <span>Owner: {milestone.owner}</span>
                  <span>•</span>
                  <span>{milestone.status === 'completed' ? 'Completed' : milestone.status === 'blocked' ? 'Updated' : 'Target'}: {milestone.completed}</span>
                </div>
                <div className="milestone-notes" style={{ fontSize: '14px', color: '#111827', lineHeight: '1.6' }}>
                  {milestone.notes}
                </div>
                {milestone.blocker && (
                  <div className="blocker-alert" style={{ background: '#FEF3C7', border: '1px solid #F59E0B', borderRadius: '6px', padding: '12px', marginTop: '12px', display: 'flex', alignItems: 'start', gap: '8px' }}>
                    <div className="blocker-icon" style={{ width: '16px', height: '16px', background: '#F59E0B', borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF', fontWeight: '700', fontSize: '10px' }}>
                      !
                    </div>
                    <div className="blocker-text" style={{ flex: 1, fontSize: '13px', color: '#78350F' }}>
                      <strong>Blocker:</strong> {milestone.blocker}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="update-form" style={{ background: '#FFFFFF', border: '2px solid #E5E7EB', borderRadius: '12px', padding: '24px' }}>
        <h3 className="form-title" style={{ fontSize: '18px', fontWeight: '700', color: '#111827', marginBottom: '20px' }}>
          Update Milestone
        </h3>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            Select Milestone
          </label>
          <select 
            className="form-input"
            value={selectedMilestone}
            onChange={(e) => setSelectedMilestone(e.target.value)}
            style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#F9FAFB' }}
          >
            <option value="">Choose milestone to update...</option>
            <option value="shipment">Shipment Prepared</option>
            <option value="transit">In Transit</option>
            <option value="delivered">Delivered</option>
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            New Status
          </label>
          <select 
            className="form-input"
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            style={{ width: '100%', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#F9FAFB' }}
          >
            <option value="pending">Pending</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="blocked">Blocked</option>
          </select>
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label className="form-label" style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '8px', display: 'block' }}>
            Update Notes
          </label>
          <textarea 
            className="form-input"
            value={updateNotes}
            onChange={(e) => setUpdateNotes(e.target.value)}
            placeholder="Add milestone update notes..."
            style={{ width: '100%', minHeight: '100px', padding: '12px 16px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit', color: '#111827', background: '#F9FAFB', resize: 'vertical' }}
          />
        </div>

        <div className="action-bar" style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button 
            className="btn btn-secondary"
            style={{ height: '48px', padding: '0 24px', border: '1px solid #E5E7EB', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#FFFFFF', color: '#111827' }}
          >
            Cancel
          </button>
          <button 
            onClick={handleSaveUpdate}
            className="btn btn-primary"
            style={{ height: '48px', padding: '0 24px', border: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '600', fontFamily: 'inherit', cursor: 'pointer', background: '#0066CC', color: '#FFFFFF' }}
          >
            Save Update
          </button>
        </div>
      </div>
    </div>
  );
}
