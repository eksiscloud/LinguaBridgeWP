#!/usr/bin/env python3
# chmod +x translate_publish.py
import json
import subprocess
import sys
from openai import OpenAI
from bs4 import BeautifulSoup

# --- ASETUKSET ---
SOURCE_DOMAIN = "original.example.tld"
SOURCE_URL = "https://original.example.tld"
TARGET_URL = "https://translated.example.tld"
TARGET_PATH = "/var/www/translated.example.tld/public_html"
OPENAI_API_KEY = "sk-proj-something"

client = OpenAI(api_key=OPENAI_API_KEY)

# --- HTML preprocessing ---
def strip_internal_links(html, domain=SOURCE_DOMAIN):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if domain in href:
            a.unwrap()
    return str(soup)

# --- Title needs different prompting ---
def translate_title(title):
    prompt = f"Translate the following blog post title from Finnish to fluent English:\n\n{title}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# --- Article, keeping HTML-structure ---
def translate_html_with_gpt(html):
    prompt = f"""
Translate the following Finnish blog article into fluent English. Keep the HTML structure intact.
Do not add any introductions or commentary. Only return the translated content.
Remove all internal links but preserve the visible text.

Finnish content:
{html}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# --- Publishing to translated.example.tld using WP-CLI ---
def create_post(title, content):
    cmd = [
        "wp", "--allow-root",
        f"--path={TARGET_PATH}",
        f"--url={TARGET_URL}",
        "post", "create",
        "--post_type=post",
        "--post_status=draft",
        "--user=<give_username>",
        f"--post_title={title}",
        f"--post_content={content}"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(result.stdout.strip())
        return True
    else:
        print("Error when publishing:", result.stderr.strip(), file=sys.stderr)
        return False

# --- Add 'translated' tag to original, and removing 'translate' ---
def tag_original_post(post_id):
    cmds = [
        ["wp", "--allow-root", "--url=" + SOURCE_URL, "post", "term", "add", str(post_id), "post_tag", "translated"],
        ["wp", "--allow-root", "--url=" + SOURCE_URL, "post", "term", "remove", str(post_id), "post_tag", "translate"]
    ]
    for cmd in cmds:
        subprocess.run(cmd)
   #cmd = [
   #     "wp", "--allow-root",
   #     "--url=" + SOURCE_URL,
   #     "post", "term", "add", str(post_id), "post_tag", "translated"
   # ]
   # cmd = [
   #     "wp", "--allow-root",
   #     "--url=" + SOURCE_URL,
   #     "post", "term", "remove", str(post_id), "post_tag", "translate"
   # ]

    #subprocess.run(cmd)

# --- Mainprocess ---
def main():
    #raw = sys.stdin.read()
    import fileinput
    raw = "".join(fileinput.input())
    if not raw.strip():
        print("No feed.")
        sys.exit(1)

    post = json.loads(raw)
    post_id = post["ID"]
    title = post["post_title"]
    html = post["post_content"]

    cleaned_html = strip_internal_links(html)
    translated_html = translate_html_with_gpt(cleaned_html)
    translated_title = translate_title(title)

    success = create_post(translated_title, translated_html)
    if success:
        tag_original_post(post_id)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
