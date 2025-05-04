/**
 * Format a number as a currency string
 * @param value Number to format
 * @returns Formatted string with commas
 */
export function formatNumber(value: number | undefined | null): string {
  if (value === undefined || value === null) return 'N/A';
  
  // Format with commas for thousands
  // For large numbers (billions), convert to B
  if (Math.abs(value) >= 1e9) {
    return `${(value / 1e9).toFixed(2)}B`;
  }
  
  // For millions, convert to M
  if (Math.abs(value) >= 1e6) {
    return `${(value / 1e6).toFixed(2)}M`;
  }
  
  // Regular formatting with commas
  return value.toLocaleString('en-US', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0
  });
}

/**
 * Format a number as a percentage
 * @param value Number to format (e.g. 0.25 for 25%)
 * @returns Formatted percentage string
 */
export function formatPercent(value: number | undefined | null): string {
  if (value === undefined || value === null) return 'N/A';
  
  return `${(value * 100).toFixed(2)}%`;
}

/**
 * Format a number as a ratio (e.g. 2.5x)
 * @param value Number to format
 * @returns Formatted ratio string
 */
export function formatRatio(value: number | undefined | null): string {
  if (value === undefined || value === null) return 'N/A';
  
  return `${value.toFixed(2)}x`;
} 