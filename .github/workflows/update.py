name: Update Movie Data

on:
  schedule:
    - cron: '0 */2 * * *'
  workflow_dispatch: 

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4 
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: |
          pip install cloudscraper beautifulsoup4

      - name: Run Scraper
        run: python app.py

      - name: Commit and Push
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
           

          git add output*.json
           

          git commit -m "Auto Update: $(date)" || exit 0
           
          git pull --rebase origin main
           
          git push origin main
