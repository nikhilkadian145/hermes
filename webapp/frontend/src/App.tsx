import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { Chat } from './pages/Chat';
import GSTReports from './pages/GSTReports';
import { SalesInvoicesPage } from './pages/SalesInvoicesPage';
import { InvoiceDetailPage } from './pages/InvoiceDetailPage';
import { UploadPage } from './pages/UploadPage';
import { PurchaseBillsPage } from './pages/PurchaseBillsPage';
import { BillReviewPage } from './pages/BillReviewPage';
import { FileCenterPage } from './pages/FileCenterPage';
import { ContactsPage } from './pages/ContactsPage';
import { ContactDetailPage } from './pages/ContactDetailPage';
import { PaymentsPage } from './pages/PaymentsPage';
import { ReconciliationPage } from './pages/ReconciliationPage';
import { AccountsPage } from './pages/AccountsPage';
import { MappingRulesPage } from './pages/MappingRulesPage';
import { ReportsHubPage } from './pages/ReportsHubPage';
import { ReportViewerPage } from './pages/ReportViewerPage';
import { AnomaliesPage } from './pages/AnomaliesPage';
import { VendorSpendPage } from './pages/VendorSpendPage';
import { ProcessingQualityPage } from './pages/ProcessingQualityPage';
import { CustomReportBuilderPage } from './pages/CustomReportBuilderPage';
import { AuditPage } from './pages/AuditPage';
import { ImportCenterPage } from './pages/ImportCenterPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { SettingsPage } from './pages/SettingsPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { GlobalErrorHandler } from './components/GlobalErrorHandler';



export function App() {
  return (
    <BrowserRouter>
      <GlobalErrorHandler />
      <Routes>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/invoices">
            <Route index element={<Navigate to="sales" replace />} />
            <Route path="sales" element={<SalesInvoicesPage />} />
            <Route path="sales/:id" element={<InvoiceDetailPage />} />
            <Route path="purchases" element={<PurchaseBillsPage />} />
            <Route path="purchases/review/:id" element={<BillReviewPage />} />
          </Route>
          <Route path="/contacts" element={<ContactsPage />} />
          <Route path="/contacts/:id" element={<ContactDetailPage />} />
          <Route path="/payments">
            <Route index element={<PaymentsPage />} />
            <Route path="reconciliation" element={<ReconciliationPage />} />
          </Route>
          <Route path="/reports">
            <Route index element={<ReportsHubPage />} />
            <Route path="gst" element={<GSTReports />} />
            <Route path="custom" element={<CustomReportBuilderPage />} />
            <Route path="vendor-spend" element={<VendorSpendPage />} />
            <Route path="processing-quality" element={<ProcessingQualityPage />} />
            <Route path=":type" element={<ReportViewerPage />} />
          </Route>
          <Route path="/documents" element={<FileCenterPage />} />
          <Route path="/anomalies" element={<AnomaliesPage />} />
          <Route path="/accounts">
            <Route index element={<AccountsPage />} />
            <Route path="mapping-rules" element={<MappingRulesPage />} />
          </Route>
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/settings/import" element={<ImportCenterPage />} />
          <Route path="/system" element={<SystemHealthPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
