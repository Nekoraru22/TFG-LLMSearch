from setuptools import setup

setup(
    name="llmsearch",
    version="0.1",
    py_modules=["llmsearch"],
    entry_points={
        "console_scripts": [
            "LLMSearch=llmsearch:main",
        ],
    },
)