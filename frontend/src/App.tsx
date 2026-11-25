import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import type { TabKey } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardOverview } from './pages/DashboardOverview';
import { MapIntelligencePage } from './pages/MapIntelligencePage';
import { RegressionPage } from './pages/RegressionPage';
import { ClassificationPage } from './pages/ClassificationPage';
import { SpatialSearchPage } from './pages/SpatialSearchPage';
import { RoutingPage } from './pages/RoutingPage';
import { ReportsPage } from './pages/ReportsPage';
import { AboutPage } from './pages/AboutPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-[#F8FAF7] text-[#182C25] flex font-sans antialiased">
      {/* Fixed Environmental Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        mobileOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* Main App Container */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-200 ${sidebarCollapsed ? 'md:pl-20' : 'md:pl-64'
          }`}
      >
        {/* Top Header Bar */}
        <Header
          collapsed={sidebarCollapsed}
          onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
          onNavigate={setActiveTab}
        />

        {/* Primary Viewport Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12">
          {activeTab === 'dashboard' && <DashboardOverview onNavigate={setActiveTab} />}
          {activeTab === 'map' && <MapIntelligencePage />}
          {activeTab === 'regression' && <RegressionPage />}
          {activeTab === 'classification' && <ClassificationPage />}
          {activeTab === 'spatial' && <SpatialSearchPage />}
          {activeTab === 'routing' && <RoutingPage />}
          {activeTab === 'reports' && <ReportsPage />}
          {activeTab === 'about' && <AboutPage />}
        </main>

        {/* Clean Environmental Footer */}
        <footer className="bg-white border-t border-[#E3EBE5] py-5 text-xs text-[#718078]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
            <p>
              &copy; {new Date().getFullYear()} AquaGuard AI &bull; Environmental Intelligence &amp; Water Resources Platform
            </p>
            <p className="text-[11px] text-[#718078]">
              CGWB Maharashtra &bull; BIS IS 10500:2012 Certified Modules: Groundwater Regression &bull; Water Potability &bull; Spatial &amp; Road Routing
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default App;
