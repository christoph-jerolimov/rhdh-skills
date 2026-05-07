"""Tests for review-pr skill structure and content validation."""

import re

import pytest
import yaml

REVIEW_PR_SKILL_DIR_NAME = "rhdh-pr-review"


@pytest.fixture
def review_pr_skill_dir(skill_root):
    """Return the review-pr skill directory path."""
    return skill_root / "skills" / REVIEW_PR_SKILL_DIR_NAME


class TestReviewPrSkillMd:
    """Test that review-pr SKILL.md has required structure."""

    @pytest.fixture
    def skill_md(self, review_pr_skill_dir):
        """Load review-pr SKILL.md content."""
        skill_path = review_pr_skill_dir / "SKILL.md"
        assert skill_path.exists(), "skills/review-pr/SKILL.md must exist"
        return skill_path.read_text(encoding="utf-8")

    @pytest.fixture
    def skill_frontmatter(self, skill_md):
        """Parse YAML frontmatter from SKILL.md."""
        match = re.match(r"^---\n(.*?)\n---", skill_md, re.DOTALL)
        if not match:
            pytest.fail("SKILL.md missing YAML frontmatter")
        return yaml.safe_load(match.group(1))

    def test_skill_md_exists(self, review_pr_skill_dir):
        """SKILL.md must exist in skills/review-pr/."""
        assert (review_pr_skill_dir / "SKILL.md").exists()

    def test_frontmatter_has_name(self, skill_frontmatter):
        """SKILL.md must have name field set to review-pr."""
        assert "name" in skill_frontmatter
        assert skill_frontmatter["name"] == "rhdh-pr-review"

    def test_frontmatter_has_description(self, skill_frontmatter):
        """SKILL.md must have a description field."""
        assert "description" in skill_frontmatter
        assert len(skill_frontmatter["description"]) > 20

    def test_has_essential_principles(self, skill_md):
        """SKILL.md must have <essential_principles> section."""
        assert "<essential_principles>" in skill_md
        assert "</essential_principles>" in skill_md

    def test_has_intake_section(self, skill_md):
        """SKILL.md must have <intake> section."""
        assert "<intake>" in skill_md
        assert "</intake>" in skill_md

    def test_has_routing_section(self, skill_md):
        """SKILL.md must have <routing> section with table."""
        assert "<routing>" in skill_md
        assert "</routing>" in skill_md
        assert "| Response |" in skill_md or "| Intent |" in skill_md

    def test_has_success_criteria(self, skill_md):
        """SKILL.md must have <success_criteria> section."""
        assert "<success_criteria>" in skill_md
        assert "</success_criteria>" in skill_md

    def test_references_workflow(self, skill_md):
        """SKILL.md should reference the workflow file."""
        assert "workflows/" in skill_md


class TestReviewPrWorkflows:
    """Test that review-pr workflow files have required structure."""

    @pytest.fixture
    def review_pr_skill_dir(self, skill_root):
        return skill_root / "skills" / REVIEW_PR_SKILL_DIR_NAME

    @pytest.fixture
    def workflow_file(self, review_pr_skill_dir):
        """Load the review-operator-pr workflow."""
        path = review_pr_skill_dir / "workflows" / "review-operator-pr.md"
        assert path.exists(), "workflows/review-operator-pr.md must exist"
        return path.read_text(encoding="utf-8")

    def test_workflow_exists(self, review_pr_skill_dir):
        """review-operator-pr.md must exist."""
        assert (
            review_pr_skill_dir / "workflows" / "review-operator-pr.md"
        ).exists()

    def test_workflow_has_required_reading_or_prerequisites(self, workflow_file):
        """Workflow must have required_reading or prerequisites section."""
        assert "<required_reading>" in workflow_file or "<prerequisites>" in workflow_file

    def test_workflow_has_process(self, workflow_file):
        """Workflow must have <process> section."""
        assert "<process>" in workflow_file
        assert "</process>" in workflow_file

    def test_workflow_has_success_criteria(self, workflow_file):
        """Workflow must have <success_criteria> section."""
        assert "<success_criteria>" in workflow_file
        assert "</success_criteria>" in workflow_file

    def test_workflow_has_tracking(self, workflow_file):
        """Workflow must have <tracking> section for activity logging."""
        assert "<tracking>" in workflow_file
        assert "</tracking>" in workflow_file

    def test_workflow_mentions_gh_cli(self, workflow_file):
        """Workflow should use gh CLI for PR data."""
        assert "gh pr" in workflow_file

    def test_workflow_mentions_oc_commands(self, workflow_file):
        """Workflow should use oc CLI for cluster operations."""
        assert "oc " in workflow_file

    def test_workflow_mentions_image_swap(self, workflow_file):
        """Workflow should include image swap commands."""
        assert "oc set image" in workflow_file or "oc patch" in workflow_file


class TestReviewPrReferences:
    """Test that review-pr reference files exist and have required content."""

    @pytest.fixture
    def review_pr_skill_dir(self, skill_root):
        return skill_root / "skills" / REVIEW_PR_SKILL_DIR_NAME

    @pytest.fixture
    def reference_file(self, review_pr_skill_dir):
        """Load the operator-pr-images reference."""
        path = review_pr_skill_dir / "references" / "operator-pr-images.md"
        assert path.exists(), "references/operator-pr-images.md must exist"
        return path.read_text(encoding="utf-8")

    def test_reference_exists(self, review_pr_skill_dir):
        """operator-pr-images.md must exist."""
        assert (
            review_pr_skill_dir / "references" / "operator-pr-images.md"
        ).exists()

    def test_reference_has_xml_sections(self, reference_file):
        """Reference file should use XML tags for structure."""
        has_xml = bool(re.search(r"<\w+>", reference_file))
        assert has_xml, "Reference file should use XML tags"

    def test_reference_mentions_quay(self, reference_file):
        """Reference must mention the quay.io registry."""
        assert "quay.io" in reference_file

    def test_reference_mentions_image_naming(self, reference_file):
        """Reference must document the PR image naming convention."""
        assert "pr-" in reference_file.lower() or "PR" in reference_file


class TestOrchestratorRoutesToReviewPr:
    """Test that the orchestrator SKILL.md routes to review-pr."""

    @pytest.fixture
    def orchestrator_md(self, skills_dir):
        """Load orchestrator SKILL.md content."""
        return (skills_dir / "SKILL.md").read_text(encoding="utf-8")

    def test_orchestrator_mentions_review_pr(self, orchestrator_md):
        """Orchestrator SKILL.md must mention review-pr."""
        assert "rhdh-pr-review" in orchestrator_md

    def test_orchestrator_skills_index_has_review_pr(self, orchestrator_md):
        """Orchestrator skills_index must include review-pr entry."""
        skills_index_match = re.search(
            r"<skills_index>(.*?)</skills_index>", orchestrator_md, re.DOTALL
        )
        assert skills_index_match, "Orchestrator must have <skills_index> section"
        assert "rhdh-pr-review" in skills_index_match.group(1)
