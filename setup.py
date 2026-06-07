from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "bim.utils.algoritm_packing",
        ["bim/utils/algoritm_packing.pyx"]
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        language_level=3
    )
)