from setuptools import setup

setup(
    name="agent-kom",
    version="0.1",
    py_modules=["cli"],
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "agent-kom=cli:main",
        ],
    },
)