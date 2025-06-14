from typing import Any, Dict

import ujson

from symptom_checker.config import DATA_DIR
from symptom_checker.includes.utils import invert_dict_of_lists

json_kwargs = {"indent": 2}

print("Making final database files")

# load mappings
with open(DATA_DIR / "intermediate" / "diseases.json", "r") as f:
    diseases = ujson.load(f)

with open(DATA_DIR / "intermediate" / "disease_to_symptoms.json", "r") as f:
    disease_to_symptoms = ujson.load(f)

with open(DATA_DIR / "intermediate" / "disease_to_genes.json", "r") as f:
    disease_to_genes = ujson.load(f)


def dict_without(dictionary: Dict[Any, Any], without: Any) -> Dict[Any, Any]:

    """
    Remove a key from a dictionary and return the copy without.
    """

    new = dictionary.copy()
    new.pop(without)

    return new


# construct ID-based mappings
disease_to_info_ids = {
    disease["disease_code"]: dict_without(disease, "disease_code")
    for disease in diseases
}

disease_to_symptoms_ids = {
    disease["disease_code"]: [
        symptom["symptom_hpo_id"] for symptom in disease["symptoms"]
    ]
    for disease in disease_to_symptoms
}

disease_to_symptoms_complete = {
    disease["disease_code"]: {
        symptom["symptom_hpo_id"]: dict_without(symptom, "symptom_hpo_id")
        for symptom in disease["symptoms"]
    }
    for disease in disease_to_symptoms
}

symptom_text_to_ids = {}

for disease in disease_to_symptoms:
    for symptom in disease["symptoms"]:
        symptom_id = symptom["symptom_hpo_id"]
        symptom_text = symptom["symptom_hpo_term"].lower()

        if symptom_text not in symptom_text_to_ids:
            symptom_text_to_ids[symptom_text] = {symptom_id}

        else:
            symptom_text_to_ids[symptom_text].add(symptom_id)

symptom_text_to_ids = {
    symptom_text: list(symptom_ids)
    for symptom_text, symptom_ids in symptom_text_to_ids.items()
}

disease_to_genes_ids = {
    disease["disease_code"]: disease["disease_genes"] for disease in disease_to_genes
}


# invert disease-symptoms mapping
symptoms_to_disease_ids = invert_dict_of_lists(disease_to_symptoms_ids)

with open(DATA_DIR / "processed" / "disease_to_info_ids.json", "w") as f:
    ujson.dump(disease_to_info_ids, f, **json_kwargs)

with open(DATA_DIR / "processed" / "symptoms_to_disease_ids.json", "w") as f:
    ujson.dump(symptoms_to_disease_ids, f, **json_kwargs)

with open(DATA_DIR / "processed" / "disease_to_symptoms_complete.json", "w") as f:
    ujson.dump(disease_to_symptoms_complete, f, **json_kwargs)

with open(DATA_DIR / "processed" / "symptom_text_to_ids.json", "w") as f:
    ujson.dump(symptom_text_to_ids, f, **json_kwargs)

with open(DATA_DIR / "processed" / "disease_to_genes_ids.json", "w") as f:
    ujson.dump(disease_to_genes_ids, f, **json_kwargs)
