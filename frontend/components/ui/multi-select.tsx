import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

export interface Option {
  value: string;
  label: string;
}

interface MultiSelectProps {
  options: Option[];
  value: string[];
  onChange: (value: string[]) => void;
  className?: string;
}

export function MultiSelect({
  options = [],
  value = [],
  onChange,
  className,
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false);

  const selectedLabels = React.useMemo(() => {
    return value
      .map((v) => options.find((opt) => opt.value === v))
      .filter((opt): opt is Option => opt !== undefined);
  }, [value, options]);

  const handleSelect = (optionValue: string) => {
    const newValue = value.includes(optionValue)
      ? value.filter((v) => v !== optionValue)
      : [...value, optionValue];
    onChange(newValue);
  };

  const handleRemove = (optionValue: string) => {
    onChange(value.filter((v) => v !== optionValue));
  };

  return (
    <div className="relative">
      <Select
        open={open}
        onOpenChange={setOpen}
        value={undefined}
        onValueChange={handleSelect}
      >
        <SelectTrigger className={cn("w-full", className)}>
          <div className="flex flex-wrap gap-1">
            {selectedLabels.length > 0 ? (
              selectedLabels.map((option) => (
                <Badge
                  key={option.value}
                  variant="secondary"
                  className="mr-1"
                >
                  {option.label}
                  <button
                    className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                    onMouseDown={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleRemove(option.value);
                    }}
                  >
                    <X className="h-3 w-3" />
                    <span className="sr-only">Remove</span>
                  </button>
                </Badge>
              ))
            ) : (
              <SelectValue placeholder="Select participants..." />
            )}
          </div>
        </SelectTrigger>
        <SelectContent>
          <ScrollArea className="max-h-[200px]">
            {options.map((option) => (
              <SelectItem
                key={option.value}
                value={option.value}
                className={cn(
                  "cursor-pointer",
                  value.includes(option.value) && "bg-muted"
                )}
              >
                {option.label}
              </SelectItem>
            ))}
          </ScrollArea>
        </SelectContent>
      </Select>
    </div>
  );
} 