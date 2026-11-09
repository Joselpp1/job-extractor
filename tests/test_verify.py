from app.schemas import JobPosting, Skill
from app.verify import verify_posting, verify_skills

TEXT = "We need a developer with Python 3+ and experience\nin  FastAPI. Docker is a plus."


def test_keeps_skill_when_source_is_in_text():
    skills = [Skill(name="Python", source="Python 3+")]
    assert verify_skills(skills, TEXT) == skills


def test_ignores_case_and_extra_whitespace():
    # The text has a line break and a double space; the source has neither.
    skills = [Skill(name="FastAPI", source="EXPERIENCE in fastapi")]
    assert verify_skills(skills, TEXT) == skills


def test_discards_skill_with_invented_source():
    skills = [Skill(name="Kubernetes", source="Kubernetes experience")]
    assert verify_skills(skills, TEXT) == []


def test_discards_skill_with_blank_source():
    skills = [Skill(name="Anything", source="   ")]
    assert verify_skills(skills, TEXT) == []


def test_keeps_only_valid_skills_in_original_order():
    python = Skill(name="Python", source="Python 3+")
    fake = Skill(name="Java", source="Java Spring Boot")
    docker = Skill(name="Docker", source="Docker is a plus")
    assert verify_skills([python, fake, docker], TEXT) == [python, docker]


def test_verify_posting_filters_both_lists_and_keeps_other_fields():
    posting = JobPosting(
        title="Backend Dev",
        modality="remote",
        required_skills=[
            Skill(name="Python", source="Python 3+"),
            Skill(name="Java", source="Java Spring Boot"),
        ],
        nice_to_have_skills=[
            Skill(name="Docker", source="Docker is a plus"),
            Skill(name="AWS", source="AWS certification"),
        ],
    )

    result = verify_posting(posting, TEXT)

    assert [s.name for s in result.required_skills] == ["Python"]
    assert [s.name for s in result.nice_to_have_skills] == ["Docker"]
    assert result.title == "Backend Dev"
    assert result.modality == "remote"