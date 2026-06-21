class PodcastScript {
  title string
  script string
}

function GeneratePodcastScript(title: string, content: string) -> PodcastScript {
  client GitHubGPT4o_mini
  prompt #"
Write an engaging solo-host podcast script based on the following article.
Open with a natural conversational intro, cover the key points clearly for
a general audience, and close with a brief sign-off. Aim for 3–5 minutes
when read aloud (450–750 words). Output ONLY the spoken script with no
stage directions or annotations. Begin with a line: TITLE: <episode title>

Article title: {{ title }}

Article content:
{{ content }}
  "#
}