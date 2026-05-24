const BASE_URL = "http://localhost:8000"

interface RequestOptions {
  method?: string
  body?: unknown
  params?: Record<string, string>
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, params } = options

  let url = `${BASE_URL}${path}`
  if (params) {
    const searchParams = new URLSearchParams(params)
    url += `?${searchParams.toString()}`
  }

  const headers: Record<string, string> = {}
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json"
  }

  const response = await fetch(url, {
    method,
    headers,
    body:
      body instanceof FormData
        ? body
        : body
          ? JSON.stringify(body)
          : undefined,
  })

  if (!response.ok) {
    let detail: string
    try {
      const errorData = await response.json()
      detail = errorData.detail || JSON.stringify(errorData)
    } catch {
      detail = await response.text()
    }
    throw new Error(detail || `Request failed: ${response.status}`)
  }

  if (response.status === 204) return undefined as T

  return response.json()
}
