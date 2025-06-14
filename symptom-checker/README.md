# symptom-checker

Given a natural language query, extract symptom terms and match them to possible diseases.



## How it works

1. Make the database:
   1. Sources of data:
      1. We need to match phenotypes (e.g. symptoms) to diseases, so we use the "Rare diseases with associated phenotypes" dataset from http://www.orphadata.org/cgi-bin/index.php
      2. We'd also like to find genes associated with rare diseases, so we use the "Genes associated with rare diseases" dataset from Orphanet
      3. We'd also like to have a comprehensive set of disease info in general, so we use the "Cross-referencing of rare diseases" dataset from Orphanet
   2. Preprocessing:
      1. Extract a list of all symptom terms from the disease-phenotypes dataset to use for filtering
      2. Convert all datasets to JSON for ease of use
      3. Do any additional key-mapping for final use
2. Build the server:
   1. Take an input sentence, segment with NLTK/SpaCy, extract nouns, and search for conditions as a Django endpoint
   2. Allow for basic sorting/filtering on conditions



## Getting started

First, clone the repo:

```bash
git clone git@github.com:kevinhu/symptom-checker.git
```

Next, install dependencies.

```bash
# if using Poetry:
poetry install

# if using Pip:
pip3 install -r requirements.txt
```

Note: `mysql` must also be installed for the `pattern` package, which is used to convert plural symptoms to singular ones. On macOS, this can be done using `brew install mysql`. On Debian/Ubuntu, try `sudo apt-get install libmysqlclient-dev`.

Installing via Poetry will automatically create a virtual environment that can be accessed with `poetry shell` or executed in with `poetry run <command>`. If using Pip, you may want to manually create one before installing, for instance with `python3 -m venv symptom-checker`. 

The final JSON dictionaries with disease information and symptom+gene associations are included within the repository. If you would like to regenerate them on your own, run

```bash
# fetch files (originally XMLs)
python ./symptom_checker/construction/fetch_db.py
# convert to intermediate JSONs
python ./symptom_checker/construction/db_to_json.py
# make final database files
python ./symptom_checker/construction/finalize_db.py
```

Finally, to start the server, run

```bash
cd symptom_checker/server && gunicorn server.wsgi
```

This will start the server on `http://localhost:8000` by default with the endpoint of interest at `http://localhost:8000/check_symptoms`, accessible via POST. Note that this takes a couple of seconds because the server has to load a relatively large NLP model used by Scapy.

The parameters for the endpoint (url-encoded) are as follows:

- `description` (required): the plaintext query to analyze.
- `min_frequency`: the minimum frequency of a symptom in a disease to consider. Case-sensitive options include "Very rare", "Occasional", "Frequent", "Very frequent", and "Obligate", in order of exclusivity. If not specified, defaults to "Very rare".
- `sort_method` (required): how to sort returned diseases. Options are "first_matched_symptom" (show diseases in order of position of first matched symptom in text) and "num_matched_symptoms" (number of supplied symptoms matching the disease).

Given valid parameters, the endpoint will return a JSON response object with the following structure:

```
{
  "symptoms": [<list of matched symptoms>, ...],
  "diseases": [
    {
      "disease": {
        "disease_link": <disease_link>,
        "disease_name": <disease_name>,
        "disease_synonyms": [<alternative names for the disease>, ...],
        "disease_type": <disease_type>,
        "disease_group": <disease_group>,
        "disease_summary": <disease_summary>,
      	"disease_genes": [
      	  {
            "gene_source": <gene_source>,
            "gene_name": <gene_source>,
            "gene_symbol": <gene_symbol>,
            "gene_synonyms": [<synonymous genes>, ...],
            "gene_type": <gene_type>,
            "gene_loci": [<loci>, ...],
            "gene_association_type": <gene_association_type>,
            "gene_association_status": <gene_association_status>
      	  }, ...
      	],
      	"disease_references": [
      	  {
            "reference_source": <reference_source>,
            "reference_reference": <reference identifier>,
            "reference_relation": <reference_relation>,
            "reference_icd_relation": <reference_icd_relation>,
            "reference_validation": <reference_validation>
           }, ...
      	],
    	"matched_symptoms": [
    	  {
            "symptom_id": <symptom_id>,
            "symptom_hpo_term": <symptom text name>,
            "symptom_frequency": <symptom frequency in disease>
          }, ...
  	]
      }
    }
  ]
}
```





The endpoint is accessible via methods such as `curl`. For instance, use

```bash
curl \
	-X POST \
	--data-urlencode "description=microencephaly, cataracts, and autophagic vacuoles" \
	--data-urlencode "min_frequency=Occasional" \
	--data-urlencode "sort_method=num_matched_symptoms" \
	localhost:8000/check_symptoms/
```



## Test descriptions

```
""
"."
" "
"The patient had a seizure" # single symptom
"The patient has seizures and autism" # plurals + multiple symptoms
"The patient has seizures and seizures and autism" # more symptoms, one repeated
"The patient has seizures, autism, and corneal dystrophy" # multi-word symptom
"The patient has seizures but no autism" # negative (does not work)
"The patient has seizures but not autism" # negative (does not work)
"Seizures, autism, microcephaly" # list of symptoms
"Seizures, seizures, seizures" # repeated symptoms
```



## Some considerations

- Attempted to deploy to Heroku, but memory usage of NLP modules was too high (about 1.5GB)

- Behavior of the symptom matching:

  - There's also an `Excluded` disease-symptom frequency term, which presumably means that the presence of a symptom excludes the possibility of that disease being present. Current behavior of the filtering algorithm is to exclude diseases if any such symptom is found.
  - The `sort_method=num_matched_symptoms` takes into account the raw number of matched symptoms and not possible frequency. Intuitively, we'd want to rank a disease matched with "obligated+obligate" symptoms higher than one with "occasional+frequent" ones, but this would require an additional scoring system to be built in.
  - Queries could contain negative qualifiers such as "The patient has seizures but not autism", but the current behavior of the parser is to just extract noun chunks alone. Some more specific NLP would be required to filter these out.
  - Queries often have plural forms of symptoms, but the database used appears to only include singular forms (i.e. "seizures" versus "seizure"). Right now, we use the `pattern` library to singularize these forms while also including the plural ones just in case.

  
