import { createBrowserRouter, Navigate } from "react-router-dom";

import { DashboardLayout } from "../layouts/DashboardLayout";
import { AnalyticsPage } from "../pages/AnalyticsPage";
import { ApprovalsPage } from "../pages/ApprovalsPage";
import { ConversationsPage } from "../pages/ConversationsPage";
import { LeadsPage } from "../pages/LeadsPage";
import { OpportunitiesPage } from "../pages/OpportunitiesPage";
import { OverviewPage } from "../pages/OverviewPage";
import { ProductsPage } from "../pages/ProductsPage";
import { SimulatorPage } from "../pages/SimulatorPage";
import { SuperadminPage } from "../pages/SuperadminPage";
import { TelegramPage } from "../pages/TelegramPage";
import { TriggersPage } from "../pages/TriggersPage";
import { SignInPage } from "../features/auth/SignInPage";

export const router = createBrowserRouter([
  { path: "/", element: <Navigate to="/signin" replace /> },
  { path: "/signin", element: <SignInPage /> },
  {
    path: "/app",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "telegram", element: <TelegramPage /> },
      { path: "simulator", element: <SimulatorPage /> },
      { path: "opportunities", element: <OpportunitiesPage /> },
      { path: "approvals", element: <ApprovalsPage /> },
      { path: "conversations", element: <ConversationsPage /> },
      { path: "leads", element: <LeadsPage /> },
      { path: "products", element: <ProductsPage /> },
      { path: "triggers", element: <TriggersPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "superadmin", element: <SuperadminPage /> }
    ]
  }
]);
