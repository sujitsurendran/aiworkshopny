/**
 * Main application component with routing.
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './components/auth/LoginPage';
import { RequireAuth } from './components/auth/RequireAuth';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { CaseIntakePage } from './pages/CaseIntakePage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { ApprovalQueuePage } from './pages/ApprovalQueuePage';
import { ApprovalDecisionPage } from './pages/ApprovalDecisionPage';
import { ExceptionQueuePage } from './pages/ExceptionQueuePage';
import { FulfilmentPage } from './pages/FulfilmentPage';
import { ComplaintPage } from './pages/ComplaintPage';
import { RefundPage } from './pages/RefundPage';
import { RenewalPage } from './pages/RenewalPage';

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected routes */}
      <Route
        path="/*"
        element={
          <RequireAuth>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/cases" element={<div>Cases list page placeholder</div>} />
                <Route path="/cases/new" element={<CaseIntakePage />} />
                <Route path="/cases/:caseId" element={<CaseDetailPage />} />
                
                {/* Approval routes */}
                <Route path="/approvals" element={<ApprovalQueuePage />} />
                <Route path="/approvals/:caseId" element={<ApprovalDecisionPage />} />
                <Route path="/exceptions" element={<ExceptionQueuePage />} />
                
                {/* Operational routes */}
                <Route path="/operations/fulfilment/:caseId" element={<FulfilmentPage />} />
                <Route path="/operations/complaints" element={<ComplaintPage />} />
                <Route path="/operations/refunds" element={<RefundPage />} />
                <Route path="/operations/renewals" element={<RenewalPage />} />
                
                <Route path="/operations" element={<div>Operations page placeholder</div>} />
                <Route path="/reports" element={<div>Reports page placeholder</div>} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          </RequireAuth>
        }
      />
    </Routes>
  );
}

export default App;
