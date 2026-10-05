import os
from setuptools import setup
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext


class BuildExtRename(build_ext):
    def run(self):
        super().run()

        # rename generated .pyd files
        for f in os.listdir(os.getcwd()):
            if f.endswith(".pyd") and "cp" in f:
                new_name = f.split(".cp")[0] + ".pyd"
                os.replace(f, new_name)
                print(f"Renamed {f} -> {new_name}")


# automatically collect all .pyx files
files = []

for file in os.listdir():
    if file.endswith(".pyx"):
        files.append(file)


setup(
    ext_modules=cythonize(files, compiler_directives={"language_level": "3"}),
    cmdclass={"build_ext": BuildExtRename},
    options={"build_ext": {"inplace": True}},
)


