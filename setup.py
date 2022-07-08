from setuptools import setup


def readme():
    with open('README.md', 'r') as fp:
        return fp.read()


def requirements():
    with open('requirements.txt', 'r') as fp:
        return fp.read().split()


setup(
    author='Guy Saar',
    author_email='guy.saar@tikalk.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Operating System :: Linux Based OS",
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    description='Module to easily convert Route53 zones into Terraform CloudFlare provider records definitions',
    include_package_data=True,
    install_requires=requirements(),
    license='MIT',
    long_description=readme(),
    long_description_content_type='text/markdown',
    name='route53_to_cloudflare',
    packages=[
        'route53_to_cloudflare'
    ],
    scripts=[
        'scripts/route53-to-cloudflare'
    ],
    url='https://github.com/itaior/tfname-cf',
    version='0.0.2',
)
