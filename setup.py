from setuptools import setup, find_packages
import pathlib

# the directory containing this file
HERE = pathlib.Path(__file__).parent

# the readme
README = (HERE / "README.md").read_text() if (HERE / "README.md").exists() else ""

setup(
    name='biostats-anki',
    version='0.1.0',
    description='anki deck generator for biostats phd cards',
    long_description=README,
    long_description_content_type='text/markdown',
    author="Ha'asídí 鹿泉·哨",
    author_email='public.4g8dtswh@naashjeii.com', # optional
    license='mit', # optional
    packages=find_packages(exclude=("tests",)),
    # this is crucial for including your html/css files
    include_package_data=True,
    package_data={
        # all .html and .css files in 'biostats_anki/anki-card-templates'
        'biostats_anki': ['anki-card-templates/*.html', 'anki-card-templates/*.css'],
    },
    # define dependencies
    install_requires=[
        'genanki',
    ],
    # define the command-line script
    entry_points={
        'console_scripts': [
            'biostats-anki=biostats_anki.main:cli_entry',
        ],
    },
)