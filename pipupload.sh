#https://geekytheory.com/como-subir-tu-propio-paquete-a-pypi
tagname='0.1.4'
git tag --delete ${tagname}
git tag ${tagname}   -m "Star Adventurer Mini support thanks to Emmanuel FARHI"
git push origin :refs/tags/${tagname}
git push --tags origin master
python setup.py sdist upload -r pypi
