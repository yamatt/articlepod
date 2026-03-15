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
  title string @description("The title of the article.")
  published_date string @description("The published date of the article.")
  summary string @description("A short summary of the article, no more than 50 words.")
  script string @description(#"
    The script to be read by the TTS service. Should be a concise summary of the article, including the title and published date.
  "#)
}

// The function that performs the extraction
function ExtractArticle(url: string) -> ArticleScript {
  client GeminiClient
  prompt #"
    Take this article at the URL and provide me a single person script that I can use use with a TTS service to provide me a maximum 5 minute summary of the provided article.

    Always include the article title, and published date.

    Also provide the title of the article, the date the article was published, and a short summary of the article in 50 words or less as part of the output.

    URL: {{ url }}

    {{ ctx.output_format }}
  "#
}