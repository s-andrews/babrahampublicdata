import requests

def main():
    studies = query_ena()
    write_results(studies,"all_studies.txt")


def query_ena():
    # GEO doesn't have a way to query the submitting institution, but since its
    # data is mirrored over to ENA we can do the query on ENA and then take the
    # ids from that back to get the GEO ids

    data = requests.get("https://www.ebi.ac.uk/ena/portal/api/search?query=center_name=%22babraham%22&result=study&fields=study_accession,secondary_study_accession,study_title,study_description,center_name,first_public,geo_accession,scientific_name&limit=0&download=true&format=json").json()

    studies = []

    for entry in data:
        studies.append({
            "ena_accession":entry["study_accession"],
            "geo_accession":entry["geo_accession"],
            "secondary_accession":entry["secondary_study_accession"],
            "title": entry['study_title'],
            "description": entry["study_description"],
            "date": entry["first_public"]
        })


    return studies


def write_results(studies, file):
    breakpoint()
    with open(file,"wt", encoding="utf8") as out:
        fields = list(studies[0].keys())
        print("\t".join(fields), file=out)

        for study in studies:
            values = [study[x] for x in fields]

            print("\t".join(values), file=out)




if __name__ == "__main__":
    main()