import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Calendar } from "@/components/ui/calendar";
import { Calendar as CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { MultiSelect } from "@/components/ui/multi-select";
import { api } from "@/services/api";

export interface FiltersState {
  categories: string[];
  source: string;
  dateRange: {
    start: string;
    end: string;
  };
}

interface FilterPanelProps {
  onApplyFilters: (filters: FiltersState) => void;
  isLoading: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ onApplyFilters, isLoading }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [datePickerOpen, setDatePickerOpen] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [source, setSource] = useState<string>("any");
  
  const [startDate, setStartDate] = useState<Date>(new Date('2024-01-01'));
  const [endDate, setEndDate] = useState<Date>(new Date('2025-01-30'));

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.getCategories();
        setCategories(response);
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };
    fetchCategories();
  }, []);

  const handleCategoryChange = (values: string[]) => {
    setSelectedCategories(values);
  };

  const handleDatePresetClick = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - days);
    
    setStartDate(start);
    setEndDate(end);
    setDatePickerOpen(false);
  };

  const handleApplyFilters = () => {
    onApplyFilters({
      categories: selectedCategories,
      source: source,
      dateRange: {
        start: format(startDate, "yyyy-MM-dd"),
        end: format(endDate, "yyyy-MM-dd"),
      },
    });
  };

  return (
    <div className={cn("border rounded-xl shadow-sm bg-card p-4", isOpen ? "" : "w-min")}>
      {isOpen ? (
        <>
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Filters</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="text-muted-foreground"
            >
              ←
            </Button>
          </div>

          <div className="space-y-6">
            {/* Categories */}
            <div className="space-y-2">
              <Label htmlFor="categories">Categories</Label>
              <MultiSelect
                id="categories"
                options={categories.map(cat => ({ label: cat, value: cat }))}
                value={selectedCategories}
                onChange={handleCategoryChange}
                placeholder="Select categories"
                className="w-full"
              />
            </div>

            {/* Source */}
            <div className="space-y-2">
              <Label>Source</Label>
              <RadioGroup
                defaultValue="any"
                value={source}
                onValueChange={setSource}
                className="flex flex-col space-y-1"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="any" id="any" />
                  <Label htmlFor="any">Any</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="livechat" id="livechat" />
                  <Label htmlFor="livechat">LiveChat</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="telegram" id="telegram" />
                  <Label htmlFor="telegram">Telegram</Label>
                </div>
              </RadioGroup>
            </div>

            {/* Date Range */}
            <div className="space-y-2">
              <Label>Date Range</Label>
              <Popover open={datePickerOpen} onOpenChange={setDatePickerOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {startDate && endDate ? (
                      <>
                        {format(startDate, "MMM d, yyyy")} -{" "}
                        {format(endDate, "MMM d, yyyy")}
                      </>
                    ) : (
                      <span>Pick a date range</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <div className="p-3 border-b">
                    <div className="space-y-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => handleDatePresetClick(7)}
                      >
                        Last 7 days
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => handleDatePresetClick(30)}
                      >
                        Last 30 days
                      </Button>
                    </div>
                  </div>
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={startDate}
                    selected={{
                      from: startDate,
                      to: endDate,
                    }}
                    onSelect={(range) => {
                      if (range?.from) setStartDate(range.from);
                      if (range?.to) setEndDate(range.to);
                    }}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Apply Button */}
            <Button
              className="w-full rounded-full"
              onClick={handleApplyFilters}
              disabled={isLoading}
            >
              {isLoading ? "Loading..." : "Run"}
            </Button>
          </div>
        </>
      ) : (
        <Button
          variant="ghost"
          className="p-2 h-auto"
          onClick={() => setIsOpen(true)}
        >
          →
        </Button>
      )}
    </div>
  );
};

export default FilterPanel;
