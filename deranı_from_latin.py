# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: CC0 version 1.0. For reading a copy of this license, please see the text file ⟪LICENSE⟫ in the top level directory.
# SPDX-License-Identifier: CC0-1.0

import sys, unicodedata, re
import pytoaq.latin as pytoaq

# ==================================================================== #

def entrypoint(self_path, latin_toaq):
  assert(isinstance(latin_toaq, str))
  sys.stdout.write(f"{deranı_from_latin(latin_toaq)}\n")
  return

def deranı_from_latin(lt):
  monograph_map = deranı_from_latin.monograph_map
  digraph_map = deranı_from_latin.digraph_map
  C = pytoaq.std_consonant_str # Toaq Consonant character
  V = pytoaq.std_vowel_str # Toaq Vowel
  L = pytoaq.std_charset # Toaq Letter
  T = "́̈̂" # Tone marks (◌́, ◌̂, ◌̂)
  CAA = "́" # Combining Acute Accent
  CUD = "̣" # Combining Underdot
  CVD = C + "aeıou" + CUD # Consonant, Vowel, Dot
  D = "aı|ao|eı|oı" # Diphthong
  DHM = "" # Deranı Hiatus mark
  FTW = f"[{C}]?h?[{V}]{CUD}?(?![{T}])[{C+V+CUD}]*"  # Falling Tone Word
  DET = normalized_re_from_wordset(pytoaq.determiners)
  TLP = normalized_re_from_wordset(pytoaq.toneless_particles)
  MS = normalized_re_from_wordset(pytoaq.matrix_subordinators)
  RRL = (  # Rewrite Rule List
    (f"(^|[^{L}])([{V}][{T}]?({D}|s|f|c|g|b))", r"\1'\2"),
    # ↑ Adding glottal stop marks ⟪'⟫ to certain word-initial vowels.
    (f"[{C}]?h?[{V}][{CUD}]?[{CAA}][{CVD}]*", add_t2_cartouche),
    # ↑ Adding cartouches to suitable ⟪◌́ ⟫-toned words.
    (f"(?<![{L}])({DET})([^{L}]+|$)", r"\1\2"),
    (f"([^])({FTW})?", add_t1_cartouche),
    # ↑ Adding empty cartouches and falling-tone word cartouches.
    (f"(?<![{L}])(mı́|shú)([^{L}]+)([^{L}]*(?!({TLP})([^{L}]|$)){FTW})(?![{L}])",
     r"\1\2\3"),
    (f"(?<![{L}])(mı|shu)([{T}]?[^{L}]+)([^{L}]*(?!({TLP})([^{L}]|$)){FTW})(?![{L}])",
     r"\1\2\3"),
    # ↑ Adding cartouches and name marks on MI and SHU phrases.
    (f"(?<![{L}])(mo[{T}]?)([^{L}]+)", r"\1 \2"),
    (f"([^{L}]+)(teo)(?![{L}])", r"\1 \2"),
    # ↑ Adding quote marks in MO—TEO quotes.
    (f"([{L}]+)", r"\1"),
    (f"[:‹]([{L}]+)[›:]", r"\1"),
    # ↑ Adding quote marks around onomastic predicates.
    # ↑ The ⟪⟫ control tag will be prepended by this program to target onomastic predicates, before this rewrite rule is applied.
    (f"̣([́̂{CUD}]?[{V}]?[mq]?)([{C}])", r"\1\2"),
    # ↑ Adding prefix-root delineators ⟪⟫.
    (f"(?!({D}))([{V}])((?!({D}))[{V}])", r"\2" + DHM + r"\3"),
    # ↑ Adding hiatus marks to non-diphthong vowel sequences.
    (f"(?<=[{L}{T}])(?)([^,{L}{T}]+)(e|na|ꝡe)([{T}])(?![{L}])", r"\1 \2\3\4"),
    # ↑ Adding ⟪⟫ in places where commas are not used in the Latin script.
    (f" (da)(?![{L}])", r" \1 "),
    (f"(?<=[{L}])(?<!mo)(?<!m[{T}]o)([]*)([^{L}]*)(({MS})(?![{L}{T}])|$)", r"\1 \2\3"),
    (" ", ""),
    # ↑ Adding assertive sentence end marks.
    (f" (ka|ba|nha|doa|ꝡo|dâ|môq)(?![{L}{T}])", r" \1 "),
    # ↑ Adding non-assertive non-interrogative sentence end marks.
    (f" (móq)(?![{L}])", r" \1 "),
    # ↑ Adding interrogative sentence end marks.
    (f"([{V}])([{T}])", r"\2\1"),
    # ↑ Moving tone marks before the first vowel.
    (f"([{V}])m", r"\1"),
    # ↑ Mapping coda ⟪m⟫ to the dedicated Deranı glyph.
    ("[.…?!‹›]", "")
    # ↑ Removing needless Latin punctuation.
  )
  # ==== #
  lt = unicodedata.normalize("NFD", lt)
  lt = re.sub("(?<![A-Za-zı])([A-Z])", r"\1", lt)
  lt = re.sub(f"(^|([.…?!]|mo[{T}])\s+)", r"\1", lt)
  lt = lt.lower()
  lt = lt.replace("i", "ı")
  for rr in RRL:  # Applying the rewrite rules.
    lt = re.sub(rr[0], rr[1], lt)
  def f(i): # Body for the forthcoming loop.
    # Mapping digraphs and monographs to Deranı glyphs:
    nonlocal lt
    for (m, l) in ((digraph_map, 2), (monograph_map, 1)):
      l = min(l, len(lt) - i)
      r = m.get(lt[i : i + l])
      if r is not None:
        lt = with_replaced_interval(lt, i, i + l, r)
    return True
  traverse_while(lambda i: i < len(lt), f)
  return lt

