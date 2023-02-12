
import sys
from latin import normalized_with_quotes_excluded

for line in sys.stdin:
  s = line.strip()
  try:
    s = normalized_with_quotes_excluded(s)
  except:
    s = s + " ◈◈◈ ERR: " + str(sys.exc_info()[1])
  print(s)
