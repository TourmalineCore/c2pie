# PDF Structure Overview

This document describes base structure of PDF file and workflow for C2PA manifest injection to PDF file.

## General information

Basic PDF file contains following parts:
- ***Header***: contains PDF version and base document information (e.g. title, producer, etc.)
- ***Body***: contains number of objects that describe content of document (e.g. ContentTree, custom object, etc.)
- ***Cross-reference section***: contains offsets from the beginning of the file for each object that located in *body*
- ***Trailer***: contains information about *cross-reference section*, such as length and offset

PDF standard supports adding new objects to already existing PDF file. This process is called `Incremental Updates`.

## Incremental Updates

The contents of PDF file can be updated incrementally without rewriting the entire file. When updating a PDF file incrementally, changes shall be appended to the end of the file, leaving its original contents intact.

This feature could help to embed C2PA manifest to already existing file without changing the existing structure, which can make embedding easier.

Incremental updated PDF file structure should contain the following parts:
- ***Original header***
- ***Original body***
- ***Original cross-reference section***
- ***Original trailer*** with reference to Cross-reference Section Update (tag `Prev`)
- ***Body Update***: contains new/changed objects
- ***Cross-reference Section Update***: contains offsets for new/changed objects
- ***Updated Trailer***: should cotains reference to Original cross-reference section

For further information please follow to [ISO 3200](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) (7.5.6 Incremental Updates).


## Embedding of C2PA Manifest Stores

All C2PA Manifest Stores shall be embedded using embedded file streams ([ISO 3200](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf), 7.11.4 Embedded File Streams).
Also there is needed to add AFRelationship object which value is C2PA_Manifest and refer to file stream object.

The following are the possible steps for embedding C2PA manifest to PDF file structure:
1. Create a stream object with C2PA manifest as payload
2. Create an AFRelationship object with reference to stream object
3. Add reference to AFRelationship object to Root object that specified in Trailer (`/Root` tag)
4. Create ***Cross-reference Section Update***
5. Create ***Updated Trailer***

***Please note that this information is an assumption based on existing documentation and an analysis of the Adobe PDF file example (`docs/examples/adobe_doc_example.pdf`). This has not been tested in practice.***

## References
1. [ISO 3200. Document Managment - Portable document format - Part 1: PDF 1.7](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf)
2. [Content Credentials. Embedding manifests into PDFs](https://c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_embedding_manifests_into_pdfs:~:text=A.4.-,Embedding%20manifests%20into%20PDFs,-A.4.1.%20General)