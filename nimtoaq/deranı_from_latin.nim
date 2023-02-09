# NIM ≥1.6

# COPYRIGHT LICENSE: CC0 version 1.0. For reading a copy of this license, please see the text file ⟪LICENSE⟫ in the top level directory.
# SPDX-License-Identifier: CC0-1.0

# ==================================================================== #
# MODULES

import sugar
from os import nil
from system import quit, io
import sets, tables
import regex, strformat, strutils
from std/sequtils import toSeq, mapIt, all
import unicode
import normalize

from latin import nil

# ==================================================================== #
# PROCS

proc deranı_from_latin*(lt: string, opts: seq[string]): string
proc normalized_re_from_wordset(ws: HashSet[string]): string
proc monograph_map(): Table[string, string]
proc digraph_map(): Table[string, string]
proc add_t2_cartouche(m: RegexMatch, s: string): string
proc add_t1_cartouche(m: RegexMatch, s: string): string
proc utf8_with_replaced_interval(
  s1: string, i: uint, j: uint, s2: string): string
proc utf8_slice_of(s: string, i: uint, j: uint): string
proc traverse_while(
  ℙ1: proc (i: int): bool,
  ℙ2: proc (i: int): bool = ((_: int) => true),
  init: int = 0,
  step: int = 1
): void

# ==================================================================== #
# MAIN

when isMainModule:
  let args = os.commandLineParams()
  assert(args.len >= 1)
  let opts: seq[string] = args[1..^1]
  var s = deranı_from_latin(args[0], opts)
  #write(stdout, s & "\n")
  echo s
  quit()

# ==================================================================== #

