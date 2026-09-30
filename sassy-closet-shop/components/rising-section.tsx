"use client";

import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { useQuietRise } from "@/components/use-quiet-rise";

export function RisingSection({
  children,
  className,
  ...rest
}: {
  children: ReactNode;
  className?: string;
} & Omit<ComponentPropsWithoutRef<"section">, "children" | "className">) {
  const ref = useQuietRise<HTMLElement>();
  return (
    <section ref={ref} className={["sc-rise", className].filter(Boolean).join(" ")} {...rest}>
      {children}
    </section>
  );
}
