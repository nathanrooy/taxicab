from setuptools import setup
import taxicab as tc

with open("README.md", "r") as f:
    long_description = f.read()
    
with open("requirements.txt", "r") as f:
    INSTALL_REQUIRES = [line.strip() for line in f.readlines()]

setup(
    name='Taxicab',
    version=tc.__version__,
    author=tc.__author__,
    author_email='nathanrooy@gmail.com',
    url='https://github.com/nathanrooy/taxicab',
    description='Accurate routing for Open Street Maps and OSMnx',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['taxicab'],
    python_requires='>=3.5',
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)
