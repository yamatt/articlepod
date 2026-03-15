function GeneratePodcastAudio(script: string) -> string {
  client GeminiTTS
  prompt #"
    A concise, clear podcast narrator:

    {{ script }}
  "#
}