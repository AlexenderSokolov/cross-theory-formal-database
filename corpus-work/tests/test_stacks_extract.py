import importlib.util
from pathlib import Path
import unittest
import tempfile

P=Path(__file__).parents[1]
def module():
    s=importlib.util.spec_from_file_location('stacks_extract',P/'scripts/stacks_extract.py')
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def source(tmp_path):
    (tmp_path/'tags').mkdir()
    (tmp_path/'tags/tags').write_text('AAAA,one-theorem-good\nBBBB,one-lemma-other\nCCCC,one-theorem-bad\nDDDD,one-situation-base\n')
    (tmp_path/'one.tex').write_text(r'''\begin{situation}
\label{situation-base} Let $R$ be a ring.
\end{situation}
\begin{lemma}
\label{lemma-other} $1=1$.
\end{lemma}
\begin{proof} Reflexivity proves this. \end{proof}
\begin{theorem}
\label{theorem-good} In Situation \ref{situation-base}, $x=x$.
\end{theorem}
\begin{proof}
By Lemma \ref{lemma-other}, and \eqref{eq-local}, we get
\begin{equation}\label{eq-local}x=x.\end{equation}
\end{proof}
\begin{theorem}\label{theorem-bad} $x=x$.\end{theorem}
\begin{proof} Omitted. \end{proof}
''')
    return module().StacksSource(tmp_path)

