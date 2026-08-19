/**
 * AlertItem component matching wireframe_dashboard.html alert-item design.
 */

import React from 'react';
import { cn } from '../../lib/utils';

interface AlertItemProps {
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  className?: string;
}

export function AlertItem({ title, description, severity, className }: AlertItemProps) {
  const severityStyles = {
    high: 'border-l-red-500 bg-red-50',
    medium: 'border-l-orange-500 bg-orange-50',
    low: 'border-l-blue-500 bg-blue-50',
  };

  return (
    <div className={cn('p-3 bg-white border-l-4 rounded-md', severityStyles[severity], className)}>
      <div className="text-sm font-semibold text-gray-900 mb-1">
        {title}
      </div>
      <div className="text-sm text-gray-600">
        {description}
      </div>
    </div>
  );
}
