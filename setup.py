from setuptools import setup, find_packages

long_desc = """
PDFTables helps with extracting tables from PDF files.
"""
# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for classifiers

setup(
    name='pdftables',
    version='0.0.3',
    description="Parses PDFs and extracts what it believes to be tables.",
    long_description=long_desc,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
    keywords='',
    author='ScraperWiki Ltd',
    author_email='feedback@scraperwiki.com',
    url='http://scraperwiki.com',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'pdfminer>=20110515',
    ],
    tests_require=[],
    entry_points=\
    """
    """,
)
