"""
Ontology module — AI Brain · USA · Solo · v0.1

Defines the core enums for US legal practice:
- USState: all 50 states + DC + territories
- MatterType: federal + state case types
- USCourt: federal court hierarchy + state generic slots
- USStatute: federal + key state statutes
- USBarRule: ABA Model Rules + ethics opinions
- Matter: core case dataclass
- Citation: Bluebook citation dataclass

v0.1 = Federal-focused. State-specific procedural detail deferred to v0.2+.
PROVENANCE: CITED from usa/_research/ files.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class USState(Enum):
    """All 50 states + DC + territories — placeholder enum for v0.1.
    v0.2+ adds per-state procedural depth. PROVENANCE: CITED:01-court-hierarchy.md"""

    AL = "Alabama"
    AK = "Alaska"
    AZ = "Arizona"
    AR = "Arkansas"
    CA = "California"
    CO = "Colorado"
    CT = "Connecticut"
    DE = "Delaware"
    FL = "Florida"
    GA = "Georgia"
    HI = "Hawaii"
    ID = "Idaho"
    IL = "Illinois"
    IN = "Indiana"
    IA = "Iowa"
    KS = "Kansas"
    KY = "Kentucky"
    LA = "Louisiana"
    ME = "Maine"
    MD = "Maryland"
    MA = "Massachusetts"
    MI = "Michigan"
    MN = "Minnesota"
    MS = "Mississippi"
    MO = "Missouri"
    MT = "Montana"
    NE = "Nebraska"
    NV = "Nevada"
    NH = "New Hampshire"
    NJ = "New Jersey"
    NM = "New Mexico"
    NY = "New York"
    NC = "North Carolina"
    ND = "North Dakota"
    OH = "Ohio"
    OK = "Oklahoma"
    OR = "Oregon"
    PA = "Pennsylvania"
    RI = "Rhode Island"
    SC = "South Carolina"
    SD = "South Dakota"
    TN = "Tennessee"
    TX = "Texas"
    UT = "Utah"
    VT = "Vermont"
    VA = "Virginia"
    WA = "Washington"
    WV = "West Virginia"
    WI = "Wisconsin"
    WY = "Wyoming"
    DC = "District of Columbia"
    PR = "Puerto Rico"
    VI = "U.S. Virgin Islands"
    GU = "Guam"
    OTHER = "Other state/territory"


class MatterType(Enum):
    """US legal matter type codes. PROVENANCE: CITED:02-court-rules-civil.md, 03-court-rules-criminal.md"""

    # Federal
    FEDERAL_CIVIL = "Federal Civil Action"
    FEDERAL_CRIMINAL = "Federal Criminal Case"
    FEDERAL_BANKRUPTCY_7 = "Chapter 7 Bankruptcy"
    FEDERAL_BANKRUPTCY_11 = "Chapter 11 Bankruptcy"
    FEDERAL_BANKRUPTCY_13 = "Chapter 13 Bankruptcy"
    FEDERAL_IMMIGRATION = "Federal Immigration Matter"
    FEDERAL_PATENT = "Patent Litigation"
    FEDERAL_COPYRIGHT = "Copyright Infringement"
    FEDERAL_TRADEMARK = "Trademark Action"
    FEDERAL_SEC_ENFORCEMENT = "SEC Enforcement Action"
    FEDERAL_ANTITRUST = "Antitrust Action"
    FEDERAL_TAX = "Federal Tax Matter"
    FEDERAL_ADMIRALTY = "Admiralty / Maritime"
    # State (generic — state-specific in v0.2+)
    STATE_CIVIL = "State Civil Action"
    STATE_CRIMINAL = "State Criminal Case"
    STATE_FAMILY = "State Family Matter"
    STATE_PROBATE = "State Probate"
    STATE_REAL_ESTATE = "State Real Estate Transaction"
    # ADR
    AAA_ARBITRATION = "AAA Arbitration"
    JAMS_ARBITRATION = "JAMS Arbitration"
    FINRA_ARBITRATION = "FINRA Arbitration"
    MEDIATION = "Mediation"
    OTHER = "Other"


class USCourt(Enum):
    """US court hierarchy — Federal + State generic slots.
    PROVENANCE: CITED:01-court-hierarchy.md"""

    # Federal — apex
    SCOTUS = "Supreme Court of the United States"
    # Federal — circuit courts (13 circuits)
    FED_CIRCUIT_1 = "U.S. Court of Appeals for the First Circuit"
    FED_CIRCUIT_2 = "U.S. Court of Appeals for the Second Circuit"
    FED_CIRCUIT_3 = "U.S. Court of Appeals for the Third Circuit"
    FED_CIRCUIT_4 = "U.S. Court of Appeals for the Fourth Circuit"
    FED_CIRCUIT_5 = "U.S. Court of Appeals for the Fifth Circuit"
    FED_CIRCUIT_6 = "U.S. Court of Appeals for the Sixth Circuit"
    FED_CIRCUIT_7 = "U.S. Court of Appeals for the Seventh Circuit"
    FED_CIRCUIT_8 = "U.S. Court of Appeals for the Eighth Circuit"
    FED_CIRCUIT_9 = "U.S. Court of Appeals for the Ninth Circuit"
    FED_CIRCUIT_10 = "U.S. Court of Appeals for the Tenth Circuit"
    FED_CIRCUIT_11 = "U.S. Court of Appeals for the Eleventh Circuit"
    FED_CIRCUIT_DC = "U.S. Court of Appeals for the D.C. Circuit"
    FED_CIRCUIT_FEDERAL = "U.S. Court of Appeals for the Federal Circuit"
    # Federal — trial
    FED_DISTRICT = "U.S. District Court (94 districts — specify in matter)"
    FED_BANKRUPTCY = "U.S. Bankruptcy Court"
    FED_TAX = "U.S. Tax Court"
    FED_CLAIMS = "U.S. Court of Federal Claims"
    FED_INTL_TRADE = "U.S. Court of International Trade"
    # Federal — specialized
    FED_MAGISTRATE = "U.S. Magistrate Court"
    FED_FISA = "Foreign Intelligence Surveillance Court"
    # State — generic (v0.2+ per state)
    STATE_SUPREME = "State Supreme Court (specify state)"
    STATE_APPELLATE = "State Appellate Court (specify state)"
    STATE_TRIAL = "State Trial Court (specify state)"
    OTHER = "Other"


class USStatute(Enum):
    """US statute registry — Federal + key state + currency warnings.
    PROVENANCE: CITED:04-07 statute research files"""

    # Constitutional
    US_CONSTITUTION = "U.S. Constitution"
    # Federal procedural
    FRCP = "Federal Rules of Civil Procedure"
    FRCRP = "Federal Rules of Criminal Procedure"
    FRE = "Federal Rules of Evidence"
    FRAP = "Federal Rules of Appellate Procedure"
    FRBP = "Federal Rules of Bankruptcy Procedure"
    # Federal statutes
    FAA = "Federal Arbitration Act (9 U.S.C.)"
    BANKRUPTCY_CODE = "Bankruptcy Code (11 U.S.C.)"
    PATENT_ACT = "Patent Act (35 U.S.C.)"
    COPYRIGHT_ACT = "Copyright Act (17 U.S.C.)"
    SHERMAN_ACT = "Sherman Antitrust Act (15 U.S.C. §§ 1-7)"
    CLAYTON_ACT = "Clayton Antitrust Act (15 U.S.C. §§ 12-27)"
    FTC_ACT = "Federal Trade Commission Act (15 U.S.C. §§ 41-58)"
    SECURITIES_ACT_1933 = "Securities Act of 1933"
    SECURITIES_EXCHANGE_ACT_1934 = "Securities Exchange Act of 1934"
    INVESTMENT_ADVISERS_ACT = "Investment Advisers Act of 1940"
    IRC = "Internal Revenue Code (26 U.S.C.)"
    ECPA = "Electronic Communications Privacy Act"
    CFAA = "Computer Fraud and Abuse Act (18 U.S.C. § 1030)"
    BSA = "Bank Secrecy Act"
    CTA = "Corporate Transparency Act — FinCEN (CURRENCY: rolling enforcement)"
    ADA = "Americans with Disabilities Act"
    TITLE_VII = "Title VII Civil Rights Act of 1964"
    ADEA = "Age Discrimination in Employment Act"
    FLSA = "Fair Labor Standards Act"
    FMLA = "Family and Medical Leave Act"
    ERISA = "Employee Retirement Income Security Act"
    CLEAN_WATER_ACT = "Clean Water Act"
    CLEAN_AIR_ACT = "Clean Air Act"
    CERCLA = "Comprehensive Environmental Response, Compensation, and Liability Act"
    FOIA = "Freedom of Information Act"
    APA = "Administrative Procedure Act"
    LANHAM_ACT = "Lanham Act (Trademark) (15 U.S.C. §§ 1051-1127)"
    DMCA = "Digital Millennium Copyright Act"
    # State data protection (sample — CITED:04-statute-data-protection.md)
    CCPA_CPRA = "California Consumer Privacy Act + CPRA"
    NY_SHIELD = "NY SHIELD Act"
    DGCL = "Delaware General Corporation Law"
    # Uniform codes
    UCC = "Uniform Commercial Code (CURRENCY: Article 12 Digital Assets · state adoption ongoing)"


class USBarRule(Enum):
    """ABA Model Rules + ethics opinions. PROVENANCE: CITED:10,11,12 bar rule research files"""

    ABA_MR_1_1 = "ABA Model Rule 1.1 — competence"
    ABA_MR_1_6 = "ABA Model Rule 1.6 — confidentiality of information"
    ABA_MR_5_5 = "ABA Model Rule 5.5 — unauthorized practice of law / multijurisdictional practice"
    ABA_MR_7 = "ABA Model Rule 7 — publicity/solicitation (formerly 7.1-7.5, streamlined 2018)"
    ABA_OPINION_512 = "ABA Formal Opinion 512 — AI ethics (CURRENCY: state opinions emerging)"
    ABA_OPINION_483 = "ABA Formal Opinion 483 — lawyers' obligations after data breach"
    ABA_OPINION_477R = "ABA Formal Opinion 477R — securing communication of protected client info"


@dataclass
class Matter:
    """Core case matter dataclass. PROVENANCE: TRAINED"""

    matter_id: str
    matter_type: MatterType
    court: USCourt
    state: Optional[USState] = None
    short_title: str = ""
    parties_plaintiff: list[str] = field(default_factory=list)
    parties_defendant: list[str] = field(default_factory=list)
    statutes_invoked: list[USStatute] = field(default_factory=list)
    filed_date: Optional[str] = None
    next_hearing_date: Optional[str] = None
    next_hearing_location: Optional[str] = None
    status_note: Optional[str] = None


@dataclass
class Citation:
    """Bluebook citation dataclass. PROVENANCE: CITED:13-citation-format-primary.md"""

    raw: str
    format: str = "UNKNOWN"  # SCOTUS | FED_CIRCUIT | FED_DISTRICT | USC | CFR | STATE | UNKNOWN
    volume: Optional[int] = None
    reporter: Optional[str] = None
    page: Optional[int] = None
    year: Optional[int] = None
    court: Optional[str] = None
    title_num: Optional[int] = None
    section: Optional[str] = None
    valid: bool = False
    parse_notes: Optional[str] = None
