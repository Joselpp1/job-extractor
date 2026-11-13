from app.schemas import JobPosting, Skill
from app.verify import verify_posting, verify_skills

TEXT = "We need a developer with Python 3+ and experience\nin  FastAPI. Docker is a plus."

POSTING_TEXT = (
    "Cargo: Desarrollador Backend Junior. Empresa: TechNova SAS. "
    "Modalidad: Remoto / Presencial. Ubicacion: Medellin. "
    "Salario a convenir. Contrato por obra o labor."
)


# --- Skills ---

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


def test_verify_posting_filters_both_skill_lists():
    posting = JobPosting(
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


# --- Literal fields ---

def test_keeps_literal_fields_that_appear_in_text():
    posting = JobPosting(
        title="Desarrollador Backend Junior",
        company="TechNova SAS",
        location="Medellin",
        salary="Salario a convenir",
        contract_type="obra o labor",
        modality_source="Remoto / Presencial",
    )

    result = verify_posting(posting, POSTING_TEXT)

    assert result.title == "Desarrollador Backend Junior"
    assert result.company == "TechNova SAS"
    assert result.location == "Medellin"
    assert result.salary == "Salario a convenir"
    assert result.contract_type == "obra o labor"
    assert result.modality_source == "Remoto / Presencial"


def test_removes_literal_fields_that_were_invented():
    posting = JobPosting(company="Google", salary="$3.000.000", contract_type="Término indefinido")

    result = verify_posting(posting, POSTING_TEXT)

    assert result.company is None
    assert result.salary is None
    assert result.contract_type is None


# --- Modality ---

def test_keeps_modality_with_traceable_source():
    posting = JobPosting(modality="remote", modality_source="Remoto")
    assert verify_posting(posting, POSTING_TEXT).modality == "remote"


def test_removes_modality_without_source():
    posting = JobPosting(modality="onsite")
    assert verify_posting(posting, POSTING_TEXT).modality is None


def test_removes_modality_when_source_is_invented():
    posting = JobPosting(modality="hybrid", modality_source="Modalidad híbrida")

    result = verify_posting(posting, POSTING_TEXT)

    assert result.modality is None
    assert result.modality_source is None