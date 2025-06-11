
from setuptools import setup, find_packages

setup(
    name='sentinelit',
    version='1.1.0',
    author='James Zulu',
    author_email='james.zulu@diakriszuluinvestmentsprojects.co.za',
    description='SentinelIT – AI-driven cybersecurity suite with reverse engineering traps and advanced defense modules',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zulu74/SentinelIT_NextGEN-CYBERSECURITY-SOFTWARE',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
