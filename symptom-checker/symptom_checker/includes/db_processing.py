import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Union


def process_disease(disease_elem: ET.XML) -> Dict[str, Union[str, List[Any]]]:

    """
    Process a disease element in the <DisorderList> group for en_product1.
    Args:
        disease_elem:
            ElementTree object corresponding to the disease.
    Returns:
        dictionary of disease attributes
    """

    disease_code = disease_elem.find("OrphaCode").text
    disease_link = disease_elem.find("ExpertLink").text
    disease_name = disease_elem.find("Name").text

    disease_synonyms = [elem.text for elem in disease_elem.find("SynonymList")]

    disease_type = disease_elem.find("DisorderType/Name").text
    disease_group = disease_elem.find("DisorderGroup/Name").text

    def process_reference(reference_elem: ET.XML) -> Dict[str, Union[str, List[Any]]]:

        """
        Process a disease reference element.
        """

        reference_source = reference_elem.find("Source").text
        reference_reference = reference_elem.find("Reference").text

        # get nested relation and validation info
        relation_elem, icd_relation_elem, validation_elem = (
            reference_elem.find("DisorderMappingRelation/Name"),
            reference_elem.find("DisorderMappingICDRelation/Name"),
            reference_elem.find("DisorderMappingValidationStatus/Name"),
        )

        reference_relation = ""
        reference_icd_relation = ""
        reference_validation = ""

        # overwrite values if exists
        if relation_elem is not None:
            reference_relation = relation_elem.text

        if icd_relation_elem is not None:
            reference_icd_relation = icd_relation_elem.text

        if validation_elem is not None:
            reference_validation = validation_elem.text

        return {
            "reference_source": reference_source,
            "reference_reference": reference_reference,
            "reference_relation": reference_relation,
            "reference_icd_relation": reference_icd_relation,
            "reference_validation": reference_validation,
        }

    references_elem = disease_elem.find("ExternalReferenceList")
    disease_references = [process_reference(elem) for elem in references_elem]

    disease_summary_elem = disease_elem.find(
        "SummaryInformationList/SummaryInformation/TextSectionList/TextSection/Contents"
    )

    disease_summary = ""

    # overwrite if exists
    if disease_summary_elem is not None:

        disease_summary = disease_summary_elem.text

    return {
        "disease_code": disease_code,
        "disease_link": disease_link,
        "disease_name": disease_name,
        "disease_synonyms": disease_synonyms,
        "disease_type": disease_type,
        "disease_group": disease_group,
        "disease_references": disease_references,
        "disease_summary": disease_summary,
    }


def process_disease_symptoms(disease_elem: ET.XML) -> Dict[str, Union[str, List[Any]]]:

    """
    Process a disease-symptoms element in the <DisorderList> group for en_product4.
    Args:
        disease_elem:
            ElementTree object corresponding to the disease and symptoms.
    Returns:
        dictionary of disease attributes and symptoms
    """

    disease_id = disease_elem.attrib["id"]

    # validation and source
    disease_validation_status = disease_elem.find("ValidationStatus").text
    disease_validation_online = disease_elem.find("Online").text
    disease_validation_date = disease_elem.find("ValidationDate").text
    disease_source = disease_elem.find("Source").text

    # disorder element
    disorder_elem = disease_elem.find("Disorder")

    disease_code = disorder_elem.find("OrphaCode").text
    disease_link = disorder_elem.find("ExpertLink").text
    disease_name = disorder_elem.find("Name").text
    disease_type = disorder_elem.find("DisorderType/Name").text
    disease_group = disorder_elem.find("DisorderGroup/Name").text

    symptoms_elem = disorder_elem.find("HPODisorderAssociationList")

    def process_symptom(symptom_elem: ET.XML) -> Dict[str, Union[str, List[Any]]]:

        """
        Process a disease symptom element.
        """

        symptom_hpo_elem = symptom_elem.find("HPO")

        symptom_hpo_id = symptom_hpo_elem.find("HPOId").text
        symptom_hpo_term = symptom_hpo_elem.find("HPOTerm").text

        symptom_frequency = symptom_elem.find("HPOFrequency/Name").text
        symptom_criteria = symptom_elem.find("DiagnosticCriteria").text

        return {
            "symptom_hpo_id": symptom_hpo_id,
            "symptom_hpo_term": symptom_hpo_term,
            "symptom_frequency": symptom_frequency,
            "symptom_criteria": symptom_criteria,
        }

    symptoms = [process_symptom(elem) for elem in symptoms_elem]

    return {
        "disease_id": disease_id,
        "disease_validation_status": disease_validation_status,
        "disease_validation_online": disease_validation_online,
        "disease_validation_date": disease_validation_date,
        "disease_source": disease_source,
        "disease_code": disease_code,
        "disease_link": disease_link,
        "disease_name": disease_name,
        "disease_type": disease_type,
        "disease_group": disease_group,
        "symptoms": symptoms,
    }


def process_disease_genes(disease_elem: ET.XML) -> Dict[str, Union[str, List[Any]]]:

    """
    Process a disease-genes element in the <DisorderList> group for en_product6.
    Args:
        disease_elem:
            ElementTree object corresponding to the disease and genes.
    Returns:
        dictionary of disease attributes and genes
    """

    disease_id = disease_elem.attrib["id"]
    disease_code = disease_elem.find("OrphaCode").text
    disease_link = disease_elem.find("ExpertLink").text
    disease_name = disease_elem.find("Name").text
    disease_type = disease_elem.find("DisorderType/Name").text
    disease_group = disease_elem.find("DisorderGroup/Name").text

    def process_gene(gene_association_elem):

        """
        Process a disease gene element.
        """

        gene_source = gene_association_elem.find("SourceOfValidation").text
        gene_elem = gene_association_elem.find("Gene")
        gene_name = gene_elem.find("Name").text
        gene_symbol = gene_elem.find("Symbol").text
        gene_synonyms = [elem.text for elem in gene_elem.find("SynonymList")]
        gene_type = gene_elem.find("GeneType/Name").text

        gene_external_references = [
            {
                "source": elem.find("Source").text,
                "reference": elem.find("Reference").text,
            }
            for elem in gene_elem.find("ExternalReferenceList")
        ]

        gene_loci = [
            elem.find("GeneLocus").text for elem in gene_elem.find("LocusList")
        ]

        gene_association_type_elem, gene_association_status_elem = (
            gene_elem.find("DisorderGeneAssociationType/Name"),
            gene_elem.find("DisorderGeneAssociationStatus/Name"),
        )

        gene_association_type = ""
        gene_association_status = ""

        # overwrite if exists
        if gene_association_type_elem is not None:
            gene_association_type = gene_association_type_elem.text

        if gene_association_status_elem is not None:
            gene_association_status = gene_association_status_elem.text

        return {
            "gene_source": gene_source,
            "gene_name": gene_name,
            "gene_symbol": gene_symbol,
            "gene_synonyms": gene_synonyms,
            "gene_type": gene_type,
            "gene_loci": gene_loci,
            "gene_association_type": gene_association_type,
            "gene_association_status": gene_association_status,
        }

    disease_genes = [
        process_gene(elem) for elem in disease_elem.find("DisorderGeneAssociationList")
    ]

    return {
        "disease_id": disease_id,
        "disease_code": disease_code,
        "disease_link": disease_link,
        "disease_name": disease_name,
        "disease_type": disease_type,
        "disease_group": disease_group,
        "disease_genes": disease_genes,
    }
