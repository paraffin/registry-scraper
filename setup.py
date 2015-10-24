from setuptools import setup, find_packages

setup(
    name='registry_scraper',
    version='0.0.1',
    packages=['registry_scraper']),
    install_requires=[
        'boto==2.38.0'
    ],
    entry_points={
        'console_scripts': [
            'registry_scraper = registry_scraper.__main__:main'
        ]
    }
)
