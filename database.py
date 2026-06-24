from pymongo import MongoClient

def get_db():
    
    url = "mongodb+srv://jean1234:jean5678@calificaapp.62l1sl2.mongodb.net/gestion_escolar?retryWrites=true&w=majority"
    
    client = MongoClient(url, tlsAllowInvalidCertificates=True)
    db = client["gestion_escolar"]
    return db