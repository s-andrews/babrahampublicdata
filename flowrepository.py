import requests
import re
from pathlib import Path
from html.parser import HTMLParser

def main():

    reject_id_file = "flowrepository_rejects.txt"

    already_rejected_ids = load_rejected_ids(reject_id_file)
    ids = get_all_projects()

    with open("all_flowrepository_data.txt","wt", encoding="utf8") as out:
        printed_header = False
        with open(reject_id_file,"at", encoding="utf8") as rejects:
            for id in ids:
                print("Checking "+id)
                if id in already_rejected_ids:
                    print("Already rejected")
                    continue

                details = parse_id(id)
                if not details:
                    print("Not Babraham")
                    # This isn't a Babraham entry
                    print(id, file=rejects)
                
                else:
                    print("Printing details")
                    if not printed_header:
                        # We need to add a header
                        headers = list(details.keys())
                        print("\t".join(headers), file=out)
                        printed_header = True
                    
                    line = [str(x) for x in details.values()]
                    print("\t".join(line), file=out)



def parse_id(id):
    # Get the details for this id, only if this is a Babraham sample
    # if it's not a Babraham sample then return None so we don't bother
    # checking this again in future.

    data = requests.get(f"http://flowrepository.org/id/{id}").text

    if not "babraham" in data.lower():
        return None

    parser = FlowParser()
    parser.feed(data)

    # Now we need to get the data out of the parser.

    # This is what we need to collect.
    names = []
    for i in ['Primary researcher','PI/manager',"Uploaded by"]:
        if parser.values_to_collect[i] and parser.values_to_collect[i] not in names:
            names.append(parser.values_to_collect[i])

    names = ", ".join(names)

    publication = ""

    date = make_date(parser.values_to_collect["Dataset uploaded"])

    if parser.values_to_collect["Manuscripts"]:
        # We just take the first 4+ digit number out of that
        # and assume we've correctly captured the pubmed id
        hit = re.search("(\d{4,})",parser.values_to_collect["Manuscripts"])
        publication = "https://pubmed.ncbi.nlm.nih.gov/"+hit.groups()[0]+"/"
    

    values_to_return = {
            "database": "FlowRepository",
            "accession": id,
            "link": f"http://flowrepository.org/id/{id}",
            "date": date,
            "submitters": names,
            "publication": publication,
            "title": parser.values_to_collect["Experiment name"],
            "description": ""

    }
    return values_to_return

def make_date(text):
    # We get dates looking like "Jul 2017" and we need them to
    # be 2017-07-01
    months = {
        "Jan":"01",
        "Feb":"02",
        "Mar":"03",
        "Apr":"04",
        "May":"05",
        "Jun":"06",
        "Jul":"07",
        "Aug":"08",
        "Sep":"09",
        "Oct":"10",
        "Nov":"11",
        "Dec":"12"
    }

    month,year = text.split(" ")

    date = year.strip()+"-"+months[month.strip()]+"-01"

    return date


class FlowParser(HTMLParser):
    # Pretty much everything we need here comes from td elements
    # where we're going to get the value from one td and then
    # pull out the data in the next one when we see it

    def __init__(self):
        HTMLParser.__init__(self)
        self.values_to_collect = {
            "Experiment name":"",
            "Primary researcher":"",
            "PI/manager":"",
            "Uploaded by":"",
            "Dataset uploaded":"",
            "Manuscripts":""
        }
        self.innametd = False
        self.invaluetd = False
        self.value_to_collect = ""

    def handle_starttag(self, tag , attrs) -> None:
        if tag=="td":
            if self.innametd:
                if self.value_to_collect:
                    self.invaluetd = True
                    #print("Setting invaluetd")

                self.innametd = False
    
            else:
                #print("Setting innametd")
                self.innametd = True

    def handle_endtag(self, tag):
        if tag == "td":
            if self.invaluetd:
                self.invaluetd = False
                self.value_to_collect = ""


    def handle_data(self, data) -> None:
        # If this isn't a td data then we don't care
        if not (self.innametd or self.invaluetd):
            #print("Not in name or value")
            return


        # Are we collecting a value for an existing value? If so we collect
        # the data for that.
        if self.invaluetd and self.value_to_collect:
            #print("Collecting "+data.strip()+" for "+self.value_to_collect)
            self.values_to_collect[self.value_to_collect] += data.strip()
            

        elif not self.value_to_collect:
            # Otherwise we check to see if the data matches any of the 
            # values we want to collect next time around
            #print("Checking for name in "+data)

            for k in self.values_to_collect.keys():
                if k in data:
                    self.value_to_collect = k
                    #print("Setting value to "+k)
                    return

            # If we get here then whatever was in this field was something
            # we don't care about.
            #print("No name match to "+data)

def load_rejected_ids(file):
    # This file will have a list of flow repository ids which we've 
    # previously parsed and know have no connection to Babraham so
    # we don't need to look at them again.

    rejected_ids = []

    if not Path(file).exists():
        return rejected_ids

    with open(file, "rt", encoding="utf8") as infh:
        for line in infh:
            id = line.strip()
            if id:
                rejected_ids.append(id)


    return rejected_ids

def get_all_projects():
    # We haven't been able to get a repository API key from them so we're
    # going to have to do this the old fashioned way unfortunately.

    # We'll start by getting the base page which will give us the first
    # lot of ids and the number of pages to retrieve
    data = requests.post("http://flowrepository.org/ajax/list_public_ds").text

    page_numbers = get_page_numbers(data)
    
    ids = get_ids(data)

    print (f"Found {len(ids)} ids on page 1 of {page_numbers}")

    for i in range(2,page_numbers):
        data = requests.post("http://flowrepository.org/ajax/list_public_ds",json={"pg":str(i)}).text
        new_ids = get_ids(data)
        print (f"Found {len(new_ids)} ids on page {i} of {page_numbers}")

        ids.extend(new_ids)

    return ids


def get_ids(text):
    ids = []
    for hit in re.finditer("<td class='repid'><a href=\"http://flowrepository.org/id/([^\"]+?)\"",text):
        ids.append(hit.groups()[0])

    return ids

def get_page_numbers(text):
    hit = re.search("Displaying page \d+ of (\d+)",text)

    return int(hit.groups()[0])


if __name__ == "__main__":
    main()