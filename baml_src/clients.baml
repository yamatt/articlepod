client<llm> GitHubGPT4o-mini {
  provider "openai-generic"
  options {
    base_url "https://models.inference.ai.azure.com"
    api_key  env.GITHUB_TOKEN
    model    "openai/gpt-4o-mini"
  }
}
