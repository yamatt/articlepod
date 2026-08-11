client<llm> GeminiFlash {
  provider "google-ai"
  options {
    api_key  env.GEMINI_API_KEY
    model    "gemini-3.5-flash"
  }
}
