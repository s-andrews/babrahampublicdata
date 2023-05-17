# Babraham Public Data
This repository contains code which scrapes the major public data repositories to find all data deposited by Babraham, and then uses this to populate a web interface.

The repositories which are covered are:

1. GEO (https://www.ncbi.nlm.nih.gov/geo/)
2. ENA (https://www.ebi.ac.uk/ena/browser/)
3. ArrayExpress (https://www.ebi.ac.uk/biostudies/arrayexpress)
4. PRIDE (https://www.ebi.ac.uk/pride/)

We will be adding support for FlowRepository and BioImageArchive in due course.

Scripts
-------
The main scripts of relevance are

```sequencing.py```
Collects all of the sequencing data and populates a file called ```all_sequencing_studies.txt```

```pride.py```
Collects proteomics data from PRIDE and populates all_pride_studies.txt```

```create_json.py```
Reads the delimited output from the above scripts and combines them into a JSON file called ```babraham_public_data.json``` in the ```www``` folder

An update of the data in this repository would require running these scripts in the order they are listed.

Web interface
-------------

The web front end to this system is initialised by making the ```www``` directory accessible on a web server.  There is no server side code so a simple file level export is fine.
