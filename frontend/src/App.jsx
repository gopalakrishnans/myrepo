import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import SearchResultsPage from './pages/SearchResultsPage';
import ProcedureDetailPage from './pages/ProcedureDetailPage';
import ComparePage from './pages/ComparePage';
import HospitalSearchPage from './pages/HospitalSearchPage';
import EstimatorPage from './pages/EstimatorPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/search" element={<SearchResultsPage />} />
            <Route path="/procedure/:id" element={<ProcedureDetailPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/hospitals" element={<HospitalSearchPage />} />
            <Route path="/estimator" element={<EstimatorPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
