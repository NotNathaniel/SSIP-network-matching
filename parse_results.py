from __future__ import annotations
import csv
import zipfile
from typing import List, Tuple
from xml.etree import ElementTree as ET


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _load_shared_strings(zf: zipfile.ZipFile) -> List[str]:
    tree = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings: List[str] = []
    for si in tree.findall(f"{NS}si"):
        t = si.find(f".//{NS}t")
        strings.append(t.text if t is not None else "")
    return strings


def extract_edges(xlsx_path: str, sheet_xml: str = "xl/worksheets/sheet2.xml") -> List[Tuple[str, str, float]]:
    """Return a list of edges from the Results worksheet."""
    with zipfile.ZipFile(xlsx_path) as zf:
        strings = _load_shared_strings(zf)
        sheet = ET.fromstring(zf.read(sheet_xml))

    edges: List[Tuple[str, str, float]] = []
    for row in sheet.findall(f".//{NS}row"):
        cells: dict[str, str] = {}
        for c in row.findall(f"{NS}c"):
            col = ''.join(filter(str.isalpha, c.get('r', '')))
            val = ''
            if c.get('t') == 'inlineStr':
                t = c.find(f".//{NS}t")
                if t is not None:
                    val = t.text or ''
            else:
                v = c.find(f"{NS}v")
                if v is not None:
                    val = strings[int(v.text)] if c.get('t') == 's' else v.text or ''
            cells[col] = (val or "").strip()

        sa = cells.get('A', '').lstrip('-').lstrip('|').strip()
        sw = cells.get('D', '').strip()
        score_text = cells.get('E', '').strip()
        try:
            score = float(score_text)
        except ValueError:
            continue
        if sa and sw and sa.lower() != 'problem_name':
            edges.append((sa, sw, score))
    return edges


def write_edges_csv(edges: List[Tuple[str, str, float]], csv_path: str) -> None:
    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(["saudi_entity", "swedish_entity", "match_score"])
        writer.writerows(edges)


if __name__ == "__main__":
    edges = extract_edges('SSIP Project Results.xlsx')
    write_edges_csv(edges, 'network_edges.csv')
    print(f"wrote {len(edges)} edges")
