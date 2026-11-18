import azure.functions as func
import logging
import json
import os
from azure.cosmos import CosmosClient 


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="counter")

def HTTPTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger funktio käsitteli pyynnön.")

    #Haetaan yhtesmerkkijono Azuren asetuksista
    connection_string = os.environ.get("CosmosDBConnectionString")
    
    if not connection_string:
        return func.HttpResponse(
            json.dumps({"error": "CosmosDBConnectionString ympyristömuuttujaa ei ole asetettu."}),
            status_code=500,
            mimetype="application/json"
        )
    try:
        #Yhdistetään Cosmos DB:hen
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client("counterpage-db")
        container = database.get_container_client("counter")

        #Luetaan nykyinen kävijänumero ("id": "1")
        item = container.read_item(item="1", partition_key="1")

        #Kasvatatetaan kävijänumeroa yhdellä
        item["count"] += 1

        #Päivitetään kävijänumero takaisin tietokantaan
        container.replace_item(item="1", body=item)

        #Palautetaan uusi kävijänumero fronttiin
        return func.HttpResponse(
            json.dumps({"count": item["count"]}),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "content-type"
            }
        )
    except Exception as e:
        logging.error(f"Virhe tietokannan käsittelyssä: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