proc deranı_from_latin*(
  lt: string, opts: seq[string]
): string {.exportc.} =
  var cartouche_space: string
  if opts.find("compatibility_space") != -1:
    cartouche_space = "󱛛" # Deranı compatibility space (U0F16DB).
  else:
    cartouche_space = " " # Non-breaking space.
  const C = latin.std_consonant_str # Toaq Consonant character
  const V = latin.std_vowel_str # Toaq Vowel
  const L = latin.std_charset # Toaq Letter
  const T = "́̈̂" # Tone marks (◌́, ◌̂, ◌̂)
  const T34 = "̈̂" # Tone 3 & 4 (◌̂, ◌̂)
  const CAA = "́" # Combining Acute Accent
  const CUD = "̣" # Combining Underdot
  const CVD = C & "aeıou" & CUD # Consonant, Vowel, Dot
  const D = "aı|ao|eı|oı" # Diphthong
  const DHM = "󱛍" # Deranı Hiatus mark
  const FTW = fmt"[{C}]?h?[{V}]{CUD}?(?![{T}])[{C & V & CUD}]*"
  # ↑ Falling Tone Word
  let DET: string = normalized_re_from_wordset(latin.determiners)
  let TLP: string = normalized_re_from_wordset(latin.toneless_particles)
  let MS: string = normalized_re_from_wordset(latin.root_subordinators)
  let CONJ: string = normalized_re_from_wordset(latin.conjunctions)
  const SSA = "\u0086"  # control character: Start Selected Area
  const ESA = "\u0087"  # control character: End Selected Area
  const PU1 = "\u0091"  # control character: Private Use #1
  let RRL = @[  # Rewrite Rule List
    (fmt",(\s*{CONJ}{T}?\s)", r"$1"),
    # ↑ Removing commas preceding conjunctions: the Deranı ⟪󱛔⟫ doesn't appear in this context.
    (fmt"(^|[^{L}{T}])([{V}][{T}]?(s|f|c|g|b))", "$1'$2"),
    # ↑ Adding glottal stop marks ⟪'⟫ to certain word-initial vowels.
    (fmt"([{C}]?h?[{V}][{CUD}]?[{CAA}][{CVD}]*)", "\eadd_t2_cartouche"),
    # ↑ Adding cartouches to suitable ⟪◌́ ⟫-toned words.
    (fmt"(?<![{L}])({DET}),?([^{L}]+|$)", fmt"$1{SSA}$2{ESA}"),
    (fmt"{SSA}([^{ESA}]+){ESA}({FTW})?", "\eadd_t1_cartouche"),
    # ↑ Adding empty cartouches and falling-tone word cartouches.
    (fmt"(?<![{L}])(mı́|shú)([^{L}]+)((?!({TLP})([^{L}]|$)){FTW})(?![{L}])",
     fmt"󱛘$1{SSA}$2{ESA}󱛓$3󱛓󱛙"),
    (fmt"(?<![{L}])(mı|shu)([{T34}]?)([^{L}{T}]+)" &
     fmt"((?!({TLP})([^{L}]|$)){FTW})(?![{L}])",
     fmt"$1$2{SSA}$3{ESA}󱛓$4󱛓"),
    # ↑ Adding cartouches and name marks on MI and SHU phrases.
    (SSA & "(.*)" & ESA, "\eadd_deranı_spaces"),
    # ↑ Cartouches containing more than one word must use non-breaking spaces (either a standard non-breaking space or a Deranı compatibility space, as specified by the argument ⟦cartouche_space⟧).
    (fmt"(?<![{L}])(mo[{T}]?)([^{L}{T}]+)", "$1 󱛓$2"),
    (fmt"([^{L}]+)(teo)(?![{L}])", "$1󱛓 $2"),
    # ↑ Adding quote marks in MO—TEO quotes.
    (fmt"{PU1}([{L}]+)", "󱛓$1󱛓"),
    (fmt"[:‹]([{L}]+)[›:]", "󱛓$1󱛓"),
    # ↑ Adding quote marks around onomastic predicates.
    # ↑ The PU1 control tag will be prepended by this program to target onomastic predicates, before this rewrite rule is applied.
    (fmt"̣([́̂{CUD}]?[{V}]?[mq]?)([{C}])", "$1󱛒$2"),
    # ↑ Adding prefix-root delineators ⟪󱛒⟫.
    (fmt"(?!({D}))([{V}])([{V}])", fmt"$2{DHM}$3"),
    # ↑ Adding hiatus marks to non-diphthong vowel sequences.
    (fmt"(?<=[{L}{T}])(󱛓?󱛙?([\s]󱛚)?)([^,󱛚{L}{T}]+)(e|na|ꝡe|ꝡa)([{T}])(?![{L}])",
     "$1 󱛔$3$4$5"),
    # ↑ Adding ⟪󱛔⟫ in places where commas are not used in the Latin script.
    (fmt" (da)(?![{L}{T}])", " $1 󱛕"),
    (fmt"(?<=[{L}{T}])(?<!mo)(?<!m[{T}]o)([󱛓󱛙]*)([^{L}{T}󱛒]*)(({MS})(?![{L}{T}])|$)",
     "$1 󱛕$2$3"),
    ("󱛕 󱛕", "󱛕"),
    # ↑ Adding assertive sentence end marks.
    (fmt" (ka|ba|nha|doa|ꝡo|dâ|môq)( 󱛕)?(?![{L}{T}])", " $1 󱛖"),
    # ↑ Adding non-assertive non-interrogative sentence end marks.
    (fmt" (móq)( 󱛕)?(?![{L}])", " $1 󱛗"),
    # ↑ Adding interrogative sentence end marks.
    (fmt"([{V}])([{T}])", "$2$1"),
    # ↑ Moving tone marks before the first vowel.
    (fmt"([{V}])m(?![{V}])", "$1󱚱"),
    # ↑ Mapping coda ⟪m⟫ to the dedicated Deranı glyph.
    (fmt"[:;.…?!‹›{PU1}]", "")
    # ↑ Removing needless Latin punctuation.
  ]
  # ==== #
  var r = toNfd(lt)
  r = regex.replace(r, re"(?<![A-Za-zı])([A-Z])", PU1 & "$1")
  var s = fmt(r"(^|([.…?!]|mo[{T}])\s+)")
  r = regex.replace(r, re(s & PU1), "$1")
  r = toLower(r)
  r = strutils.replace(r, "i", "ı")
  # Applying the rewrite rules:
  var callback_named = @[
    ("add_t2_cartouche", (m: RegexMatch, s: string) {.closure.} => add_t2_cartouche(m, s)),
    ("add_t1_cartouche", (m: RegexMatch, s: string) {.closure.} => add_t1_cartouche(m, s)),
    ("add_deranı_spaces", (
      ((m: RegexMatch, s: string) => regex.replace(
        s[m.captures[0][0]], re(r"\s"), cartouche_space))
    ))].toTable
  proc f(i: int): bool = # Body for the forthcoming loop.
    var rr = RRL[i]
    if rr[1].len > 0 and rr[1][0] == '\e':
      let cb = callback_named[rr[1][1..^1]]
      r = regex.replace(r, re(rr[0]), cb)
    else:
      r = regex.replace(r, re(rr[0]), rr[1])
    return true
  traverse_while((i: int) => (i < RRL.len), f)
  proc g(i: int): bool = # Body for the forthcoming loop.
    # Mapping digraphs and monographs to Deranı glyphs:
    for (m, l) in @[(digraph_map(), 2), (monograph_map(), 1)]:
      var rl = cast[uint](min(l, runeLen(r) - i))
      let ui = cast[uint](i)
      var s = utf8_slice_of(r, ui, ui + rl)
      if m.hasKey(s):
        let v = m[s]
        r = utf8_with_replaced_interval(
          r, ui, ui + cast[uint](runeLen(s)), v)
    return true
  traverse_while((i: int) => (i < runeLen(r)), g)
  return r

