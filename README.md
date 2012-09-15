yatir
=====

## Introduction

yatir is a yet another Tumblr image ripper. It downloads images from a given Tumblr blog. It always tries to download images in the highest resolution.

For example, if you want to download images from ACCIDENTAL CHINESE HIPSTERS execute the following command:

  $ yatir accidentalchinesehipsters.tumblr.com

## Installing yatir

yatir is written in Python and thus requires Python to be installed.

### 1. Clone yatir from Github

  git clone https://github.com/hypebeast/yatir.git yatir

### 2. Start yatir
  $ ./yatir

## Usage

### 1. Configure yatir

To configure yatir edit the config.ini file. This file located in '~/.yatir'.

### 2. Create the blogs file

By default yatir reads the Tumblr blogs from blogs.txt located in the same directory as yatir is executed. Each line contains one blog name. For example:

```text
monk3y
playwithfire
jessica-fletcher
thingsthatexciteme
```

### 3. Start downloading images

  $ ./yatir

### Command line arguments

To see all available command line arguments, execute:

  $ ./yatir -h
