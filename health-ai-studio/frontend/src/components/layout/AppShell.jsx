import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar, { SidebarToggle } from './Sidebar';
import TopNav from './TopNav';
import ChatWidget from '../ai/ChatWidget';

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen lg:flex">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="min-h-screen flex-1 lg:ml-0">
        <div className="px-4 pt-4 lg:hidden">
          <SidebarToggle onClick={() => setSidebarOpen(true)} />
        </div>
        <TopNav />
        <main className="px-4 py-6 sm:px-6">
          <Outlet />
        </main>
      </div>
      <ChatWidget />
    </div>
  );
}
