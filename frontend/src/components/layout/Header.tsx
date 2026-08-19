/**
 * Top header bar with branding and user menu.
 */

import React from 'react';
import { useAuth } from '../../lib/auth-context';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center px-6">
      <div className="flex items-center justify-between w-full">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">
            Verizon Customer Credit Platform
          </h1>
        </div>

        <nav className="flex items-center space-x-4">
          {user && (
            <>
              <div className="text-sm text-gray-700">
                <span className="font-medium">{user.full_name}</span>
                <span className="text-gray-500 ml-2">({user.roles.join(', ')})</span>
              </div>
              <button
                onClick={logout}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Logout
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
