# -*- coding: utf-8 -*-

# USAGE: $ python toadua_en_word_count.py toadua_api_snapshot.json

import sys, json, re, unicodedata

def normalize(s):
  s = unicodedata.normalize('NFD', s)
  s = re.sub(u'i', u'ı', s)
  s = re.sub(u'[x’]', u"'", s)
  s = re.sub(u'[\u0300-\u030f]', u'', s)
  s = re.sub(u"[^0-9A-Za-zı'_ ()]+", u' ', s)
  s = re.sub(u' +', u' ', s)
  return s.strip().lower()

if len(sys.argv) < 2:
  print("Not enough parameters.")
  quit()
else:
  path = sys.argv[1]
  with open(path, "r", encoding="utf8") as file:
    json = json.loads(file.read())
    words = set()
    defs = set()
    upvoted_words = set()
    n_official_words = 0
    n_spreadsheet_words = 0
    #for e in json['results']:
    for e in json:
      if (e['scope'] == 'en' and ' ' not in e['head'].strip()
          and e['user'] not in ['examples', 'countries']):
        is_upvoted = 'vote' in e and e['vote'] > 0
        isnt_downvoted = not ('vote' in e and e['vote'] < 0)
        if e['user'] == 'spreadsheet' and isnt_downvoted:
          n_spreadsheet_words += 1
        if e['user'] == 'official':
          n_official_words += 1
          words.add(normalize(e['head']))
          upvoted_words.add(normalize(e['head']))
          defs.add(e['body'].strip(" .") + u'.')
        elif isnt_downvoted:
          words.add(normalize(e['head']))
          defs.add(e['body'].strip(" .") + u'.')
          if is_upvoted:
            upvoted_words.add(normalize(e['head']))
    print(u"Number of unique words:           " + str(len(words)))
    print(u"Number of unique definitions:     " + str(len(defs)))
    print(u"Number of official words:         " + str(n_official_words))
    print(u"Number of unofficial words:       " + str(len(words)-n_official_words))
    print(u"Number of official/upvoted words: " + str(len(upvoted_words)))
    print(u"Number of spreadsheet words:      " + str(n_spreadsheet_words))

