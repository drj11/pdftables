from pdftables.scripts.render import main
import sys
import os
import shutil
import glob
from nose.tools import with_setup


def clean_output_directories():
    sys.argv[1] = 'fixtures/sample_data/unica_preco_recebido.pdf'
    shutil.rmtree('png', ignore_errors=True)
    shutil.rmtree('svg', ignore_errors=True)

@with_setup(clean_output_directories)
def test_png_output_directory_is_created():
    assert not os.path.isdir('png')
    main()
    assert os.path.isdir('png')

@with_setup(clean_output_directories)
def test_svg_output_directory_is_created():
    assert not os.path.isdir('svg')
    main()
    assert os.path.isdir('svg')

@with_setup(clean_output_directories)
def test_expected_png_output():
    main()
    assert os.path.isfile('png/unica_preco_recebido.pdf_00.png')

@with_setup(clean_output_directories)
def test_expected_svg_output():
    main()
    assert os.path.isfile('svg/unica_preco_recebido.pdf_00.svg')

# Some of the fixture pdfs
PDF_FILES = [
    ('fixtures/sample_data/unica_preco_recebido.pdf', 1),
    ('fixtures/sample_data/m29-JDent36s2-7.pdf', 6),
    ('fixtures/sample_data/COPAMONTHLYMay2013.pdf', 1),
    ('fixtures/sample_data/COPAWEEKLYJUNE52013.pdf', 1),
    ('fixtures/sample_data/tabla_subsidios.pdf', 1),
    ('fixtures/sample_data/AnimalExampleTables.pdf', 4),
    ('fixtures/sample_data/m30-JDent36s15-20.pdf', 6),
    ('fixtures/sample_data/commodity-prices_en.pdf', 1),
]

@with_setup(clean_output_directories)
def test_expected_number_of_pages():
    for infile, expected_pages in PDF_FILES:
        sys.argv[1] = infile
        main()

        actual_pages = len(glob.glob('svg/%s_*.svg' % os.path.basename(infile)))
        assert expected_pages == actual_pages

        actual_pages = len(glob.glob('png/%s_*.png' % os.path.basename(infile)))
        assert expected_pages == actual_pages
