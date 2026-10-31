import type { FieldValues, Path, UseFormSetError } from 'react-hook-form'
import { ApiError } from './api'

/**
 * Shows a failed request on the form: server validation messages go next to their fields,
 * and anything else becomes one message at the top.
 */
export function showServerError<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
  fallback = 'Something went wrong. Please try again.',
) {
  if (!(error instanceof ApiError)) {
    setError('root', { message: fallback })
    return
  }
  const fields = Object.entries(error.fieldErrors)
  if (fields.length === 0) {
    setError('root', { message: error.message || fallback })
    return
  }
  for (const [field, message] of fields) {
    setError(field as Path<T>, { message })
  }
}
