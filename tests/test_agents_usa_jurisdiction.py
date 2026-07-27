"""
Acceptance tests (TDD) — USA jurisdiction-native agents.

Opus-owned CONTRACT. The USA deadline agent must be HONEST about the 50-state
reality: there is NO single federal statute of limitations, so it surfaces the
framework + common ranges + the UCC §2-725 anchor + "verify your state" — it must
NOT fabricate one authoritative computed deadline. Axes: shape · US-native ·
NO foreign residue (India / Singapore / UK).
"""

import inspect
import re


from ailawfirm_usa.agents import deadline_agent, drafting_agent, matter_agent

FOREIGN_RESIDUE = re.compile(
    r"\b1963\b|CrPC|BNSS|\bSLP\b|\b482\b|anticipatory\s+bail|indian-hc-drafting|"
    r"supreme-court-drafting|ailawfirm[-_]india|Limitation Act 1963|"
    r"Limitation Act 1959|Limitation Act 1980|ROC 2021|\bSGHC\b|ailawfirm[_-]singapore|"
    r"\bCPR\s+Part\b|ailawfirm[_-]uk",
    re.I,
)


def _flat(d: dict) -> str:
    return " ".join(str(v) for v in d.values())


class TestDeadlineUSA:
    def test_varies_by_state_framing(self):
        b = _flat(deadline_agent.handle("limitation period for a contract claim")).lower()
        assert "state" in b
        assert "varies" in b or "verify" in b

    def test_ucc_sale_of_goods_four_years(self):
        b = _flat(deadline_agent.handle("breach of a contract for the sale of goods"))
        assert "UCC" in b
        assert "4" in b
        assert "2-725" in b or "Article 2" in b

    def test_personal_injury_common_two_years(self):
        b = _flat(deadline_agent.handle("personal injury claim after a car accident")).lower()
        assert "2 year" in b or "two year" in b
        assert "state" in b

    def test_does_not_fabricate_single_deadline(self):
        # varies by state -> must carry the caveat, never present a lone precise date as authoritative
        b = _flat(deadline_agent.handle("contract breach on 12 January 2020")).lower()
        assert "state" in b and ("varies" in b or "verify" in b)

    def test_shape_keys(self):
        r = deadline_agent.handle("contract claim")
        for k in ("agent", "category", "period"):
            assert k in r

    def test_no_foreign_residue(self):
        for q in ["contract claim", "personal injury", "sale of goods", "recover property"]:
            assert not FOREIGN_RESIDUE.search(_flat(deadline_agent.handle(q))), q


class TestDraftingUSA:
    def test_complaint_recognised(self):
        r = drafting_agent.handle("draft a complaint for breach of contract")
        assert "complaint" in r.get("doc_type", "").lower()
        assert "draft-with-docx" in _flat(r).lower()

    def test_motion_to_dismiss_recognised(self):
        r = drafting_agent.handle("draft a motion to dismiss under FRCP 12(b)(6)")
        assert "motion" in r.get("doc_type", "").lower()

    def test_answer_recognised(self):
        r = drafting_agent.handle("draft an answer and counterclaim")
        assert "answer" in r.get("doc_type", "").lower()

    def test_shape_keys(self):
        r = drafting_agent.handle("draft a memorandum of law")
        assert "doc_type" in r and "suggested_skill" in r

    def test_no_foreign_residue(self):
        for q in ["draft a complaint", "draft a writ petition", "draft an SLP", "draft an originating claim"]:
            assert not FOREIGN_RESIDUE.search(_flat(drafting_agent.handle(q))), q


class TestMatterUSA:
    def test_store_path_is_usa(self):
        src = inspect.getsource(matter_agent)
        assert ".ailawfirm_usa" in src
        assert ".ailawfirm-india" not in src and ".ailawfirm_singapore" not in src

    def test_add_then_list_roundtrip(self, tmp_path, monkeypatch):
        store = tmp_path / "matters.json"
        monkeypatch.setattr(matter_agent, "_STORE_PATH", store, raising=False)
        matter_agent.handle("add matter Doe v Acme Corp")
        assert "Doe" in _flat(matter_agent.handle("list matters"))

    def test_shape_keys(self):
        assert matter_agent.handle("list matters").get("agent") == "matter_agent"

    def test_no_foreign_residue(self):
        for q in ["add matter ABC", "list matters", "status of XYZ"]:
            assert not FOREIGN_RESIDUE.search(_flat(matter_agent.handle(q))), q
