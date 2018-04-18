from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
	name = "uetlib",
	ext_modules = cythonize("uetlib.pyx")
)