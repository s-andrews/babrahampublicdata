# We tried to do this query via proteome exchange since that would cover
# all of the proteomics databases under that banner, but that doesn't
# seem to have a centralised API and the search tool on the website is
# horribly broken.  We've gone to PRIDE specifically, which is probably
# OK since that's where we always submit our data.


import requests

def main():
    studies = get_pride_studies()
    write_studies(studies,"all_pride_studies.txt")

def write_studies(studies, file):
    with open(file,"wt", encoding="utf8") as out:
        headers = list(studies[0].keys())
        print("\t".join(headers), file=out)

        for study in studies:
            line = [study[x] for x in headers]
            print("\t".join(line), file=out)



def get_pride_studies():
    # There isn't a specific field to query submitter institutions so
    # we need to just use babraham as a keyword.  This seems to work
    # OK though.
    query_url = "https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=babraham&pageSize=1000&sortDirection=DESC&sortFields=submission_date"

    studies = requests.get(query_url).json()

    kept_studies = []
    for study in studies["_embedded"]["compactprojects"]:

        # We just searched on a keyword so we might not actually have a Babraham affiliation
        # (though Babraham is a pretty specific search term)
        if not "babraham" in " ".join(study["affiliations"]).lower():
            print("No Babraham affiliation for "+study["accession"])

        doi = ""
        if study["references"]:
            doi = get_doi(study["accession"])

        kept_studies.append({
            "accession": study["accession"],
            "title": study["title"],
            "description": study["projectDescription"],
            "date": study["publicationDate"],
            "doi": doi
        })

    return kept_studies


def get_doi(accession):
    # There is a separate API to pull the full details of a study to get the doi

    data = requests.get(f"https://www.ebi.ac.uk/pride/ws/archive/v2/projects/{accession}").json()

    return data["references"][0]["doi"]


if __name__ == "__main__":
    main()