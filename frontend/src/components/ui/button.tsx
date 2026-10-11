// Customized shadcn/ui button pattern (MIT): https://ui.shadcn.com/docs/components/button
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils";
const variants = cva("button", {
  variants: {
    variant: {
      default: "primary",
      outline: "secondary",
      ghost: "button-ghost",
    },
    size: { default: "", sm: "button-small", icon: "icon-button" },
  },
  defaultVariants: { variant: "default", size: "default" },
});
export type ButtonProps = React.ComponentProps<"button"> &
  VariantProps<typeof variants> & { asChild?: boolean };
export function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : "button";
  return (
    <Component
      data-slot="button"
      className={cn(variants({ variant, size, className }))}
      {...props}
    />
  );
}
