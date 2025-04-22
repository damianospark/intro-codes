#!/bin/bash

# Mecab-ko 설치
wget -O- http://ftpmirror.gnu.org/automake/automake-1.11.tar.gz | tar xzf -
cd automake-1.11
./configure
make
make install
cd ..
wget -O- https://bitbucket.org/eunjeon/mecab-ko/downloads/mecab-0.996-ko-0.9.2.tar.gz | tar xzf -
cd mecab-0.996-ko-0.9.2
./configure
make
make check
make install
ldconfig

# Mecab-ko-dic 설치
wget -O- https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.1.1-20180720.tar.gz | tar xzf -
cd mecab-ko-dic-2.1.1-20180720
./autogen.sh
./configure
make
make install

pip install natto-py
