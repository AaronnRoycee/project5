from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / 'screenshots'
OUT = Path(__file__).resolve().parent / 'Project5_Report.docx'

doc = Document()
section = doc.sections[0]
section.left_margin = section.right_margin = Inches(0.9)
section.top_margin = section.bottom_margin = Inches(0.8)

base = doc.styles['Normal']
base.font.name = 'Calibri'
base.font.size = Pt(10.5)
base.paragraph_format.space_after = Pt(4)
for name, size in (('Heading 1', 13), ('Heading 2', 11.5)):
    style = doc.styles[name]
    style.font.name = 'Calibri'
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0x9B, 0x22, 0x22)
    style.paragraph_format.space_before = Pt(9)
    style.paragraph_format.space_after = Pt(3)


def para(text='', bold_lead=None, style=None):
    p = doc.add_paragraph(style=style)
    if bold_lead:
        p.add_run(bold_lead).bold = True
    add_rich(p, text)
    return p


def add_rich(p, text):
    parts = text.split('`')
    for i, part in enumerate(parts):
        run = p.add_run(part)
        if i % 2:
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)


def bullet(text, bold_lead=None):
    return para(text, bold_lead, style='List Bullet')


def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(6)
    shade = OxmlElement('w:shd')
    shade.set(qn('w:val'), 'clear')
    shade.set(qn('w:fill'), 'F2F4F7')
    p._p.get_or_add_pPr().append(shade)
    for i, line in enumerate(text.split('\n')):
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        if i < len(text.split('\n')) - 1:
            run.add_break()


def table(rows, widths, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Light Grid Accent 1'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.width = Inches(widths[c])
            cell.text = ''
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            add_rich(p, value)
            for run in p.runs:
                run.font.size = Pt(9)
                if r == 0 and header:
                    run.bold = True
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('CSE 6332 Project 5: Redis Word Counts')
run.bold = True
run.font.size = Pt(16)
sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.add_run('Aaron Pantoja  ·  Fall 2026  ·  https://cse6332-project5.onrender.com/word-chart-app/').font.size = Pt(9.5)

doc.add_heading('1. Implementation: how the counts are stored and read in Redis', level=1)
para('The starter app reads each book in `books/`, counts its words and serves four pages. I completed the five Redis '
     'TODOs in `server.js`. Each book is one Redis hash: the key is `book:{title}:word_counts`, each field is a word, '
     'and each value is that word\u2019s count. A hash fits the data: one key per book, one field per word, and a single '
     'word can be read with `HGET` without loading the whole book.')
table([
    ['TODO', 'Code', 'What it does'],
    ['1  indexBooks()', '`await client.del(redisKey);`\n`await client.hSet(redisKey, wordCounts);`',
     'Deletes the book\u2019s old hash, then writes every word and its count in one HSET command.'],
    ['2  /api/books', '`await client.keys(\'book:*:word_counts\')`',
     'Finds the key of every stored book; the route turns each key into a title.'],
    ['3  /api/book/:title/top/:n', '`await client.hGetAll(redisKey)`',
     'Reads every word and count of one book; the route filters, sorts and returns the top N.'],
    ['4  /api/compare-words', '`Promise.all([client.hKeys(redisKey1), client.hKeys(redisKey2)])`',
     'Reads only the words (not the counts) of both books at the same time to find unique and common words.'],
    ['5  /api/chart-data/:title/:n', '`await client.hGetAll(redisKey)`',
     'Reads every word and count of one book for the chart, as in TODO 3.'],
], [1.45, 2.55, 2.7])
para('Every Redis call returns a promise and is awaited. TODO 4 uses only the field names because comparing books needs the '
     'words, not their counts, so it transfers less data than HGETALL.')
para('', 'Result in Redis. ')
table([
    ['Key (KEYS book:*)', 'Distinct words (HLEN)', 'Example (HGET)'],
    ['`book:Pride_and_Prejudice:word_counts`', '6,942', '`elizabeth` = 645'],
    ['`book:War_and_Peace:word_counts`', '17,581', '`natasha` = 1,213'],
    ['`book:Tarzan_of_the_Apes:word_counts`', '7,534', '`tarzan` = 628'],
], [2.9, 1.6, 2.2])
para('To check the stored data independently, I recounted every book with a separate Python script using the same rules. '
     'Its number of distinct words matched HLEN for all three books exactly, and its count for every word I checked matched HGET.')

doc.add_heading('2. Issues encountered and how I solved them', level=1)
bullet('The professor\u2019s `fetch_books.sh` failed with HTTP 403 for all three books, from my laptop and from the container. '
       'The error page from www.gutenberg.org said \u201cServer unable to read htaccess file,\u201d a fault on their server. '
       'I changed the script to fall back to gutenberg.pglaf.org, the mirror run by the Project Gutenberg Literary Archive '
       'Foundation, which serves the same files; the three books total 4.6 MB as expected.', 'Book download refused. ')
bullet('The counting code matches only the letters a\u2013z, so accented letters split words. War and Peace marks stress on names: '
       '\u201cNat\u00e1sha\u201d was stored as \u201cnat\u201d and \u201csha\u201d, \u201cP\u00e9tya\u201d as \u201ctya\u201d (270 times), '
       'and \u201csha\u201d appeared in the book\u2019s top 20 words while \u201cnatasha\u201d had no count at all. I added one step that '
       'removes accents before matching (`normalize(\'NFD\')` and deleting the combining marks). Now natasha = 1,213, petya = 267, '
       'helene = 165, and \u201csha\u201d is gone. War and Peace went from 17,568 to 17,581 distinct words; the other books changed '
       'by a few words only.', 'Accented words split in two. ')
bullet('Redis in the course container saves to disk (appendonly yes), so a hash survives restarts. Without the DEL in TODO 1, '
       'HSET would update the new words but leave fields that no longer exist. This happened in practice: after the accent fix, '
       'the old fragments such as \u201csha\u201d disappeared only because TODO 1 deletes the key before writing it.',
       'Old counts survive a restart. ')
bullet('The reference site (veritae.org/word-chart-app) returned HTTP 502 while I worked, so I could not compare against it. '
       'The independent Python recount above took its place.', 'Reference site down. ')
bullet('To put the app online I built a Docker image with Node.js, Redis and the books (downloaded at build time), deployed '
       'it on Render, and added a redirect from / to /word-chart-app/. The image uses about 65 MB of memory.',
       'Deployment. ')
bullet('`KEYS` scans every key and blocks Redis while it runs. With three books it is instant, and the assignment asks for it; '
       'with many keys I would use SCAN instead. Curly apostrophes (\u2019) still end a word, so \u201cElizabeth\u2019s\u201d counts '
       'toward \u201celizabeth\u201d; I left this as in the starter.', 'Known limits. ')

doc.add_heading('3. Pages', level=1)
para('I restyled the four pages to match my Project 3 and 4 site (dark theme, navigation bar, red accent). Only the styling '
     'changed; the page scripts and routes are the starter\u2019s.')

shots = [
    ('2-word-counts.png', 'Figure 1. Word Counts: Pride and Prejudice, basic filter (pie: top 5, bar: top 25)', 4.5),
    ('3-unique-comparison.png', 'Figure 2. Unique Word Comparison: Pride and Prejudice vs Tarzan of the Apes', 4.5),
    ('4-word-chart.png', 'Figure 3. Word Charts: War and Peace, top 20, literary filter', 4.5),
    ('1-landing.png', 'Figure 4. Landing page', 4.0),
]
for file, caption, width in shots:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(SHOTS / file), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)

doc.save(OUT)
print(OUT)
