$( document ).ready(function() {
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
        table.row.add([
            data[r]["database"],
            "<a href=\""+data[r]["link"]+"\">"+data[r]["accession"]+"</a>",
            data[r]["date"],
            data[r]["title"],
            data[r]["submitters"]
        ])
    }

    table.columns.adjust().draw();

}

