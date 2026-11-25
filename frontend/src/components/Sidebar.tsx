import React from 'react';
import {
  LayoutDashboard,
  Map,
  Droplets,
  Activity,
  MapPin,
  Navigation,
  FileText,
  Info,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Compass,
  X
} from 'lucide-react';

export type TabKey =
  | 'dashboard'
  | 'map'
  | 'regression'
  | 'classification'
  | 'spatial'
  | 'routing'
  | 'reports'
  | 'about';

interface SidebarProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

interface NavItem {
  key: TabKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  tag?: string;
  badge?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  collapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
}) => {
  const primaryNav: NavItem[] = [
    { key: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { key: 'map', label: 'Geo Map', icon: Map, badge: 'GIS' },
  ];

  const intelligenceModules: NavItem[] = [
    { key: 'regression', label: 'Groundwater Prediction', icon: Droplets, tag: 'KNN Regressor' },
    { key: 'classification', label: 'Water Quality Classification', icon: Activity, tag: 'XGBoost · BIS' },
    { key: 'spatial', label: 'Nearest Wells', icon: MapPin, tag: 'KDTree Search' },
    { key: 'routing', label: 'Pune Routing', icon: Navigation, tag: 'OSM Graph' },
  ];

  const documentationNav: NavItem[] = [
    { key: 'reports', label: 'Reports & Audits', icon: FileText },
    { key: 'about', label: 'About & Standards', icon: Info },
  ];

  const renderNavButton = (item: NavItem) => {
    const Icon = item.icon;
    const isActive = activeTab === item.key;

    return (
      <button
        key={item.key}
        onClick={() => {
          onTabChange(item.key);
          onCloseMobile();
        }}
        title={collapsed ? item.label : undefined}
        className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 relative group ${
          isActive
            ? 'bg-[#119B72] text-white shadow-sm shadow-[#119B72]/30 font-semibold'
            : 'text-[#D9F2E6]/85 hover:text-white hover:bg-[#0B4F43]'
        } ${collapsed ? 'justify-center px-2' : ''}`}
      >
        {/* Active Pill Indicator on Left */}
        {isActive && !collapsed && (
          <span className="absolute left-0 top-2 bottom-2 w-1 bg-[#D9F2E6] rounded-r-full" />
        )}

        <Icon className={`w-4 h-4 shrink-0 transition-transform duration-150 ${isActive ? 'text-white' : 'text-[#D9F2E6]/80 group-hover:text-white group-hover:scale-105'}`} />

        {!collapsed && (
          <div className="flex-1 flex items-center justify-between overflow-hidden">
            <span className="truncate tracking-tight">{item.label}</span>
            {item.badge && (
              <span className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded ${
                isActive ? 'bg-[#073B32]/40 text-[#D9F2E6]' : 'bg-[#0B4F43] text-[#D9F2E6]/80'
              }`}>
                {item.badge}
              </span>
            )}
            {item.tag && !item.badge && (
              <span className={`text-[9px] font-normal truncate max-w-[70px] ${
                isActive ? 'text-white/80' : 'text-[#D9F2E6]/60'
              }`}>
                {item.tag}
              </span>
            )}
          </div>
        )}
      </button>
    );
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#073B32] text-white select-none">
      {/* Brand & Header Area */}
      <div className={`p-4 flex items-center ${collapsed ? 'justify-center' : 'justify-between'} border-b border-[#0B4F43]`}>
        <div 
          onClick={() => { onTabChange('dashboard'); onCloseMobile(); }}
          className="flex items-center gap-3 cursor-pointer group"
        >
          {/* Custom Environmental Emblem */}
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#119B72] to-[#0B4F43] border border-[#119B72]/40 flex items-center justify-center shadow-md shadow-black/20 group-hover:scale-105 transition-transform shrink-0">
            <Compass className="w-5 h-5 text-[#EDF8F1]" />
          </div>

          {!collapsed && (
            <div className="overflow-hidden">
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-base tracking-tight text-white">
                  AquaGuard
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-[#119B72]/30 text-[#D9F2E6] border border-[#119B72]/50 px-1.5 py-0.2 rounded">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-[#D9F2E6]/70 truncate tracking-tight font-normal">
                Environmental Intelligence
              </p>
            </div>
          )}
        </div>

        {/* Mobile Close Button */}
        <button
          onClick={onCloseMobile}
          className="md:hidden text-[#D9F2E6]/70 hover:text-white p-1 rounded-lg hover:bg-[#0B4F43]"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {/* Core Navigation */}
        <div className="space-y-1">
          {!collapsed && (
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-[#D9F2E6]/50 mb-1.5">
              Overview
            </p>
          )}
          {primaryNav.map(renderNavButton)}
        </div>

        {/* Intelligence Modules */}
        <div className="space-y-1">
          {!collapsed && (
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-[#D9F2E6]/50 mb-1.5">
              Intelligence Modules
            </p>
          )}
          {intelligenceModules.map(renderNavButton)}
        </div>

        {/* Documentation & Reports */}
        <div className="space-y-1">
          {!collapsed && (
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-[#D9F2E6]/50 mb-1.5">
              Platform & Governance
            </p>
          )}
          {documentationNav.map(renderNavButton)}
        </div>
      </div>

      {/* Environmental Standards Verification Card */}
      {!collapsed && (
        <div className="mx-3 mb-3 p-3 rounded-xl bg-[#0B4F43]/70 border border-[#119B72]/30 text-[11px] text-[#D9F2E6]">
          <div className="flex items-center gap-1.5 font-semibold text-white mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-[#119B72]" />
            <span>BIS IS 10500:2012</span>
          </div>
          <p className="text-[10px] text-[#D9F2E6]/75 leading-relaxed">
            Statutory drinking water benchmarks & CGWB monitoring network verified.
          </p>
        </div>
      )}

      {/* Collapse / Expand Footer Bar (Desktop Only) */}
      <div className="hidden md:flex items-center justify-between p-3 border-t border-[#0B4F43] text-xs text-[#D9F2E6]/70">
        {!collapsed && (
          <span className="text-[11px] font-medium tracking-tight">
            v1.2 &bull; Maharashtra
          </span>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg hover:bg-[#0B4F43] hover:text-white transition-colors text-[#D9F2E6]/80 mx-auto md:mx-0"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Left Sidebar */}
      <aside
        className={`hidden md:block fixed top-0 bottom-0 left-0 z-40 transition-all duration-200 border-r border-[#0B4F43] shadow-lg ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Backdrop & Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div 
            onClick={onCloseMobile}
            className="fixed inset-0 bg-black/50 backdrop-blur-xs transition-opacity" 
          />
          <div className="fixed inset-y-0 left-0 w-72 max-w-[85vw] z-50 shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
