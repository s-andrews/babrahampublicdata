$( document ).ready(function() {
    $.ajaxSetup({
        scriptCharset: "utf-8",
        contentType: "application/json; charset=utf-8"
    });
    $.getJSON(
        "babraham_public_data.json",
        populateTable
    )
});

function populateTable(data) {
    console.log(data)
    d = data

    let table = new DataTable("#publicdata")


    for (let r=0; r< data.length; r++) {

        let title = data[r]["title"]
        if (data[r]["publication"]) {
            title = "<a target=\"_external\" href=\""+data[r]["publication"]+"\">Publication</a> "+title
        }

        table.row.add([
            data[r]["database"],
            "<a href=\""+data[r]["link"]+"\" target=\"_external\">"+data[r]["accession"]+"</a>",
            data[r]["date"],
            title,
            data[r]["submitters"]
        ])
    }

    table.columns.adjust().order([2,'desc']).draw();
    

}

