from setuptools import setup, find_packages

setup(
    name="vocalAIze",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.1.1",
        "pyaudio>=0.2.13",
        "pydub>=0.25.1",
        "python-dotenv>=1.0.0",
    ],
    author="Romil Shah",
    author_email="your.email@example.com",
    description="Voice-powered AI assistant that leverages OpenAI for speech-to-text, language processing, and text-to-speech capabilities",
    keywords="voice, AI, assistant, OpenAI, speech-to-text, text-to-speech",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "vocalAIze=main:main",
        ],
    },
)