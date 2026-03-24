import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';
import { BottomTabBar } from './BottomTabBar';
import { ToastContainer } from '../ui/Toast';

export function AppLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem('hermes-sidebar-collapsed') === 'true';
  });

  const handleToggleCollapse = () => {
    const newVal = !collapsed;
    setCollapsed(newVal);
    localStorage.setItem('hermes-sidebar-collapsed', String(newVal));
  };

  return (
    <div className="min-h-screen bg-bg-base flex flex-col pt-[52px] md:pt-[56px] pb-[64px] md:pb-0 font-sans text-text-primary selection:bg-accent-subtle">
      <TopBar onMenuClick={() => setMobileMenuOpen(true)} />
      
      <div className="flex flex-1 relative w-full h-full min-h-[calc(100vh-56px)]">
        <Sidebar 
          mobileOpen={mobileMenuOpen} 
          onMobileClose={() => setMobileMenuOpen(false)} 
          collapsed={collapsed}
          onToggleCollapse={handleToggleCollapse}
        />
        
        <main 
          className="flex-1 w-full transition-[margin] duration-300 ml-0 md:ml-[60px]"
          style={window.innerWidth >= 768 ? { marginLeft: collapsed ? 60 : 240 } : undefined}
        >
          <div className="w-full max-w-[1280px] mx-auto p-4 md:p-6 pb-24 md:pb-6 relative z-0">
            <Outlet />
          </div>
        </main>
      </div>

      <BottomTabBar />
      <ToastContainer />
    </div>
  );
}
