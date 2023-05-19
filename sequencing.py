import requests

def main():
    studies = query_ena()
    write_results(studies,"all_sequencing_studies.txt")


def query_ena():
    # GEO doesn't have a way to query the submitting institution, but since its
    # data is mirrored over to ENA we can do the query on ENA and then take the
    # ids from that back to get the GEO ids

    data = requests.get("https://www.ebi.ac.uk/ena/portal/api/search?query=center_name=%22babraham%22&result=study&fields=study_accession,secondary_study_accession,study_title,study_description,center_name,first_public,geo_accession,scientific_name&limit=0&download=true&format=json")
    data.encoding = data.apparent_encoding
    data = data.json()

    studies = []

    for entry in data:

        print("Processing "+entry["study_accession"])

        # Some of these are super-series - which we'll ignore
        if entry["study_description"].startswith("This SuperSeries"):
            continue

        database = ""
        accession = ""
        link = ""
        submitters = ""
        publication = ""

        # We try databases in order of preference
        if "geo_accession" in entry and entry["geo_accession"]:
            database = "GEO"
            accession = entry["geo_accession"]
            link = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}"
            submitters, publication = get_geo_info(accession)

        elif entry["secondary_study_accession"].startswith("ERP"):
            database = "ArrayExpress"
            accession, submitters, publication = get_array_express_info(entry['secondary_study_accession'])
            link = f"https://www.ebi.ac.uk/biostudies/arrayexpress/studies/{accession}"

            if not accession:
                # If we don't find an array express ID then this is just an ENA/SRA
                # submission
                database = "ENA"
                accession = entry["study_accession"]
                link = f"https://www.ebi.ac.uk/ena/browser/view/{accession}"
        else:
            print(f"Skipping {entry['study_accession']} as it's not GEO or Array Express")
            continue

        # Turn the pubmed id into a link (if there is one)
        if publication:
            publication = "https://pubmed.ncbi.nlm.nih.gov/"+publication

        studies.append({
            "database": database,
            "accession":accession,
            "link": link,
            "date": entry["first_public"],
            "submitters": submitters,
            "publication": publication,
            "title": entry['study_title']
        })

    return studies

def get_geo_info(accession):
    data = requests.get(f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}&form=text&view=quick")
    data.encoding = data.apparent_encoding
    data = data.text

    submitters = []
    pmid = ""

    for line in data.split("\n"):
        if line.startswith("!Series_contributor"):
            submitters.append(line.split("=")[1].strip().replace(","," "))

        elif line.startswith("!Series_pubmed_id"):
            pmid = line.split("=")[1].strip()

    # Remove double spaces
    submitters = [x.replace("  "," ") for x in submitters]

    return ", ".join(submitters),pmid


def get_array_express_info(ena_accession):
    data = requests.get(f"https://www.ebi.ac.uk/biostudies/api/v1/search?query={ena_accession}").json()
    
    if not "hits" in data:
        return "","",""
    
    if not data["hits"]:
        return "","",""
    

    accession = data["hits"][0]["accession"]
    submitters = data["hits"][0]["author"]

    # We now need to find a publication.  This needs the full array express document
    fulldata = requests.get(f"https://www.ebi.ac.uk/biostudies/files/{accession}/{accession}.json")
    fulldata.encoding = fulldata.apparent_encoding
    fulldata = fulldata.json()

    publication = ""

    # If there's a publication it will be in data["subsections"][x]["type"] == "publication"
    # the PMID is data["subsections"][x]["accno"]

    for section in fulldata["section"]["subsections"]:
        if "type" in section and section["type"].lower() == "publication":
            if "accno" in section:
                publication = section["accno"]
                break


    return accession, submitters, publication


def write_results(studies, file):
    with open(file,"wt", encoding="utf8") as out:
        fields = list(studies[0].keys())
        print("\t".join(fields), file=out)

        for study in studies:
            values = [study[x] for x in fields]

            print("\t".join(values), file=out)




if __name__ == "__main__":
    main()