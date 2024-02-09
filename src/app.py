from flask import Flask, request
import pymongo
import time
from urllib.request import urlopen
import json
from bson import json_util 
uriDb = "mongodb+srv://nemaperez:UNKtXBbFfINm9dOg@cluster0.l24kvay.mongodb.net/?retryWrites=true&w=majority"
app = Flask(__name__)
app.config['MONGO_URI'] = uriDb
client =  pymongo.MongoClient(uriDb)
baseUrl = "https://api.tvmaze.com"
collection = client['TvMazeDb']['Shows']
collectionComments = client['TvMazeDb']['ShowRatings']


#buscar 
@app.route('/TvMase_Buscar',methods= ['Post'])
def Search():
 nameShow = request.json['name']
 if nameShow:
   response  =  urlopen(baseUrl + "/search/shows?q=" + nameShow)
   data = json.loads(response.read())

   resultObj = []
   
   for item in data:
    
    comentsObj = []
    resultComents =  list(collectionComments.find({ 'idShow': str(item["show"]["id"]) }))
    if  resultComents:
        for comm in  resultComents:
         comentsObj.append({ "comments": comm["comments"],"rating": comm["Rating"] })

    if item["show"]["network"]:
     networktext = item["show"]["network"]["name"]
    else:
      networktext =  item["show"]["webChannel"]["name"]    
    resultObj.append({ "id": item["show"]["id"] , 
                      "name" : item["show"]["name"],
                      "channel" : networktext,
                      "summary" : item["show"]["summary"],
                      "genres" : item["show"]["genres"],
                      "comments" : comentsObj
                      })
    
   

   return resultObj
 else:
   return {"message":"Debe ingresar el nombre del show"}
 
#Mostrar
@app.route('/TvMase_Mostrar',methods= ['Post'])
def Show():
 showId = request.json['show_id']
 if showId:
  
     result = collection.find_one({ 'id': showId })

     if result :
       
      comentsObj = []
      resultComents =  list(collectionComments.find({ 'idShow': str(showId) }))
      if  resultComents:
        for comm in  resultComents:
         comentsObj.append({ "comments": comm["comments"],"rating": comm["Rating"] })

      
        return       { "id": result["id"] , 
                      "name" : result["name"],
                      "channel" : result["channel"],
                      "summary" : result["summary"],
                      "genres" : result["genres"],
                      "comments" : comentsObj
                      }

     else:


        serchParameter = "/shows/" + showId
        response  =  urlopen(baseUrl + serchParameter)
        data = json.loads(response.read())

        try:
             
        
         collection.insert_one(
            {
            "id" : str(data["id"]),
            "name" : str(data["name"]),
            "channel" : str(data["network"]["name"]),
            "summary" : str(data["summary"]),
            "genres" : str(data["genres"])
            })
             
         return data
        except:
             return   {"message":"ocurrio un error en el guardado"}
 else:
  return {"message":"Debe ingresar un showId"}
 
#Comments
@app.route('/TvMase_Comentarios',methods= ['Post'])
def Commnets():
 showId = request.json['show_id']
 comment = request.json['comment']
 rating =  request.json['rating']
 if showId and comment and rating:
      
     try:
 
           collectionComments.insert_one(
        {
          "idShow" : str(showId),
          "comments" : str(comment),
          "Rating" : str(rating),
          
         })

           return {
                 "message":"Registro Guardado Correctamente",
                 "idShow" : str(showId),
                 "comments" : str(comment),
                 "Rating" : str(rating)
                }
     except:
       return   {"message":"ocurrio un error en el guardado"}
 else:
     return   {"message":"los parametros showId , comment y rating son requeridos"}
 
#Rating
@app.route('/TvMase_Promedio',methods= ['Post'])
def Rating():
  showId = request.json['show_id']
  if showId:
        
        time.sleep(4)
        serchParameter = "/shows/" + showId
        response  =  urlopen(baseUrl + serchParameter)
        data = json.loads(response.read())
        
        return   {
            "id" : str(data["id"]),
            "name" : str(data["name"]),
            "rating_average" : str(data["rating"]["average"]),
            }
  else:
        return   {"message":"los parametros showId , comment y rating son requeridos"}
  


if __name__ == "__main__":
 app.run(debug = True)




