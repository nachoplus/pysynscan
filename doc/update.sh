
#!/bin/bash
make clean
cd ./_build
git clone -b gh-pages --single-branch git@github.com:nachoplus/pysynscan.git html
cd ../pysynscan/docs
make html
make latexpdf
cd ./_build/html
cp ../latex/pysynscan.pdf .
pwd
git add .
git commit -a -m "Updated documentation"
git push origin gh-pages
