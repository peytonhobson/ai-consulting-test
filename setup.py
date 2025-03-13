from setuptools import setup

setup(
    name="cognitive-core",
    version="0.1.0",
    install_requires=[
        "langchain-openai>=0.3.0",
        "python-dotenv>=1.0.0",
        "pinecone>=6.0.0",
        "streamlit>=1.43.0",
        "langchain-core>=0.3.0",
        "langchain-community>=0.3.0",
        "numpy==1.23.5",
        "flashrank>=0.1.0",
        "openai>=1.66.0",
    ],
    python_requires=">=3.8",
)
