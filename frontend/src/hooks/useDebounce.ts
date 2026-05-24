import { useState, useEffect } from "react"

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(
    function updateDebouncedValue() {
      const timer = setTimeout(function setValue() {
        setDebouncedValue(value)
      }, delay)
      return function clearTimer() {
        clearTimeout(timer)
      }
    },
    [value, delay],
  )

  return debouncedValue
}
