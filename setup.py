from setuptools import setup, find_packages

setup(
    name='privacy_protocol',
    version='0.1.0',
    author='Josephis K. Wade',
    author_email='josephis.wade@gmail.com',
    description='A Python framework for Privacy-by-Design, enabling machine-readable policies, dynamic enforcement, and verifiable auditing of user consent.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BigBossBooling/PrivacyProtocol',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.9',
)
