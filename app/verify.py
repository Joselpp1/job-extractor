from app.schemas import JobPosting, Skill

# Fields whose value must be copied word for word from the posting.
LITERAL_FIELDS = ("title", "company", "location", "salary", "contract_type", "modality_source")


def normalize(text: str) -> str:
    """Lowercase and collapse any whitespace (spaces, tabs, newlines) into single spaces."""
    return " ".join(text.casefold().split())


def appears_in(phrase: str, normalized_text: str) -> bool:
    """True if the phrase, once normalized, is a non-empty part of the normalized text."""
    normalized_phrase = normalize(phrase)
    return bool(normalized_phrase) and normalized_phrase in normalized_text


def verify_skills(skills: list[Skill], original_text: str) -> list[Skill]:
    """Keep only the skills whose `source` phrase really appears in the original text."""
    normalized_text = normalize(original_text)
    return [skill for skill in skills if appears_in(skill.source, normalized_text)]


def verify_posting(posting: JobPosting, original_text: str) -> JobPosting:
    """Return a copy of the posting where every untraceable value is removed."""
    normalized_text = normalize(original_text)
    updates: dict = {}

    for field in LITERAL_FIELDS:
        value = getattr(posting, field)
        if value is not None and not appears_in(value, normalized_text):
            updates[field] = None

    # modality is a label, not a quote: keep it only if its source phrase survived.
    modality_source = updates.get("modality_source", posting.modality_source)
    if modality_source is None:
        updates["modality"] = None

    updates["required_skills"] = verify_skills(posting.required_skills, original_text)
    updates["nice_to_have_skills"] = verify_skills(posting.nice_to_have_skills, original_text)
    return posting.model_copy(update=updates)