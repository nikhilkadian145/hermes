import { ReactNode } from "react";
import { clsx } from "clsx";

interface SkeletonProps {
  width?: number | string;
  height?: number | string;
  variant?: "text" | "rect" | "circle";
  lines?: number;
  className?: string;
}

export function Skeleton({ width, height, variant = "text", lines = 1, className }: SkeletonProps) {
  const isCircle = variant === "circle";
  
  const content = Array.from({ length: lines }).map((_, i) => (
    <div
      key={i}
      className={clsx(
        "bg-[linear-gradient(90deg,var(--bg-subtle)_25%,var(--bg-overlay)_50%,var(--bg-subtle)_75%)] bg-[length:200%_100%]",
        isCircle ? "rounded-full" : "rounded-[4px]",
        className
      )}
      style={{
        width: width || (variant === "text" ? "100%" : 40),
        height: height || (variant === "text" ? 14 : 40),
        marginBottom: i < lines - 1 ? 8 : 0,
        animation: "shimmer 1.5s infinite"
      }}
    />
  ));

  return (
    <>
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
      {content}
    </>
  );
}
