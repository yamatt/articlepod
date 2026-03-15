// Define the client using the google-ai provider
client<llm> GeminiClient {
  provider google-ai
  options {
    model "gemini-3.1-flash-lite-preview"
    api_key env.GOOGLE_API_KEY
  }
}

// The structure of your article metadata
class ArticleScript {
  script string @description(#"
    The script to be read by the TTS service. Should be a concise summary of the article, including the title and published date.
  "#)
}

// The function that performs the extraction
function ExtractArticle(url: string) -> ArticleScript {
  client GeminiClient
  prompt #"
    Take this article at the URL and provide me a single person script that I can use use with a TTS service to provide me a maximum 5 minute summary of the provided article. Always include the article title, and published date.

    URL: {{ url }}

    {{ ctx.output_format }}
  "#
}