class Tests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory(); self.source=source(Path(self.tmp.name))
 def tearDown(self):
    self.tmp.cleanup()
 def test_exact_statement_and_proof(self):
    source=self.source
    r=source.extract('AAAA', ['DDDD'])
    self.assertIn(r['statement'],r['excerpt'])
    assert r['proof'].startswith('\\begin{proof}')
    assert '\\label{eq-local}' in r['proof']

 def test_reject_omission(self):
    source=self.source
    with self.assertRaisesRegex(ValueError,'incomplete'): source.extract('CCCC')

 def test_required_situation_context(self):
    source=self.source
    with self.assertRaisesRegex(ValueError,'context'): source.extract('AAAA')

 def test_render_links_preserves_local_reference(self):
    source=self.source
    m=module(); r=source.extract('AAAA',['DDDD'])
    tex=m.render(source,r,{'title':'Identity','difficulty_level':'H1','difficulty_reason':'Author assessment'})
    assert '\\eqref{eq-local}' in tex
    assert 'https://stacks.math.columbia.edu/tag/BBBB' in tex
    assert '\\ref{situation-base}' in tex
    assert 'externaldocument' not in tex

 def test_short_running_title_preserves_full_display_title(self):
    title='A deliberately long theorem title with essential hypotheses and complete scope'
    tex=module().render(self.source,self.source.extract('AAAA',['DDDD']),{'title':title,'difficulty_level':'H2','difficulty_reason':'Assessment'})
    self.assertIn(r'\title[Stacks Project, Tag AAAA]{'+title+'}',tex)
    self.assertIn(r'\begin{proof}',tex)

 def test_difficulty_is_required(self):
    source=self.source
    with self.assertRaisesRegex(ValueError,'difficulty'): module().render(source,source.extract('BBBB'),{'title':'Identity'})

 def test_section_context_extracts_intro_only(self):
    root=self.source.root
    with (root/'tags/tags').open('a') as f: f.write('EEEE,one-section-intro\n')
    s=(root/'one.tex').read_text();(root/'one.tex').write_text('\\section{Context}\n\\label{section-intro}\nLet $R$ be commutative.\n\n'+s)
    src=module().StacksSource(root)
    c=src.extract('BBBB',['one-section-intro'])['contexts'][0]
    self.assertIn('Let $R$ be commutative.',c['excerpt'])
    self.assertNotIn('\\begin{situation}',c['excerpt'])

 def test_equation_context_keeps_intro(self):
    root=self.source.root
    with (root/'tags/tags').open('a') as f: f.write('FFFF,one-equation-context\n')
    s=(root/'one.tex').read_text();(root/'one.tex').write_text('\\noindent\nDefine $a$ by\n\\begin{equation}\n\\label{equation-context}a=1.\n\\end{equation}\n\n'+s)
    c=module().StacksSource(root).extract('BBBB',['FFFF'])['contexts'][0]
    self.assertIn('Define $a$ by',c['excerpt'])
    self.assertIn('a=1.',c['excerpt'])

 def test_original_preamble_class_switch_removed(self):
    (self.source.root/'preamble.tex').write_text('\\IfFileExists{stacks-project.cls}{%\n\\documentclass{stacks-project}\n}{%\n\\documentclass{amsart}\n}\n% For dealing with references\n\\usepackage{hyperref}\n')
    t=module().render(self.source,self.source.extract('BBBB'),{'difficulty_level':'H1','difficulty_reason':'Assessment'})
    self.assertEqual(t.count('\\documentclass'),1)
    self.assertNotIn('IfFileExists',t)

 def test_remark_context(self):
    root=self.source.root
    with (root/'tags/tags').open('a') as f: f.write('GGGG,one-remark-context\n')
    with (root/'one.tex').open('a') as f: f.write('\\begin{remark}\\label{remark-context}Notation is fixed.\\end{remark}')
    c=module().StacksSource(root).extract('BBBB',['GGGG'])['contexts'][0]
    self.assertEqual(c['kind'],'remark')

 def test_item_context_includes_setup_and_complete_enumerate(self):
    root=self.source.root
    with (root/'tags/tags').open('a') as f: f.write('HHHH,one-item-setup\n')
    s=(root/'one.tex').read_text();s=s.replace('\\begin{lemma}','\\noindent\nLet $a$ be fixed.\n\\begin{enumerate}\\item\\label{item-setup}$a=1$.\\end{enumerate}\n\n\\begin{lemma}',1);(root/'one.tex').write_text(s)
    c=module().StacksSource(root).extract('BBBB',['HHHH','DDDD'])['contexts'][0]
    self.assertIn('Let $a$ be fixed.',c['excerpt'])
    self.assertIn('\\end{enumerate}',c['excerpt'])
    self.assertNotIn('\\begin{lemma}',c['excerpt'])

 def test_real_upstream_preamble_only_one_documentclass(self):
    src=module().StacksSource(P/'corpus/raw/stacks-project')
    t=module().render(src,src.extract('08YA'),{'difficulty_level':'H2','difficulty_reason':'Screened classification proof'})
    self.assertEqual(t.count('\\documentclass'),1)
    self.assertTrue(t.startswith('\\documentclass{amsart}\n%'))
    self.assertNotIn('externaldocument',t)
    self.assertNotIn('xr-hyper',t)

 def test_partial_omission_phrases_fail_closed(self):
    m=module()
    for phrase in ['We omit the proof of the converse.', 'The reader verifies the cocycle condition.', 'The reader shows that this map is an inverse.', 'We leave the compatibility check to the reader.']:
        self.assertTrue(m.proof_flags('\\begin{proof}'+phrase+'\\end{proof}'),phrase)

 def test_all_consecutive_author_proofs_retained(self):
    root=self.source.root;s=(root/'one.tex').read_text();s=s.replace('\\begin{proof} Reflexivity proves this. \\end{proof}','\\begin{proof} Reflexivity proves this. \\end{proof}\n\n\\begin{proof}[Second proof] Equality gives the conclusion. \\end{proof}');(root/'one.tex').write_text(s)
    r=module().StacksSource(root).extract('BBBB')
    self.assertEqual(r['proof'].count('\\begin{proof}'),2)

 def test_bounded_omission_exception_preserves_author_text(self):
    root=self.source.root;s=(root/'one.tex').read_text().replace('Reflexivity proves this.','Reflexivity proves this. An optional alternative has details omitted.');(root/'one.tex').write_text(s)
    src=module().StacksSource(root)
    with self.assertRaisesRegex(ValueError,'incomplete'): src.extract('BBBB')
    review={'exact_phrase':'details omitted','scope':'optional alternative proof only','why_noncore':'Complete main proof by reflexivity does not use this alternative'}
    r=src.extract('BBBB',omitted_detail_review=review)
    self.assertIn('details omitted',r['proof'])
    with self.assertRaises(ValueError): src.extract('BBBB',omitted_detail_review=dict(review,exact_phrase='omitted'))

 def test_plain_metadata_caret_tilde_escaped(self):
    m=module();t=m.render(self.source,self.source.extract('BBBB'),{'title':'n>d^r ~ bound','difficulty_level':'H2','difficulty_reason':'n>d^r'})
    self.assertNotIn('d^r',t)
    self.assertIn('d\\textasciicircum{}r',t)
    self.assertIn('\\textasciitilde{}',t)

 def test_real_section_context_matches_locator_lines(self):
    src=module().StacksSource(P/'corpus/raw/stacks-project');c=src.context('dualizing-section-dualizing-local' if 'dualizing-section-dualizing-local' in src.tags else src.by_label['dualizing-section-dualizing-local'])
    lines=(src.root/c['file']).read_text().splitlines()
    exact='\n'.join(lines[c['start_line']-1:c['end_line']])
    self.assertEqual(exact.strip(),c['excerpt'].strip())

 def test_explicit_prose_context_span_is_exact(self):
    root=self.source.root;p=root/'one.tex';s=p.read_text();p.write_text('Let $a$ be fixed.\nDefine $b=a$.\n\n'+s)
    r=module().StacksSource(root).extract('BBBB',context_spans=[{'file':'one.tex','start_line':1,'end_line':2,'reason':'Necessary notation'}])
    self.assertEqual(r['contexts'][0]['excerpt'],'Let $a$ be fixed.\nDefine $b=a$.\n')
    self.assertEqual(r['contexts'][0]['kind'],'explicit_prose_span')

 def test_prose_span_rejects_incomplete_environment(self):
    with self.assertRaises(ValueError):self.source.extract('BBBB',context_spans=[{'file':'one.tex','start_line':1,'end_line':1,'reason':'Incomplete'}])

 def test_real_item_context_matches_exact_source_lines(self):
    src=module().StacksSource(P/'corpus/raw/stacks-project');c=src.context('0AU6');lines=(src.root/c['file']).read_text().splitlines()
    self.assertEqual('\n'.join(lines[c['start_line']-1:c['end_line']]).strip(),c['excerpt'].strip())
