from setuptools import setup, find_packages

setup(
    name="business-documents",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain-openai>=0.0.5",
        "python-dotenv>=1.0.0",
        "pinecone-client>=3.0.0",
        "boto3>=1.34.0",
        "streamlit>=1.30.0",
        "langchain-core>=0.1.0",
    ],
    python_requires=">=3.8",
)
