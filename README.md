# VCF CSV JSON lib_list - converter
Yes, this is another VCF/CSV converter, but it is perfect for my needs.


## Short description
This tiny script convert VCF, CSV and JSON file to each other.  
Plus can decode quoted printable strings and reduce phone attributes if they are identical to each other.  
  \
The functions are separate, so are easily use for your scripts, from this derive lib_list in the name.

## Installation
NO dependecies are required, i use python 3.8.2 for run this script.

## Usage
```
usage: python3 . <conversion> [--decode] [--reducer] <filename>

conversion:
--vcf2csv                From VCard to CSV
--vcf2json               From VCard to JSON
--csv2vcf                From CSV to VCard
--csv2json               From CSV to JSON
--json2vcf               From JSON to VCard
--json2csv               From JSON to CSV

--decode                 Decode quoted printable strings
--reducer                Reduce phone attributes if they have the same value


WARNING: The conversion does not keep the value of duplicate attributes
```
