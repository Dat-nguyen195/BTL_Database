# Use XeLaTeX for fontspec and Vietnamese text.
$pdf_mode = 5;
$do_cd = 1;
$out_dir = 'build';
@default_files = ('main.tex');
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
