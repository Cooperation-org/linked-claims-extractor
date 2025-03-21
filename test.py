# import chromadb
# chroma_client = chromadb.Client()
# collection = chroma_client.create_collection(name="my_collection")
# collection.add(
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges"
#     ],
#     ids=["id1", "id2"]
# )
# results = collection.query(
#     query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )
# print(results)


import chromadb

client = chromadb.Client()

collections = client.list_collections()

for collection in collections:
    print(f"Collection Name: {collection.name}")