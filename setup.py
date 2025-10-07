from setuptools import setup, find_packages

setup(
    name="pdf-extractor",
    version="0.1.0",
    description="PDF text extraction module with streaming support",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["pdfplumber>=0.7.0"],
    extras_require={"dev": ["pytest>=7.0.0"]},
    entry_points={"console_scripts": ["pdf-extractor=pdf_extractor.__main__:main"]},
)
