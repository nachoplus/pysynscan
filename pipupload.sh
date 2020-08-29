#https://geekytheory.com/como-subir-tu-propio-paquete-a-pypi
tagname='0.1.1'
git tag --delete ${tagname}
git tag ${tagname}   -m "First pip candidate"
git push origin :refs/tags/${tagname}
git push --tags origin master
python setup.py sdist upload -r pypi
