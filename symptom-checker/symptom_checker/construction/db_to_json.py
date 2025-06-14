import xml.etree.ElementTree as ET

import ujson

from symptom_checker.config import DATA_DIR
from symptom_checker.includes.db_processing import (
    process_disease,
    process_disease_genes,
    process_disease_symptoms,
)

json_kwargs = {"indent": 2}

print("Converting XML to JSON")

# parse in XML
with open(DATA_DIR / "raw" / "en_product1.xml", "r", encoding="ISO-8859-1") as file:
    diseases_xml = file.read()

with open(DATA_DIR / "raw" / "en_product4.xml", "r", encoding="ISO-8859-1") as file:
    disease_to_symptoms_xml = file.read()

with open(DATA_DIR / "raw" / "en_product6.xml", "r", encoding="ISO-8859-1") as file:
    disease_to_genes_xml = file.read()

# list of diseases
diseases_xml = ET.XML(diseases_xml).find("DisorderList")
# list of disorders and symptoms
disease_to_symptoms_xml = ET.XML(disease_to_symptoms_xml).find(
    "HPODisorderSetStatusList"
)
# list of disorders and genes
disease_to_genes_xml = ET.XML(disease_to_genes_xml).find("DisorderList")

# parse diseases XML
diseases = [process_disease(elem) for elem in diseases_xml]
# parse disease-symptoms XML
disease_to_symptoms = [
    process_disease_symptoms(elem) for elem in disease_to_symptoms_xml
]
disease_to_genes = [process_disease_genes(elem) for elem in disease_to_genes_xml]

# write out JSONs
with open(DATA_DIR / "intermediate" / "diseases.json", "w") as f:
    ujson.dump(diseases, f, **json_kwargs)

with open(DATA_DIR / "intermediate" / "disease_to_symptoms.json", "w") as f:
    ujson.dump(disease_to_symptoms, f, **json_kwargs)

with open(DATA_DIR / "intermediate" / "disease_to_genes.json", "w") as f:
    ujson.dump(disease_to_genes, f, **json_kwargs)
