from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='satellite_czml',
    version='0.1.1',
    description='Creates a CZML string based on TLE (Two Line Element set) data for plotting satellites on the open source CesiumJS JavaScript library',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Nicholas Miller',
    author_email='miller.nicholas.a@gmail.com',
    keywords=['satellite-czml', 'satellite', 'czml', 'tle', 'cesium', 'cesiumjs', 'tle2czml', 'sgp4'],
    url='https://github.com/cassova/satellite-czml',
    download_url='https://github.com/cassova/satellite-czml'
)

install_requires = [
    'sgp4>=2.15',
    'pygeoif',
    'simplejson',
    'pytz'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
