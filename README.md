# LinguaBridgeWP

I needed a tool to translate and publish curated content. Multilingual plugins weren't what I needed or wanted. This solution was the closest what I came to.

Remember: **I am not a dev or a coder**

## The process
* Tag articles to translate and publish in other site
* Do `search_all.sh && translate_publish.py`
* Edit normally your translated content and publish

## The requirements
* OpenAI API
* python
* WP CLI
* `apt install jq`
* `pip install openai beautifulsoup4`

Change language parts. It is now from Finnish to English.

## Issues

It hangs after last processed article. ctrl-c helps, but that should be fixed, though.

Put both scripts in the path, I'm using `/usr/local/bin`, and use scripts in the directory of origin WordPress. I should put --url after `wp`, perhaps someday.

I use `wp` as a root. I have that priviledge. Change that part, if/when needed.