def traverse_while(ℙ1, ℙ2 = lambda _: True, init = 0, step = 1):
  # Homologuous to a C-language “for” loop.
  # The index initialization and incrementation are kept in one place, away from the body of the loop.
  i = init
  while ℙ1(i) and ℙ2(i):
    i += step

def with_replaced_interval(s1, i, j, s2):
  assert isinstance(s1, str)
  assert isinstance(s2, str)
  assert isinstance(i, int)
  assert isinstance(j, int)
  assert i < j
  return s2.join([s1[:i], s1[j:]])

def normalized_re_from_wordset(ws):
  return unicodedata.normalize("NFD", "|".join(ws)).replace("i", "ı")

NFD_cartoucheless_words = {
  unicodedata.normalize("NFD", p).replace("i", "ı")
  for p in (
    pytoaq.pronouns | pytoaq.determiners
    | pytoaq.functors_with_lexical_tone
    | {
      pytoaq.inflected_from_lemma(l, "´")
      for l in (
        pytoaq.functors_with_grammatical_tone - pytoaq.predicatizers)
    }
  )
}

def add_t2_cartouche(m):
  w = m.group(0)
  if w not in NFD_cartoucheless_words:
    if all([s not in w for s in ("hụ́", "hụ́")]):
      w = "" + w + ""
  return w

def add_t1_cartouche(m):
  α = m.group(1)
  β = m.group(2)
  if α in ("", None):
    r = " "
  else:
    if β in ("", None):
      r = α + " "
    elif β in pytoaq.toneless_particles:
      r = α + " " + β
    else:
      r = f" {β}"
  return r


# ==================================================================== #

deranı_from_latin.monograph_map = {
  "m": "",
  "b": "",
  "u": "",
  "p": "",
  "f": "",
  "e": "",
  "n": "",
  "d": "",
  "t": "",
  "z": "",
  "c": "",
  "ı": "",
  "s": "",
  "a": "",
  "r": "",
  "l": "",
  "j": "",
  "ꝡ": "",
  "q": "",
  "g": "",
  "o": "",
  "k": "",
  "ʼ": "",
  "'": "",
  "h": "",
  "́": "",
  "̈": "",
  "̂": "",
  "-": "",
#  "̣": "",
  ":": "",
  ",": " ",
#  "[": "",
#  "]": "",
#  ".": " ",
#  ";": " ",
#  "?": " "
}

deranı_from_latin.digraph_map = {
  "nh": "",
  "ch": "",
  "sh": "",
  "aı": "",
  "ao": "",
  "oı": "",
  "eı": "",
  "[]": ""
}

# ==================================================================== #

# === ENTRY POINT === #

entrypoint(*sys.argv)

