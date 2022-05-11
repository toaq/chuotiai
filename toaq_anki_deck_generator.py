"""
# HOW TO USE:
This script uses this spreadsheet as a source for sentences and translation: https://docs.google.com/spreadsheets/d/1bCQoaX02ZyaElHiiMcKHFemO4eV1MEYmYloYZgOAhac/edit#gid=0
In order for it to work you must follow this guide to create creds.json file that is used by gspread module: https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
Also you'll need to put a geckoengine in the system's PATH: https://github.com/mozilla/geckodriver/releases
Here is how you might do that: https://www.toolsqa.com/selenium-webdriver/selenium-geckodriver/

After that you put creds.json file next to this file, copy the spreadsheet presented in the first link, put a cells range at the 74th line of this script, and you're basically ready to go.

The script uses this site to pull generated diagrams from: https://toaq-dev.github.io/toaq.org/parser/

The sentences that are failed to be parsed by the parser are put in "bad_sentences.txt" file and not being used in the anki deck.

If you encounter any difficulties you can ask me any questions. You can find me under alias "Xeizzeth" in the toaq discord server: https://discord.gg/qDqDsH9
"""

import base64
import random
import os

import genanki

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

for folder_name in ["images", "bad_phrases"]:
  if not os.path.exists(folder_name):
      os.makedirs(folder_name)

toaq_anki_model = genanki.Model(
  random.randrange(1 << 30, 1 << 31),
  'Toaq Model',
  fields=[
    {'name': 'Toaq'},
    {'name': 'Eng'},
    {"name": 'Parser'}
  ],
  templates=[
    {
      'name': '{{Toaq}}',
      'qfmt': '{{Toaq}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Eng}}<hr id="parser">{{Parser}}',
    },
  ])

toaq_anki_deck = genanki.Deck(
  random.randrange(1 << 30, 1 << 31),
  'Toaq Deck')

url = "https://toaq-dev.github.io/toaq.org/parser/"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

firefox_options = Options()
firefox_options.headless = True

driver = webdriver.Firefox(options=firefox_options)

driver.get(url)

parser_input_form = driver.find_element(by=By.ID, value='i')
parser_result = driver.find_element(by=By.ID, value='parse_result')
parser_canvas = driver.find_element(by=By.CSS_SELECTOR, value="#tree-canvas")

sheet = client.open("Toaq sentences").sheet1
pairs = sheet.get_values("a3:b")

image_paths = list()
bad_phrases = list()

for pair in pairs:
  toaq, eng = pair

  toaq = "".join(x for x in toaq if not x in ["«", "»", "‹", "›", "…", "\""])

  toaq_normalized = "".join(x for x in toaq if x.isalnum())

  parser_input_form.send_keys(toaq)

  parser_input_form.send_keys("\n")

  canvas_base64 = parser_canvas.screenshot_as_base64

  canvas_png = base64.b64decode(canvas_base64)

  if "SyntaxError" in parser_result.text:
    image_path = f"bad_phrases/{toaq_normalized}.png"
    bad_phrases.append(toaq)

    with open(image_path, 'wb') as f:
        f.write(canvas_png)
  else:
    image_path = f"images/{toaq_normalized}.png"
    image_paths.append(image_path)

    with open(image_path, 'wb') as f:
        f.write(canvas_png)

    new_note = genanki.Note(
      model=toaq_anki_model,
      fields=[f'{toaq}', f'{eng}', f'<img src="{toaq_normalized}.png" />'])

    toaq_anki_deck.add_note(new_note)
    

  parser_input_form.clear()


toaq_package = genanki.Package(toaq_anki_deck)
toaq_package.media_files = image_paths

toaq_package.write_to_file('output.apkg')

if bad_phrases:
  with open("bad_phrases.txt", "w", encoding="utf-8") as f:
    for phrase in bad_phrases:
      f.write(f"{phrase}\n")
