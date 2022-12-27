#https://geekytheory.com/como-subir-tu-propio-paquete-a-pypi
tagname='0.1.3'
git tag --delete ${tagname}
git tag ${tagname}   -m "Added open-synscan support"
git push origin :refs/tags/${tagname}
git push --tags origin master
python setup.py sdist upload -r pypi
