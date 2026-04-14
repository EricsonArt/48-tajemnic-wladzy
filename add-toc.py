"""
Dodaje stronę spisu treści do ebooka 48 Tajemnic Manipulacji.
Wstawia TOC po stronie 2 (Informacje prawne).
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

PDF_IN  = "c:/Users/cosmi/Desktop/AI/Project/48-tajemnic-wladzy/48_Tajemnic_Manipulacji.pdf"
PDF_OUT = "c:/Users/cosmi/Desktop/AI/Project/48-tajemnic-wladzy/48_Tajemnic_Manipulacji.pdf"

W, H = A4  # 595 x 842 pt

# Kolory
BG      = HexColor("#0d0d0d")
ACCENT  = HexColor("#c0392b")
TITLE_C = white
ENTRY_C = HexColor("#e8e8e8")
NUM_C   = HexColor("#888888")
LINE_C  = HexColor("#2a2a2a")

# Wszystkie wpisy TOC: (etykieta, numer strony PDF w oryginalnym dokumencie)
# Po wstawieniu TOC strony przesuną się o 1, ale podajemy oryginalne numery.
ENTRIES = [
    ("WSTĘP",                                                    3),
    ("PRAWO 1  — ZAWSZE MÓW MNIEJ, NIŻ POTRZEBA",               5),
    ("PRAWO 2  — CHROŃ SWOJĄ REPUTACJĘ",                         6),
    ("PRAWO 3  — UKRYWAJ SWOJE INTENCJE",                        7),
    ("PRAWO 4  — ZAWSZE MÓW MNIEJ, NIŻ WIESZ",                  8),
    ("PRAWO 5  — WABIK I PUŁAPKA",                               9),
    ("PRAWO 6  — WYGRYWAJ PRZEZ DZIAŁANIA",                     10),
    ("PRAWO 7  — NAUCZ SIĘ UZALEŻNIAĆ INNYCH OD SIEBIE",       12),
    ("PRAWO 8  — KONTROLUJ OPCJE",                              13),
    ("PRAWO 9  — GRAJ NA FANTAZJACH LUDZI",                     14),
    ("PRAWO 10 — KULT OSOBOWOŚCI",                              15),
    ("PRAWO 11 — OPANUJ SZTUKĘ TIMINGU",                        16),
    ("PRAWO 12 — UŻYWAJ NIEOBECNOŚCI",                          18),
    ("PRAWO 13 — ZARAŹ INNYCH SWOJĄ WIZJĄ",                     20),
    ("PRAWO 14 — TRZYMAJ INNYCH W NAPIĘCIU",                    21),
    ("PRAWO 15 — ZACHOWUJ SIĘ JAK KRÓL",                       22),
    ("PRAWO 16 — POSIADAJ TYLKO TYLE, ILE MOŻESZ OBRONIĆ",     23),
    ("PRAWO 17 — REMODELUJ SIEBIE",                             24),
    ("PRAWO 18 — TWÓRZ SPEKTAKULARNE WRAŻENIA",                 25),
    ("PRAWO 19 — PLANUJ AŻ DO KOŃCA",                           27),
    ("PRAWO 20 — ROZBROIĆ KRYTYKĘ",                             28),
    ("PRAWO 21 — NIE ZOBOWIĄZUJ SIĘ DO NIKOGO",                29),
    ("PRAWO 22 — BĄDŹ AMORFICZNY",                              30),
    ("PRAWO 23 — KONCENTRUJ SWOJE SIŁY",                        31),
    ("PRAWO 24 — WIEDZA BEZ DZIAŁANIA JEST MARTWA",             32),
    ("ZAKOŃCZENIE",                                             34),
    ("O AUTORZE",                                               35),
]


def build_toc_page() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # Tło
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Czerwona kreska dekoracyjna z lewej
    c.setFillColor(ACCENT)
    c.rect(36, 60, 4, H - 120, fill=1, stroke=0)

    # Nagłówek
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(52, H - 64, "48 TAJEMNIC MANIPULACJI")

    c.setFillColor(TITLE_C)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(52, H - 100, "SPIS TREŚCI")

    # Pozioma linia pod nagłówkiem
    c.setStrokeColor(LINE_C)
    c.setLineWidth(1)
    c.line(52, H - 112, W - 52, H - 112)

    # Wpisy
    TOP_Y    = H - 136
    ROW_H    = 22          # wysokość wiersza
    LABEL_X  = 52
    NUM_X    = W - 52
    MAX_ROWS = len(ENTRIES)

    for i, (label, page) in enumerate(ENTRIES):
        y = TOP_Y - i * ROW_H
        if y < 60:
            break

        # Naprzemienne tło co dwa wiersze
        if i % 2 == 0:
            c.setFillColor(HexColor("#151515"))
            c.rect(44, y - 5, W - 88, ROW_H - 2, fill=1, stroke=0)

        # Etykieta
        c.setFillColor(ENTRY_C)
        c.setFont("Helvetica", 10)
        c.drawString(LABEL_X, y + 4, label)

        # Kropki wypełniające
        c.setFillColor(NUM_C)
        c.setFont("Helvetica", 9)
        label_w = c.stringWidth(label, "Helvetica", 10)
        num_str = str(page)
        num_w   = c.stringWidth(num_str, "Helvetica-Bold", 10)
        dot_start = LABEL_X + label_w + 8
        dot_end   = NUM_X   - num_w   - 6
        dot_x = dot_start
        while dot_x < dot_end:
            c.drawString(dot_x, y + 4, ".")
            dot_x += 5

        # Numer strony
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(NUM_X, y + 4, num_str)

    # Stopka
    c.setFillColor(NUM_C)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 40, "© 2024 mindtriki  |  Wszelkie prawa zastrzeżone")

    c.save()
    return buf.getvalue()


def main():
    print("Generuję stronę TOC...")
    toc_bytes = build_toc_page()

    print("Wczytuję oryginalny PDF...")
    reader = PdfReader(PDF_IN)
    writer = PdfWriter()

    toc_reader = PdfReader(io.BytesIO(toc_bytes))
    toc_page   = toc_reader.pages[0]

    # Wstaw strony: 0, 1 (okładka + informacje prawne), TOC, reszta
    for i, page in enumerate(reader.pages):
        writer.add_page(page)
        if i == 1:          # po stronie nr 2 (indeks 1)
            writer.add_page(toc_page)

    print(f"Zapisuję do {PDF_OUT}...")
    with open(PDF_OUT, "wb") as f:
        writer.write(f)

    total = len(reader.pages) + 1
    print(f"Gotowe! PDF ma teraz {total} stron.")


if __name__ == "__main__":
    main()
