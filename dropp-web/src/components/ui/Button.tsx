import { ButtonHTMLAttributes, ReactNode } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { IconDefinition } from '@fortawesome/fontawesome-svg-core';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  icon?: IconDefinition;
  children: ReactNode;
  isLoading?: boolean;
}

export function Button({ 
  variant = 'primary', 
  icon, 
  children, 
  isLoading, 
  className = '', 
  ...props 
}: ButtonProps) {
  const baseStyles = "w-full flex items-center justify-center gap-2 py-4 px-6 rounded-full font-semibold text-[15px] transition-all active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100";
  
  const variants = {
    primary: "bg-dropp-orange text-white hover:bg-dropp-orange/90 shadow-[0_0_20px_rgba(255,107,0,0.3)]",
    secondary: "bg-surface border border-border text-white hover:bg-card",
    ghost: "bg-transparent text-gray-400 hover:text-white",
    danger: "bg-red-500/10 text-red-500 hover:bg-red-500/20",
  };

  return (
    <button 
      className={`${baseStyles} ${variants[variant]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <span className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        <>
          {icon && <FontAwesomeIcon icon={icon} className="w-4 h-4" />}
          {children}
        </>
      )}
    </button>
  );
}
