import zipfile
from xml.etree import ElementTree as ET
import csv

# parse shared strings
with zipfile.ZipFile('SSIP Project Results.xlsx') as zf:
    shared = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    strings = []
    for si in shared.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        t = si.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
        strings.append(t.text if t is not None else '')

    sheet = ET.fromstring(zf.read('xl/worksheets/sheet2.xml'))

edges = []
for row in sheet.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
    cells = {}
    for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
        col = ''.join(filter(str.isalpha, c.get('r')))
        val = ''
        if c.get('t') == 'inlineStr':
            t = c.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
            if t is not None:
                val = t.text
        else:
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            if v is not None:
                val = strings[int(v.text)] if c.get('t') == 's' else v.text
        cells[col] = val
    sa = (cells.get('A') or '').strip().lstrip('-').lstrip('|').strip()
    sw = (cells.get('D') or '').strip()
    score = (cells.get('E') or '').strip()
    if sa and sw and sa != 'problem_name':
        edges.append((sa, sw, score))

with open('network_edges.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['saudi_entity', 'swedish_entity', 'match_score'])
    writer.writerows(edges)
print('wrote', len(edges), 'edges')
