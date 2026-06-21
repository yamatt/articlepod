client<llm> GitHubGPT4o_mini {
  provider "openai-generic"
  options {
    base_url "https://models.inference.ai.azure.com"
    api_key  env.GITHUB_TOKEN
    model    "gpt-4o-mini"
  }
}
