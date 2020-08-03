#!/bin/bash
fecha=`date`
make clean
cd ../../pysynscandocs
git clone -b gh-pages --single-branch https://github.com/nachoplus/pysynscan.git html
cd ../pysynscan/docs
make html
make latexpdf
cd ../../pysynscandocs/html
cp ./latex/pysynscan.pdf .
pwd
git add .
git commit -a -m "Updated documentation ${fecha}"
git push origin gh-pages