# ==================================================================== #

proc traverse_while(
  ℙ1: proc (i: int): bool,
  ℙ2: proc (i: int): bool = ((_: int) => true),
  init: int = 0,
  step: int = 1
): void =
  # Homologuous to a C-language “for” loop.
  # The index initialization and incrementation are kept in one place, away from the body of the loop.
  var i = init
  while ℙ1(i) and ℙ2(i):
    i += step

proc utf8_with_replaced_interval(
  s1: string,
  i: uint,
  j: uint,
  s2: string
): string =
  assert(i < j)
  return utf8_slice_of(s1, 0, i) &
    s2 & utf8_slice_of(s1, j, cast[uint](runeLen(s1)))

proc normalized_re_from_wordset(ws: HashSet[string]): string =
  return strutils.replace(toNfd(toSeq(ws).join(sep = "|")), "i", "ı")

proc NFD_cartoucheless_words(): HashSet[string] =
  return toHashSet(
    (
      latin.pronouns + latin.determiners +
      latin.functors_with_lexical_tone + toHashSet((
        latin.functors_with_grammatical_tone - latin.predicatizers
      ).mapIt(latin.inflected_from_lemma(it, "´")))
    ).mapIt(
      strutils.replace(toNfd(it), "i", "ı")
    )
  )

proc add_t2_cartouche(m: RegexMatch, s: string): string =
  var w = s[m.captures[0][0]]
  if not NFD_cartoucheless_words().contains(w):
    if all(@["hụ́", "hụ́"], (s: string) => not contains(w, s)):
      w = "󱛘" & w & "󱛙"
  return w

proc add_t1_cartouche(m: RegexMatch, s: string): string =
  var α = s[m.captures[0][0]]
  var β: string
  if m.captures.len >= 1 and m.captures[1].len >= 1:
    β = s[m.captures[1][0]]
  else:
    β = ""
  var r: string
  if α == "":
    r = " 󱛚"
  else:
    α = regex.replace(α, re(r"\s"), " ")
    # ↑ Replacing spaces with non-breaking spaces.
    if β == "":
      r = α & "󱛚 "
    elif latin.toneless_particles.contains(β):
      r = α & "󱛚 " & β
    else:
      r = fmt" 󱛘{β}󱛙"
  return r

# ==================================================================== #

proc monograph_map(): Table[string, string] =
  return {
    "m": "󱚰",
    "b": "󱚲",
    "u": "󱚲",
    "p": "󱚳",
    "f": "󱚴",
    "e": "󱚴",
    "n": "󱚵",
    "d": "󱚶",
    "t": "󱚷",
    "z": "󱚸",
    "c": "󱚹",
    "ı": "󱚹",
    "s": "󱚺",
    "a": "󱚺",
    "r": "󱚻",
    "l": "󱚼",
    "j": "󱚾",
    "ꝡ": "󱛁",
    "q": "󱛂",
    "g": "󱛃",
    "o": "󱛃",
    "k": "󱛄",
    "ʼ": "󱛅",
    "'": "󱛅",
    "h": "󱛆",
    "́": "󱛊",
    "̈": "󱛋",
    "̂": "󱛌",
    "-": "󱛒",
  #  "̣": "󱛒",
    ":": "󱛓",
    ",": " 󱛔"
  }.toTable

proc digraph_map(): Table[string, string] =
  return {
    "nh": "󱚽",
    "ch": "󱚿",
    "sh": "󱛀",
    "aı": "󱚺󱛎󱚹",
    "ao": "󱚺󱛎󱛃",
    "oı": "󱛃󱛎󱚹",
    "eı": "󱚴󱛎󱚹",
    "[]": "󱛚"
  }.toTable

# ==================================================================== #

iterator utf8_iter(s: string): string =
  ## Yield successive UTF-8 characters from string ⟦s⟧.
  var r: string
  var i = 0
  for b in s:
    r.add b
    i += 1
    if r.validateUtf8() == -1:
      yield r
      r.setLen(0)
    elif r.len >= 4:
      raise newException(
        ValueError, fmt"Invalid UTF8 byte sequence: ⟪{r.toHex()}⟫")
    
proc utf8_slice_of(s: string, i: uint, j: uint): string =
  let l = cast[uint](runeLen(s))
  assert(i <= l)
  assert(j <= l)
  assert(i <= j)
  var k: uint = 0
  var r: string = ""
  for cp in utf8_iter(s):
    if k < j:
      if k >= i:
        r &= cp
    else:
      break
    k += 1
  return r

