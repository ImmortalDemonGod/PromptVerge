# FILE: cultivation/systems/PromptVerge/promptverge/flows/knowledge_workflow.py
from functools import lru_cache
from typing import List, Tuple
from prefect import flow, task
from marvin import fn
import spacy
from zshot import PipelineConfig
from zshot.knowledge_extractor import KnowGL
from .. import schemas, prompts

@lru_cache(maxsize=1)
def _get_nlp_pipeline():
    """
    Loads and caches the spaCy/zShot NLP pipeline to avoid reloading on every call.
    """
    # 1. Initialize the base spaCy pipeline.
    #    'en_core_web_sm' is a small, efficient English model.
    nlp = spacy.load("en_core_web_sm")

    # 2. Configure and add the zShot component for knowledge extraction.
    #    KnowGL is a good general-purpose model for this task.
    config = PipelineConfig(
        knowledge_extractor=KnowGL(),
    )
    nlp.add_pipe("zshot", config=config, last=True)
    return nlp


@task
def extract_kg_triples(paper_content: str) -> List[Tuple[str, str, str]]:
    """
    Extracts Knowledge Graph triples from text using a cached zShot/spaCy pipeline.
    This replaces the TD-002 placeholder with a live implementation.
    """
    # 1. Get the cached NLP pipeline.
    nlp = _get_nlp_pipeline()

    # 2. Process the input text through the full pipeline.
    doc = nlp(paper_content)

    # 3. Extract and format the triples into the desired (head, relation, tail) format.
    #    zShot stores its output in the `doc._.relations` custom attribute.
    extracted_triples = []
    if doc._.relations:
        for relation in doc._.relations:
            # Ensure start and end spans are not empty
            if relation.start and relation.end:
                # The zshot Span object contains start/end character indices and the entity label.
                # To get the actual text of the entity, we slice the original doc.
                head = doc.text[relation.start.start:relation.start.end]
                tail = doc.text[relation.end.start:relation.end.end]
                label = relation.relation.name
                extracted_triples.append((head, label, tail))

    return extracted_triples

@fn(prompt=prompts.PROMPT_GENERATE_QUIZ)
def generate_quiz(kg_triples_str: str) -> schemas.KnowledgeGraphQuiz:
    """
    Generates a quiz based on the provided knowledge graph triples.
    Marvin will now use the prompt defined in `promptverge/prompts.py`
    to execute this function with a live API call.
    """
    # The function body is now intentionally empty.
    pass

# --- Step 3: Workflow Orchestration ---

@flow(name="Knowledge Workflow")
def run_knowledge_flow(paper_content: str) -> schemas.KnowledgeGraphQuiz:
    """
    Orchestrates the full workflow from a scientific paper to a quiz.
    """
    # 1. Extract structured data using live zShot/spaCy pipeline
    triples = extract_kg_triples(paper_content)

    # Format triples as a string for the prompt context
    triples_str = "\n".join([f"- {t}" for t in triples])

    # 2. Generate the final artifact using the structured data
    quiz = generate_quiz(triples_str)

    return quiz
