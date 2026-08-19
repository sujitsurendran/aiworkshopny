/**
 * Main layout component with header and sidebar.
 */

import React from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <Header />
        <main className="app-main bg-gray-50 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
