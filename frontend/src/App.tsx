import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import type { TabKey } from './components/Navbar';
import { DashboardOverview } from './pages/DashboardOverview';
import { RegressionPage } from './pages/RegressionPage';
import { ClassificationPage } from './pages/ClassificationPage';
import { SpatialSearchPage } from './pages/SpatialSearchPage';
import { RoutingPage } from './pages/RoutingPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Universal Responsive Header */}
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
        {activeTab === 'dashboard' && <DashboardOverview onNavigate={setActiveTab} />}
        {activeTab === 'regression' && <RegressionPage />}
        {activeTab === 'classification' && <ClassificationPage />}
        {activeTab === 'spatial' && <SpatialSearchPage />}
        {activeTab === 'routing' && <RoutingPage />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>
            &copy; {new Date().getFullYear()} AquaGuard AI &bull; AI-Based Groundwater Level Prediction & Geographical Risk Assessment
          </p>
          <p className="text-[11px] text-slate-400">
            Certified Modules: Ragini (Regression) &bull; Sakshi (Classification) &bull; Vedangi (Spatial & Routing)
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;
