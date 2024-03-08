import { useCallback, useRef } from 'react';

/**
 * Custom hook to create a debounced function.
 * @param functionToDebounce The function to debounce.
 * @param delay The delay in milliseconds.
 * @returns A debounced version of the provided function.
 */
export function useDebouncedFunction<T extends (...args: any[]) => any>(
  functionToDebounce: T,
  delay: number,
): (...args: Parameters<T>) => void {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const debouncedFunction = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        functionToDebounce(...args);
      }, delay);
    },
    [functionToDebounce, delay],
  );

  return debouncedFunction;
}
