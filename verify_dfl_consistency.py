# -*- coding: utf-8 -*-

# COPYRIGHT LICENSE: CC0 version 1.0. For reading a copy of this license, please see the text file ⟪LICENSE⟫ in the top level directory.
# SPDX-License-Identifier: CC0-1.0

import sys, os, subprocess, time

# ==================================================================== #

SELF_PATH = os.path.dirname(os.path.realpath(__file__))

SENTENCES = (
  "Jadı.",
  "Pujao mıe sá ruaıjoaq shı ꝡë tî tú paq lö gua nä dua há ꝡä duagı hó.",
  "Ꝡa bu chıaq nháo sía, rú du he ꝡä báq nıqdao kı̣raq besụshuı nä hıe nhûq nháo báq hóq pêo río.",
  "Kêo duq nháo sá jua da. Châqtu bîe ꝡä chuq nháo réoqhaq rú râo ꝡä tıshea tóqfua rú tı tó hó, nä duaı tıtua sá lueqche shı cheaq sá hezo haq kı̣shı.",
  "Rú tıe sá máq, rú bu dua júaq lueqche ꝡä heq máq hí. Rû dua sía hezo poq hụ́ꝡa, ju kuı nú ꝡä rúaıjoaq bï, râo tó baq e shea gaq hó, nä jıaınua nháo tíechuo tâoshao hạochuq.",
  "Jé ꝡa râo sá chaq jü râo hóq nä hoaı chıo sä puı rúose, lúeqche jü chum heaq hó háqrıaı, nä moe daosı hó câbıaq ꝡä buaq rıeq hó lä hıe já háqrıaı fâ kúa hobo dâ.",
  "Chıaısı tua tıoqpoa hó kíao, nạ́bıe geanua hó tíechuo, nạ́bıe gaı hó ꝡä reaq sá nuru bao shı háqrıaı.",
  "Ꝡa bôı kaqgaı núru, bû bota hụ́bıe, nä pua noqmıeq nháo hó châ ꝡä toenua nháo sá hea nuı rú tua nıe nháo máq búq aqbo da.",
  "Râo ꝡä fuo máq léq nhaobo, nä boı huogaı nháo ꝡä châ jua nä nhea choalaq bộtao báq nuı tîcuao chúao nhaobo.",
  "Ꝡa fa ru huosı nháo. Nạ́bıe sho gaı nháo ꝡä cheo choadeoq kú sa shuao puq, rú do raqdua hó chéq tú ꝡë shıu kaqgaı hó hóa tî dúeq rá múaoguaq.",
  "Tîu ca ꝡä chuq nháo núru, ꝡä deq muıdua nháo báq zu bẹnıaı."
  "Fao da."
)

# ==================================================================== #

def run(cmd):
   return (
     subprocess.run(cmd, capture_output=True, shell=True)
     .stdout.decode('utf-8')
   )

N = 1

def proceed():
  def f(s):
    return s.replace("\n", "␤")
  for s in SENTENCES:
    print(f"◉ ⟪{s}⟫")
    t1 = time.time()
    for i in range(0, N):
      po = (run(f'python3 {SELF_PATH}/pytoaq/deranı_from_latin.py "{s}"'))
    t2 = time.time()
    for i in range(0, N):
      jo = (run(f'node {SELF_PATH}/nimtoaq/deranı_from_latin.js "{s}"'))
    t3 = time.time()
    for i in range(0, N):
      no = (run(f'{SELF_PATH}/nimtoaq/deranı_from_latin "{s}"'))
    t4 = time.time()
    if po == no and po == jo:
      print(f"→ ⟪{f(po)}⟫")
    else:
      print(f"P ⟪{f(po)}⟫")
      print(f"J ⟪{f(jo)}⟫")
      print(f"N ⟪{f(no)}⟫")
    print("⧖ Py:  {:.6f}s | JS-Nim: {:.6f}s | Nim: {:.6f}s".format(
      (t2 - t1) / N, (t3 - t2) / N, (t4 - t3) / N))
    print("—-—-—-—")
  return

# ==================================================================== #

# === ENTRY POINT === #

if __name__ == "__main__":
  proceed()

