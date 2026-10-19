# Article Pod

Article Pod takes a URL and converts it into a podcast.

## Running

Fork this repo.

You will need to provide secrets for Cloudflare R2 to store the audio files and the name of your R2 Bucket.

You will need to configure your Podcast tool to access the RSS feed provided through GitHub Pages.

### Adding Article

1. Go to the Actions page
2. Select the Add Article Workflow
3. Click "Run Workflow"
4. Provide the URL to the article and click "Run"

## How this works

### Articles

The overview is the workflow is provided a URL. It then looks up the content for that URL. A local LLM summarises that into a podcast script. A local Text to Speech model converts that into a WAV which is converted into an MP3, which is stored in Cloudflare R2. The meta-data for the article is stored in GitHub and finally a podcast RSS feed is generated and published via GitHub Pages.
