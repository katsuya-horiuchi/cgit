#!/usr/bin/env python3

# This script uses Pygments and Python3. You must have both installed
# for this to work.
#
# http://pygments.org/
# http://python.org/
#
# It may be used with the source-filter or repo.source-filter settings
# in cgitrc.
#
# The following environment variables can be used to retrieve the
# configuration of the repository for which this script is called:
# CGIT_REPO_URL        ( = repo.url       setting )
# CGIT_REPO_NAME       ( = repo.name      setting )
# CGIT_REPO_PATH       ( = repo.path      setting )
# CGIT_REPO_OWNER      ( = repo.owner     setting )
# CGIT_REPO_DEFBRANCH  ( = repo.defbranch setting )
# CGIT_REPO_SECTION    ( = section        setting )
# CGIT_REPO_CLONE_URL  ( = repo.clone-url setting )

import io
import os
import subprocess
import sys

import markdown
from pygments import highlight
from pygments.util import ClassNotFound
from pygments.lexers import MarkdownLexer, TextLexer
from pygments.lexers import guess_lexer
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter


sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
data = sys.stdin.read()
filename = sys.argv[1]
formatter = HtmlFormatter(style='pastie', nobackground=True)

try:
    lexer = guess_lexer_for_filename(filename, data)
except ClassNotFound:
    # check if there is any shebang
    if data[0:2] == '#!':
        try:
            lexer = guess_lexer(data)
        except ClassNotFound:
            lexer = TextLexer()
    else:
        lexer = TextLexer()
except TypeError:
    lexer = TextLexer()

if filename[-6:] == '.ipynb':
    cmd = subprocess.Popen(
        'jupyter-nbconvert --stdin --to html --stdout',
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    stdout, _ = cmd.communicate(input=data.encode('utf-8'))
    if stdout:
        sys.stdout.write('''
</code></pre></td></tr></table>
<style>
    .blob { display: none; }
</style>
''')
        sys.stdout.write("<div>")
        sys.stdout.write(stdout.decode('utf-8'))
        sys.stdout.write("</div>")
        sys.stdout.write("<table class='blob'><tr><td><pre><code>")
        sys.exit(0)

if isinstance(lexer, MarkdownLexer):
    sys.stdout.write('''
<!-- close the stuff we want to hide anyway -->
</code></pre></td></tr></table>
<link rel="stylesheet" href="/cgit-rendering.css">
<style>
''')
    sys.stdout.write(HtmlFormatter(style='pastie').get_style_defs('.highlight'))
    sys.stdout.write('''
    </style>
    ''')
    sys.stdout.write("<div class='markdown-body' id='top'>")
    sys.stdout.flush()
    # Note: you may want to run this through bleach for sanitization
    html = markdown.markdown(
        data,
        output_format="html5",
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
            "markdown.extensions.tables",
            "markdown.extensions.toc"
        ],
        extension_configs={
            "markdown.extensions.codehilite":{"css_class":"highlight"}
        }
    )
    sys.stdout.write(html)
    sys.stdout.write("</div>")
    sys.stdout.write("<table class='blob'><tr><td><pre><code>")
else:
    sys.stdout.write('<style>')
    sys.stdout.write(formatter.get_style_defs('.highlight'))
    sys.stdout.write('</style>')
    sys.stdout.write(highlight(data, lexer, formatter, outfile=None))
