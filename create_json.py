import json

def main():
    all_data = []
    data_files = ["all_pride_studies.txt","all_sequencing_studies.txt"]

    for file in data_files:
        read_file(file,all_data)

    write_json(all_data, "www/babraham_public_data.json")


def write_json(data, file):
    with open(file,"wt", encoding="utf8") as out:
        out.write(json.dumps(data))

def read_file(file,data):
    with open(file,"rt",encoding="utf8") as infh:
        headers = infh.readline().strip().split("\t")
        for line in infh:
            sections = line.strip().split("\t")

            # A kludge to work around breakage in the sequencing data
            if len(sections) != len(headers):
                continue

            if not sections:
                continue

            this_data = {}
            for i in range(len(headers)):
                this_data[headers[i]] = sections[i]

            data.append(this_data)


if __name__=="__main__":
    main()