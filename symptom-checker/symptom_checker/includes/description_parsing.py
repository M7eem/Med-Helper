from typing import List

import scispacy
import spacy
import ujson
from pattern.en import singularize

from symptom_checker.config import DATA_DIR
from symptom_checker.includes.utils import (
    flatten_list_of_lists,
    remove_duplicates_in_order,
)

nlp = spacy.load("en_core_sci_sm")

CONVERT_PREVALENCE = {
    "Excluded": "Excluded (0%)",
    "Very rare": "Very rare (<4-1%)",
    "Occasional": "Occasional (29-5%)",
    "Frequent": "Frequent (79-30%)",
    "Very frequent": "Very frequent (99-80%)",
    "Obligate": "Obligate (100%)",
}

PREVALENCE_RANK = {
    "Excluded (0%)": -1,
    "Very rare (<4-1%)": 1,
    "Occasional (29-5%)": 2,
    "Frequent (79-30%)": 3,
    "Very frequent (99-80%)": 4,
    "Obligate (100%)": 5,
}

with open(DATA_DIR / "processed" / "disease_to_info_ids.json", "r") as f:
    disease_to_info_ids = ujson.load(f)

with open(DATA_DIR / "processed" / "symptoms_to_disease_ids.json", "r") as f:
    symptoms_to_disease_ids = ujson.load(f)

with open(DATA_DIR / "processed" / "disease_to_symptoms_complete.json", "r") as f:
    disease_to_symptoms_complete = ujson.load(f)

with open(DATA_DIR / "processed" / "symptom_text_to_ids.json", "r") as f:
    symptom_text_to_ids = ujson.load(f)

with open(DATA_DIR / "processed" / "disease_to_genes_ids.json", "r") as f:
    disease_to_genes_ids = ujson.load(f)


def get_symptoms(text: str) -> List[str]:

    noun_chunks = [phrase.text.lower() for phrase in nlp(text).noun_chunks]
    noun_chunks = remove_duplicates_in_order(noun_chunks)

    # include singulars
    singulars = [singularize(chunk) for chunk in noun_chunks]

    # merge chunks and singulars
    # https://stackoverflow.com/questions/3471999/how-do-i-merge-two-lists-into-a-single-list
    noun_chunks = [j for i in zip(noun_chunks, singulars) for j in i]

    noun_chunks = remove_duplicates_in_order(noun_chunks)

    return noun_chunks


def get_diseases(
    symptoms: List[str], min_frequency: str, sort_method: str
) -> List[Any]:

    symptoms = [symptom for symptom in symptoms if symptom in symptom_text_to_ids]

    # match symptoms to IDs
    symptom_ids = [symptom_text_to_ids.get(symptom) for symptom in symptoms]

    # removed non-matched terms
    symptom_ids = [symptom_id for symptom_id in symptom_ids if symptom_id is not None]

    # flatten list of lists
    symptom_ids = flatten_list_of_lists(symptom_ids)

    # remove any duplicate symptom IDs (if two text terms point to the same ID)
    symptom_ids = remove_duplicates_in_order(symptom_ids)

    # position of each symptom ID
    symptom_id_pos = dict(zip(symptom_ids, range(len(symptom_ids))))

    matched_diseases = {
        symptom_id: symptoms_to_disease_ids.get(symptom_id)
        for symptom_id in symptom_ids
    }

    # symptom info per matched disease
    matched_diseases_info = dict()

    disease_blacklist = set()

    min_frequency_rank = PREVALENCE_RANK[CONVERT_PREVALENCE[min_frequency]]

    for symptom_id, disease_ids in matched_diseases.items():

        for disease_id in disease_ids:

            disease_symptom_frequency = disease_to_symptoms_complete[disease_id][
                symptom_id
            ]["symptom_frequency"]

            disease_symptom_frequency_rank = PREVALENCE_RANK[disease_symptom_frequency]

            # if symptom not found in disease, blacklist the disease
            if disease_symptom_frequency_rank == -1:

                disease_blacklist.add(disease_id)

            # if frequency rank falls below minimum, skip
            if disease_symptom_frequency_rank < min_frequency_rank:

                continue

            # get official text term for symptom
            disease_symptom_hpo_term = disease_to_symptoms_complete[disease_id][
                symptom_id
            ]["symptom_hpo_term"]

            # construct symptom info object
            symptom_info = {
                "symptom_id": symptom_id,
                "symptom_hpo_term": disease_symptom_hpo_term,
                "symptom_frequency": disease_symptom_frequency,
            }

            # create disease if not exists
            if disease_id not in matched_diseases_info:

                matched_diseases_info[disease_id] = {
                    "disease": disease_to_info_ids[disease_id],
                    "disease_genes": disease_to_genes_ids.get(disease_id, []),
                    "matched_symptoms": [symptom_info],
                }

            # otherwise, append symptom to existing disease
            else:

                matched_diseases_info[disease_id]["matched_symptoms"].append(
                    symptom_info
                )

    # filter out blacklisted diseases
    matched_diseases_info = [
        disease_info
        for disease_id, disease_info in matched_diseases_info.items()
        if disease_id not in disease_blacklist
    ]

    # sort by number of matched symptoms (greatest first)
    if sort_method == "num_matched_symptoms":

        matched_diseases_info = sorted(
            matched_diseases_info,
            key=lambda disease_info: -len(disease_info["matched_symptoms"]),
        )

    # sort by position of the first-matched symptom in the text query
    elif sort_method == "first_matched_symptom":

        matched_diseases_info = sorted(
            matched_diseases_info,
            key=lambda disease_info: min(
                [
                    symptom_id_pos[symptom["symptom_id"]]
                    for symptom in disease_info["matched_symptoms"]
                ]
            ),
        )

    return matched_diseases_info
