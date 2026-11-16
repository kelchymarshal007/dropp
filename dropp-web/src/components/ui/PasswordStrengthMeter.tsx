'use client';
import { useMemo } from 'react';

export function PasswordStrengthMeter({ password }: { password: string }) {
  const strength = useMemo(() => {
    if (!password) return 0;
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    return score;
  }, [password]);

  if (!password) return null;

  const strengthColor = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500'][strength - 1] || 'bg-gray-700';
  const strengthText = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'][strength - 1] || '';

  return (
    <div className="mt-2">
      <div className="h-1 w-full bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-1 rounded-full transition-all duration-300 ${strengthColor}`} style={{ width: `${(strength / 5) * 100}%` }}></div>
      </div>
      <p className={`text-xs mt-1 text-right font-medium ${strengthColor.replace('bg-', 'text-')}`}>{strengthText}</p>
    </div>
  );
}
