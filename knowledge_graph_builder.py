import spacy
from fastcoref import spacy_component  # needed to add_pipe

from typing import List, Container

SP_MODEL = spacy.load('en_core_web_sm')
SP_MODEL.add_pipe(
    "fastcoref",
)


def prepocess_text(text: str) -> str:
    text = text.casefold()
    # TODO What else?
    return text


def get_corefs(text):
    # resolving coreferences
    docs = SP_MODEL.pipe(
        [text],
        component_cfg={"fastcoref": {'resolve_text': True}}
    )
    corefs_resolved_text = next(docs)._.resolved_text
    return corefs_resolved_text


def get_unique_nps(text):
    unique_nps = set()
    for np in SP_MODEL(text).noun_chunks:
        unique_nps.add(np.text)
    return unique_nps


def synonym_extraction(chunks: Container[str]) -> Container[str]:
    # TODO implement
    return chunks


def lexical_layers_step(text: str) -> List[str]:
    resolved_text = get_corefs(text)
    nps = get_unique_nps(resolved_text)
    synonyms = synonym_extraction(nps)


if __name__ == "__main__":
    text = "Dude, that kickflip was sick. I've never seen you do that by yourself before"
    text = prepocess_text(text)
    nps = lexical_layers_step(text)
    pass
    """"
    
Lexical Layers:
Term extraction: “get the terms that are of great importance to describe a domain”
Synonym Extraction: “get the synonyms from the list of extracted terms”, probably need to do coreference resolution here too

Determined learning process:
Concept Extraction: “the concepts are defined from the existing terms” - not sure what this means
Concept Hierarchy: “Finding the relationship IS-A. 
Non-taxonomic Relationship Discovery: “which relationships don’t fall under IS-A”
Axiom Extraction: ???? 


"""
