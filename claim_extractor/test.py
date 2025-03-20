from claim_extractor import ClaimExtractor
import pprint
import json
import chromadb


extractor = ClaimExtractor()
# read text from file
with open("/Users/ziad/Downloads/out-claim/output_sentences.txt", "r", encoding="utf-8") as f:
    text_file = f.read()

text = """In 2023, Apple announced the release of the iPhone 15, which features an OLED display and a battery that lasts up to 48 hours. However, some experts claim that these features are exaggerated.

On the other hand, reports suggest that Google is developing a new operating system based on artificial intelligence. This system, called "Google Mind," is expected to change the way we interact with smart devices.

In the field of medicine, a recent study has shown that consuming dark chocolate can improve heart health. However, doctors warn against excessive consumption due to its high calorie content.

Finally, NASA announced the discovery of a new Earth-like planet in a distant solar system. This planet, named "Kepler-452b," could potentially support life."""


result = extractor.extract_claims(text_file)
print(result)
# save result to json
if result:
    with open("/Users/ziad/Downloads/linked-claims-extractor/claim_extractor/output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
# pprint.pprint(result)
# print(type(result))




# url = 'https://www.trustpilot.com/reviews/67d1b141640f86c138b233b8'
# result = extractor.extract_claims_from_url(url)
# pprint.pprint(result)


# from claim_extractor.schemas.loader import load_schema_info, LINKED_TRUST, OPEN_CRED, LINKED_CLAIM

# for schema_id in [LINKED_TRUST, LINKED_CLAIM]:
#     schema, meta = load_schema_info(schema_id)
#     print(schema)
#     print(meta)

# # save each result in our chromadb
# client = chromadb.PersistentClient()

# collection = client.get_or_create_collection(name="claims")

# for i, claim in enumerate(result):
#     collection.add(
#         documents=[claim],
#         metadatas=[{
#             "id": i
#         }]
#     )


