export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Standard fetch wrapper for HERMES API
 */
export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const baseUrl = "http://localhost:8000/api";
  const url = path.startsWith("http") ? path : `${baseUrl}${path.startsWith("/") ? path : "/" + path}`;

  const headers = new Headers(options?.headers);
  if (!headers.has("Content-Type") && !(options?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      let errorData;
      let errorMessage = response.statusText;
      try {
        errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        errorMessage = await response.text() || errorMessage;
      }

      const error = new ApiError(response.status, errorMessage, errorData);
      
      // Dispatch event for global error handler (for 5xx or specific network errors)
      if (response.status >= 500) {
        window.dispatchEvent(new CustomEvent('hermes:api-error', { 
          detail: { type: 'server_error', message: errorMessage, status: response.status } 
        }));
      }

      throw error;
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    // Attempt to parse JSON
    try {
      return await response.json() as T;
    } catch {
      return (await response.text()) as any as T;
    }

  } catch (err: any) {
    // Network errors (fetch threw entirely)
    if (err.name !== 'ApiError') {
      console.error("Network error:", err);
      window.dispatchEvent(new CustomEvent('hermes:api-error', { 
        detail: { type: 'network_error', message: "Cannot reach HERMES backend. Check that the service is running." } 
      }));
      throw new ApiError(0, "Network connection failed");
    }
    throw err;
  }
}
