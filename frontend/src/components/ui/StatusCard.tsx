/**
 * StatusCard component for case status distribution display matching wireframe_dashboard.html.
 */

import React from 'react';
import { cn } from '../../lib/utils';

interface StatusCardProps {
  label: string;
  value: number;
  percentage: number;
  barColor?: string;
  className?: string;
}

export function StatusCard({ label, value, percentage, barColor = '#0066CC', className }: StatusCardProps) {
  return (
    <div className={cn('flex justify-between items-center p-3 bg-white border border-gray-200 rounded-lg', className)}>
      <div className="flex-1">
        <div className="text-sm font-medium text-gray-900 mb-2">
          {label}
        </div>
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full rounded-full" 
            style={{ width: `${percentage}%`, backgroundColor: barColor }}
          />
        </div>
      </div>
      <div className="text-lg font-bold text-gray-900 ml-4">
        {value}
      </div>
    </div>
  );
}
