# -*- coding: utf-8 -*-

# LATIN TOAQ MODULE

# ==================================================================== #

import regex as re, unicodedata

# ==================================================================== #

vowel_str = "aeiıouáéíóúäëïöüâêîôûạẹịı̣ọụạ́ẹ́ị́ọ́ụ́ạ̈ẹ̈ị̈ọ̈ụ̈ậệị̂ộụ̂"
std_vowel_str = "aeıouáéíóúäëïöüâêîôûạẹı̣ọụạ́ẹ́ị́ọ́ụ́ạ̈ẹ̈ị̈ọ̈ụ̈ậệị̂ộụ̂"
vowels = vowel_str
std_vowels = std_vowel_str
consonant_str = "'bcdfghjȷklmnprstzqꝡ"
initial_str = "'bcdfghjȷklmnprstzꝡ"
word_initial_str = "bcdfghjȷklmnprstzꝡ"
std_consonant_str = "'bcdfghjklmnprstzqꝡ"
std_initial_str = "'bcdfghjklmnprstzꝡ"
std_word_initial_str = "bcdfghjklmnprstzꝡ"
charset = vowel_str + consonant_str
std_charset = std_vowel_str + std_consonant_str

initials = ("m", "b", "p", "f", "n", "d", "t", "z", "c", "s", "r", "l", "nh", "j", "ȷ", "ch", "sh", "ꝡ", "g", "k", "'", "h")
finals = ("m", "q")
consonants = initials + ("q",)
std_initials = ("m", "b", "p", "f", "n", "d", "t", "z", "c", "s", "r", "l", "nh", "j", "ch", "sh", "ꝡ", "g", "k", "'", "h")
std_consonants = std_initials + ("q",)

# ==================================================================== #

matrix_subordinators = {"ꝡa", "ma", "tıo"}
nominal_subordinators = {"ꝡä", "mä", "tïo", "lä", "ꝡé", "ná"}
adnominal_subordinators = {"ꝡë", "jü"}
predicatizers = {"jeı", "mea", "po"}
determiners = {"ló", "ké", "sá", "sía", "tú", "túq", "báq", "já", "hí", "ní", "hú"}
conjunctions = {"róı", "rú", "rá", "ró", "rí", "kéo"}
falling_tone_illocutions = {"ka", "da", "ba", "nha", "doa", "ꝡo"}
peaking_tone_illocutions = {"dâ", "môq"}
raising_tone_illocutions = {"móq"}
illocutions = (
  falling_tone_illocutions | raising_tone_illocutions
  | peaking_tone_illocutions)
focus_markers = {"kú", "tóu", "béı"}
preverbals = {"bï", "nä"}
vocative = {"hóı"}
terminators = {"teo", "kı"}
exophoric_pronouns = {
  "jí", "súq", "nháo", "súna", "nhána", "úmo", "íme", "súho", "áma", "há"
}
endophoric_pronouns = {"hó", "máq", "tá", "hóq", "róu", "zé", "bóu", "áq", "chéq"}
pronouns = exophoric_pronouns | endophoric_pronouns

matrix_subordinators = (
  matrix_subordinators | falling_tone_illocutions | terminators)

functors_with_grammatical_tone = predicatizers | {"mı", "shu", "mo"}

functors_with_lexical_tone = (
  matrix_subordinators | nominal_subordinators | adnominal_subordinators
  | determiners | conjunctions | illocutions | focus_markers
  | preverbals | vocative | terminators | {"gö", "kïo"})

functor_lemmas = (
  functors_with_grammatical_tone | functors_with_lexical_tone)

toneless_particles = (
  matrix_subordinators | falling_tone_illocutions | terminators)

interjections = {
  'm̄', 'ḿ', 'm̈', 'm̉', 'm̂', 'm̀', 'm̃'
}

# ==================================================================== #

def is_a_word(s):
  raise NotImplementedError()

def _with_replaced_characters(str, src_chars, rep_chars):
  i = 0
  while i < len(str):
    if str[i] in src_chars:
      str = str[:i] + rep_chars[src_chars.index(str[i])] + str[i+1:]
    i += 1
  return str

def diacriticless_normalized(s):
  s = s.lower()
  s = re.sub("[x’]", "'", s)
  s = re.sub("(?<=^)'", "", s)
  s = unicodedata.normalize("NFD", s)
  #s = re.sub("[^0-9A-Za-zı\u0300-\u030f'_ ()«»,;.…!?]+", " ", s)
  s = re.sub("[^0-9A-Za-zı'_ ()«»,;.…!?]+", "", s)
  s = unicodedata.normalize("NFC", s)
  s = re.sub("i", "ı", s)
  s = re.sub("ȷ", "j", s)
  return s.strip()
  
def lemma_of(s):
  return diacriticless_normalized(s)

def normalized(s):
  assert isinstance(s, str)
  if s == "":
    return s
  # Normalizing nonstandard characters:
  s = s.strip()
  s = re.sub("[x’]", "'", s)
  s = re.sub("i", "ı", s)
  s = re.sub("ȷ", "j", s)
  s = re.sub("(?<=^)'", "", s)
  s = unicodedata.normalize("NFC", s)
  if None == re.search(
    "[\sáéíóúäëïöüâêîôû]", s, re.IGNORECASE
  ):
    # The input is a lemma.
    s = s[0] + s[1:].lower()
    s = unicodedata.normalize("NFC", s)
  else:
    # The input is a normal Toaq text or fragment (not a lemma form).
    s = re.sub("[\t ]+", " ", s)
    # Currently incorrect capitalization is not corrected.
    p = ( "\\b" )
    l = re.split(p, s)
    def f(w):
      p = "^(?:[" + std_initial_str + "]h?)?([" + std_vowel_str + "])"
      r = re.findall(p, w, re.IGNORECASE)
      if r != []:
        main_vowel_pos = w.index(r[0])
        bare = _with_replaced_characters(
          w,
          "áéíóúäëïöüâêîôû",
          "aeıouaeıouaeıou")
        if bare in toneless_particles:
          return bare
        elif bare in functors_with_grammatical_tone:
          pass
        v = w[main_vowel_pos]
        w = bare[:main_vowel_pos] + v + bare[main_vowel_pos + 1:]
      return w
    i = 1
    while i < len(l):
      l[i] = f(l[i])
      i += 2
    s = "".join(l)
  return s

def is_an_inflected_contentive(s):
  return None != re.match(
    ( f"([{std_consonant_str}]h?)?"
    + f"[{std_vowel_str}]"
    + f"[aeıou]*[mq]?(([{std_consonant_str}]h?)[aeıouạẹı̣ọụ]+[mq]?)*$" ),
    s)

def is_a_contentive_lemma(s):
  return None != re.match(
    ( f"([{std_word_initial_str}]h?)?[aeıouạẹı̣ọụ]+[mq]?"
    + f"(([{std_consonant_str}]h?)[aeıouạẹı̣ọụ]+[mq]?)*$" ),
    s)

def is_a_lemma(s):
  return (
    is_a_contentive_lemma(s) or s in (
      toneless_particles | functors_with_lexical_tone | interjections))

def __is_an_interjection(s):
  return None != re.match(
      u"[áéíóúäëïöüâêîôû][aeiıou]*$", s)

# ==================================================================== #

