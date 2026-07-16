import type { ButtonHTMLAttributes, ReactNode } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  children: ReactNode;
};

const variants = {
  primary: "bg-teal text-white hover:bg-teal/90",
  secondary: "bg-white text-ink border border-line hover:bg-panel",
  ghost: "bg-transparent text-ink hover:bg-panel",
  danger: "bg-red-600 text-white hover:bg-red-700"
};

export function Button({ variant = "primary", className = "", children, ...props }: Props) {
  return (
    <button
      className={`focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
