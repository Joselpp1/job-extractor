from app.schemas import JobPosting, Skill


def normalize(text: str) -> str:
    """Lowercase and collapse any whitespace (spaces, tabs, newlines) into single spaces."""
    return " ".join(text.casefold().split())


def verify_skills(skills: list[Skill], original_text: str) -> list[Skill]:
    """Keep only the skills whose `source` phrase really appears in the original text."""
    normalized_text = normalize(original_text)
    verified = []
    for skill in skills:
        normalized_source = normalize(skill.source)
        if normalized_source and normalized_source in normalized_text:
            verified.append(skill)
    return verified


def verify_posting(posting: JobPosting, original_text: str) -> JobPosting:
    """Return a copy of the posting with untraceable skills removed."""
    return posting.model_copy(
        update={
            "required_skills": verify_skills(posting.required_skills, original_text),
            "nice_to_have_skills": verify_skills(posting.nice_to_have_skills, original_text),
        }
    )