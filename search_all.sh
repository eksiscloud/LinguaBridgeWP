#!/bin/bash
# chmod +x search_all.sh

# Settings
SOURCE_URL="https://origina.example.tld"
TRANSLATE_TAG="translate"
# change the path as you like
PYTHON_SCRIPT="/usr/local/bin/translate_and_publish.py"

# Get tag ID
TAG_ID=$(wp term list post_tag --allow-root --format=json --url="$SOURCE_URL" | jq ".[] | select(.name==\"$TRANSLATE_TAG\") | .term_id")

if [ -z "$TAG_ID" ]; then
  echo "Error: tag '$TRANSLATE_TAG' couldn'r be found."
  exit 1
fi

# Get article IDs
POST_IDS=$(wp post list --post_type=post --format=ids --tag_id="$TAG_ID" --url="$SOURCE_URL" --allow-root)

if [ -z "$POST_IDS" ]; then
  echo "No articles with tag '$TRANSLATE_TAG'."
  exit 0
fi

# Loop of articles
for ID in $POST_IDS; do
  echo "Processing article ID: $ID"

  wp post get "$ID" --allow-root --format=json --url="$SOURCE_URL" | "$PYTHON_SCRIPT"

  if [ $? -eq 0 ]; then
    echo "Article ID $ID translated and published."
  else
    echo "Error when processing article ID $ID"
  fi

  echo ""
done
