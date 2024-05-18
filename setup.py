from setuptools import find_packages,setup

setup(
    name='SAevaluator',
    version='0.0.1',
    author='Swapnil Jyot',
    author_email='swapniljytkd888@gmail.com',
    install_requires=["openai","langchain","streamlit","python-dotenv","PyPDF2"],
    packages=find_packages()
)