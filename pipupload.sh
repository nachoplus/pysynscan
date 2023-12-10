#https://geekytheory.com/como-subir-tu-propio-paquete-a-pypi
tagname='0.1.5'
git tag --delete ${tagname}
git tag ${tagname}   -m "Serial port support and some bug fix from Wim Heirman"
git push origin :refs/tags/${tagname}
git push --tags origin master
python setup.py sdist upload -r pypi
