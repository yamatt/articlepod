client<llm> Ollama {
provider openai-generic
  options {
      base_url "http://localhost:11434/v1"
      model "llama3.2:3b"
      default_role "user" // Most local models prefer the user role
  }
}

retry_policy Constant {
  max_retries 3
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}