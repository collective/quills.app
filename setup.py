from setuptools import setup, find_packages
import os

version = '1.7.0c1-post1'

setup(name='quills.app',
      version=version,
      description="The Quills blogging suite. Contains code shared between "
                  "Products.Quills and  Products.QuillsEnabled.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone blogging',
      author='Quills Team',
      author_email='plone-quills@googlegroups.com',
      url='http://plone.org/products/quills',
      download_url="http://svn.plone.org/svn/collective/quills.app",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quills'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'quills.core>=1.7.0c1,<=1.7.99',
          'Products.basesyndication',
          'Products.fatsyndication'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
