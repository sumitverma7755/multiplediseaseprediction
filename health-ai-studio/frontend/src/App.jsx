import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import DashboardPage from './pages/DashboardPage';
import PredictionPage from './pages/PredictionPage';
import PatientsPage from './pages/PatientsPage';
import HistoryPage from './pages/HistoryPage';
import LoginPage from './pages/LoginPage';

const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'screening/:disease', element: <PredictionPage /> },
      { path: 'patients', element: <PatientsPage /> },
      { path: 'history', element: <HistoryPage /> }
    ]
  }
]);

export default function App() {
  return <RouterProvider router={router} />;
}
