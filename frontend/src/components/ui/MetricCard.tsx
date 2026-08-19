/**
 * MetricCard component matching wireframe_dashboard.html metric-card design.
 */

import React from 'react';
import { cn } from '../../lib/utils';

interface MetricCardProps {
  label: string;
  value: string | number;
  trend?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  className?: string;
}

export function MetricCard({ label, value, trend, variant = 'default', className }: MetricCardProps) {
  const valueColorClass = {
    default: 'text-gray-900',
    success: 'text-green-500',
    warning: 'text-orange-500',
    danger: 'text-red-500',
  }[variant];

  return (
    <div className={cn('bg-gray-50 border border-gray-200 rounded-xl p-5', className)}>
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
        {label}
      </div>
      <div className={cn('text-3xl font-bold mb-2', valueColorClass)}>
        {value}
      </div>
      {trend && (
        <div className="text-sm text-gray-500">
          {trend}
        </div>
      )}
    </div>
  );
}
